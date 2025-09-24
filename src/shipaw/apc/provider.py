from base64 import b64decode
from typing import ClassVar

import httpx

from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.ship_types import ProviderName, pydantic_export
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.apc.address import Address as AddressAPC, Contact as ContactAPC
from shipaw.apc.services import APCServiceDict
from shipaw.apc.shared import EndPoints, get_headers, order_endpoint
from shipaw.apc.shipment import Shipment


class APCProvider(ShippingProvider):
    name: ClassVar[ProviderName] = 'APC'
    service_dict: ClassVar[ServiceDict] = APCServiceDict
    shipment_type: ClassVar[type[Shipment]] = Shipment
    address_type: ClassVar[type[AddressAPC]] = AddressAPC
    contact_type: ClassVar[type[ContactAPC]] = ContactAPC

    @staticmethod
    def book_shipment(shipment: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        shipment = ShipmentAgnost.model_validate(shipment)
        shipment_apc = Shipment.from_generic(shipment)
        shipment_apc = pydantic_export(shipment_apc, mode='python-alias')

        res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=shipment_apc)
        res.raise_for_status()
        res_json = res.json()
        order = res_json['Orders']['Order']
        order_number = order['OrderNumber']
        return ShipmentBookingResponseAgnost(
            shipment=shipment,
            shipment_num=order_number,
            tracking_link='NOT IMPLEMENTED',
            data=res_json,
            status=str(res.status_code),
            success=res.is_success,
            label_data=APCProvider.get_label_content(order_number),
        )

    @staticmethod
    def get_label_content(shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        label = httpx.get(order_endpoint(shipment_num), headers=get_headers(), params=params)
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)

