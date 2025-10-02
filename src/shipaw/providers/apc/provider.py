import json
from base64 import b64decode

import httpx
from pydantic import BaseModel

from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost
from apc_hypaship.config import apc_settings
from apc_hypaship.models.request.shipment import Shipment as ShipmentAPC
from shipaw.models.provider import ShippingProvider, register_provider
from shipaw.providers.apc.provider_funcs import APC_SERVICES, \
    apc_shipment_from_agnostic, \
    apc_shipment_to_agnostic, \
    shipment_booking_errored


# @dataclass
@register_provider
class APCShippingProvider(ShippingProvider):
    name = 'APC'
    services = APC_SERVICES

    def agnostic_shipment(self, shipment: ShipmentAPC) -> Shipment:
        return apc_shipment_to_agnostic(shipment)

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        return apc_shipment_from_agnostic(shipment)

    def book_shipment(self, shipment: dict | ShipmentAgnost, settings=apc_settings()) -> ShipmentBookingResponse:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        apc_shipment = self.provider_shipment(shipment)
        shipment_dict = apc_shipment.model_dump(mode='json', by_alias=True)

        res = httpx.post(settings.orders_endpoint, headers=settings.headers, json=shipment_dict)
        res.raise_for_status()
        res_json = res.json()
        messages = json.loads(res.text).get('Orders').get('Order').get('Messages')
        if 'ErrorFields' in messages.keys():
            return shipment_booking_errored(messages, res, res_json, shipment)
        order = res_json['Orders']['Order']
        order_number = order['OrderNumber']

        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=order_number,
            tracking_link='NOT IMPLEMENTED',
            data=res_json,
            status=str(res.status_code),
            success=res.is_success,
            label_data=self.get_label_content(order_number),
        )

    def get_label_content(self, shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        settings = apc_settings()
        label = httpx.get(settings.one_order_endpoint(shipment_num), headers=settings.headers, params=params)
        label.raise_for_status()
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)

