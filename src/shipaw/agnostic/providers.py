from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import ClassVar, TYPE_CHECKING

if TYPE_CHECKING:
    from shipaw.agnostic.requests import ShipmentRequestAgnost
    from shipaw.agnostic.responses import ShipmentBookingResponseAgnost

from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.logging import log_booked_shipment
from shipaw.agnostic.ship_types import Convertable, ProviderName
from shipaw.agnostic.shipment import Shipment


@dataclass
class ShippingProvider(ABC):
    name: ClassVar[ProviderName]
    service_dict: ClassVar[ServiceDict]
    shipment_type: ClassVar[type[Convertable]]
    address_type: ClassVar[type[Convertable]]
    contact_type: ClassVar[type[Convertable]]

    # Request/Response
    @staticmethod
    @abstractmethod
    def book_shipment(shipment: dict | Shipment) -> 'ShipmentBookingResponseAgnost':
        raise NotImplementedError

    @staticmethod
    def handle_response(request: 'ShipmentRequestAgnost', response: 'ShipmentBookingResponseAgnost'):
        log_booked_shipment(request, response)

    @staticmethod
    @abstractmethod
    def get_label_content(shipment_num: str) -> bytes:
        raise NotImplementedError


