import json
import time
from base64 import b64decode
from typing import ClassVar

import httpx
from pydantic import BaseModel
from apc_hypaship.config import APCSettings
from apc_hypaship.models.request.shipment import Shipment as ShipmentAPC

from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.services import Services
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost
from shipaw.providers.apc.response import booking_has_errors, errored_booking
from shipaw.providers.providers import ShippingProvider, register_provider
from shipaw.providers.apc.provider_funcs import (
    APC_SERVICES,
    apc_shipment_from_agnostic,
    apc_shipment_to_agnostic,
)


# @dataclass
@register_provider
class APCShippingProvider(ShippingProvider):
    name = 'APC'
    services: ClassVar[Services] = APC_SERVICES
    settings_type: ClassVar[APCSettings] = APCSettings

    def agnostic_shipment(self, shipment: ShipmentAPC) -> Shipment:
        return apc_shipment_to_agnostic(shipment)

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        return apc_shipment_from_agnostic(shipment)

    def book_shipment(self, shipment: dict | ShipmentAgnost) -> ShipmentBookingResponse:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        shipment_dict = self.build_request_json(shipment)
        res_json = self.get_response_json(shipment_dict)

        if booking_has_errors(shipment_dict):
            return errored_booking(shipment, res_json)

        resp = self.build_response(res_json, shipment)
        resp.label_data = self.wait_label(resp.shipment_num)
        return resp

    @staticmethod
    def build_response(res_json, shipment):

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

    def get_response_json(self, shipment_dict):
        res = httpx.post(self.settings.orders_endpoint, headers=self.settings.headers, json=shipment_dict)
        res.raise_for_status()
        return res.json()

    def build_request_json(self, shipment):
        apc_shipment = self.provider_shipment(shipment)
        shipment_dict = apc_shipment.model_dump(mode='json', by_alias=True)
        return shipment_dict

    def get_label_content(self, shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        settings = self.settings
        label = httpx.get(settings.one_order_endpoint(shipment_num), headers=settings.headers, params=params)
        label.raise_for_status()
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)

