from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import ClassVar

from pydantic import BaseModel

from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.ship_log import log_booked_shipment
from shipaw.agnostic.ship_types import ConvertMode, ProviderName
from shipaw.agnostic.shipment import Shipment
from shipaw.agnostic.address import FullContact


@dataclass
class ShippingProvider(ABC):
    name: ClassVar[ProviderName]
    service_dict: ClassVar[ServiceDict]
    shipment_type: ClassVar[type[BaseModel]]

    # Convert to provider-specific objects
    @staticmethod
    @abstractmethod
    def provider_contact(full_contact: FullContact, mode: ConvertMode = 'pydantic') -> dict | BaseModel:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def provider_address(full_contact: FullContact, mode: ConvertMode = 'pydantic') -> dict | BaseModel:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def provider_shipment(shipment: Shipment, mode: ConvertMode = 'pydantic') -> dict | BaseModel:
        raise NotImplementedError

    # Convert to generic
    @staticmethod
    def generic_full_contact(
        contact: BaseModel, address: BaseModel, mode: ConvertMode = 'pydantic'
    ) -> FullContact | dict:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def generic_shipment(shipment: BaseModel, mode: ConvertMode = 'pydantic') -> dict | Shipment:
        raise NotImplementedError

    # Request/Response
    @staticmethod
    @abstractmethod
    def book_shipment(shipment: dict | Shipment) -> 'ShipmentBookingResponseAgnost':
        raise NotImplementedError

    @staticmethod
    def handle_response(request: 'ShipmentRequestAgnost', response: 'ShipmentBookingResponseAgnost'):
        log_booked_shipment(request, response)
        return True

    @staticmethod
    @abstractmethod
    def get_label_content(shipment_num: str) -> bytes:
        raise NotImplementedError


@lru_cache
def service_lookup_agnost(service_dict: dict, service: str):
    reverse_map = {v: k for k, v in service_dict.items()}
    return reverse_map[service]
