from base64 import b64decode
from typing import ClassVar, override

import httpx
from apc_hypaship.models.request.address import Address
from pydantic import BaseModel
from apc_hypaship.config import APCSettings
from apc_hypaship.models.request.shipment import GoodsInfo, Order, Orders, Shipment as ShipmentAPC, ShipmentDetails

from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost
from shipaw.providers.apc.response import booking_has_errors, errored_booking
from shipaw.providers.provider_abc import ShippingProvider
from shipaw.providers.apc.provider_funcs import (
    APC_SERVICES,
    address_from_agnostic_fc,
    full_contact_from_apc_contact_address,
)


# @dataclass
# @register_provider
class APCShippingProvider(ShippingProvider):
    name = 'APC'
    services: ClassVar[Services] = APC_SERVICES
    settings_type: ClassVar[APCSettings] = APCSettings
    settings: APCSettings

    @override
    def is_sandbox(self) -> bool:
        return 'training' in self.settings.base_url.lower()

    @override
    def agnostic_shipment(self, shipment: ShipmentAPC) -> ShipmentAgnost:
        order = shipment.orders.order
        del_fc = full_contact_from_apc_contact_address(order.delivery.contact, order.delivery)
        send_fc = (
            full_contact_from_apc_contact_address(order.collection.contact, order.collection)
            if order.collection
            else None
        )
        service = APC_SERVICES.reverse_lookup(order.product_code)
        return ShipmentAgnost(
            service=service,
            shipping_date=order.collection_date,
            reference=order.reference,
            recipient=del_fc,
            sender=send_fc,
            boxes=order.shipment_details.number_of_pieces,
            direction=ShipDirection.INBOUND if order.collection is not None else ShipDirection.OUTBOUND,
            collect_ready=order.ready_at,
            collect_closed=order.closed_at,
        )

    @override
    def provider_shipment(self, shipment: ShipmentAgnost) -> BaseModel:
        # todo handle direction
        if shipment.direction not in [ShipDirection.INBOUND, ShipDirection.OUTBOUND]:
            raise NotImplementedError('APCShippingProvider does not support DROPOFF shipments')
        service_code = APC_SERVICES.lookup(shipment.service)
        ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)
        order = Order(
            ready_at=shipment.collect_ready,
            closed_at=shipment.collect_closed,
            collection_date=shipment.shipping_date,
            product_code=service_code,
            reference=shipment.reference,
            delivery=address_from_agnostic_fc(Address, shipment.recipient),
            collection=address_from_agnostic_fc(Address, shipment.sender) if shipment.sender else None,
            goods_info=GoodsInfo(),
            shipment_details=ship_deets,
        )
        return ShipmentAPC(orders=Orders(order=order))

    @override
    def book_shipment(self, shipment: dict | ShipmentAgnost) -> ShipmentBookingResponse:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        request_json = self.build_request_json(shipment)
        response_json = self.fetch_order_response_json(request_json)

        if booking_has_errors(request_json):
            return errored_booking(shipment, response_json)

        resp = self.build_response(response_json, shipment)
        resp.label_data = self.wait_fetch_label(resp.shipment_num)
        return resp

    @override
    def fetch_label_content(self, shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        settings = self.settings
        label = httpx.get(settings.one_order_endpoint(shipment_num), headers=settings.headers, params=params)
        label.raise_for_status()
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)

    @staticmethod
    def build_response(res_json: dict, shipment: ShipmentAgnost):
        orders = res_json['Orders']
        order = orders['Order']
        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=(order['OrderNumber']),
            tracking_link='NOT IMPLEMENTED',
            data=res_json,
            status=(str(orders.get('Messages').get('Code'))),
            success=(orders.get('Messages').get('Code') == 'SUCCESS'),
        )

    def fetch_order_response_json(self, shipment_dict: dict):
        res = httpx.post(self.settings.orders_endpoint, headers=self.settings.headers, json=shipment_dict)
        res.raise_for_status()
        return res.json()

    def build_request_json(self, shipment):
        apc_shipment = self.provider_shipment(shipment)
        return apc_shipment.model_dump(mode='json', by_alias=True)

