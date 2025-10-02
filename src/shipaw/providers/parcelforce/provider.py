from __future__ import annotations

from pydantic import BaseModel

from shipaw.models.provider import ShippingProvider, register_provider
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost

#
from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.shipment import Shipment as ShipmentPF
from shipaw.providers.parcelforce.provider_funcs import (
    book_shipment,
    parcelforce_shipment_from_agnostic,
    parcelforce_shipment_to_agnostic,
)


# @dataclass
@register_provider
class ParcelforceShippingProvider(ShippingProvider):
    name = 'PARCELFORCE'

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        return parcelforce_shipment_from_agnostic(shipment)

    def agnostic_shipment(self, shipment: ShipmentPF) -> Shipment:
        return parcelforce_shipment_to_agnostic(shipment)

    def book_shipment(self, shipment: dict | ShipmentAgnost) -> ShipmentBookingResponse:
        return book_shipment(shipment)

    def get_label_content(self, shipment_num: str) -> bytes:
        el_client = ParcelforceClient()
        return el_client.get_label_content(shipment_num)

