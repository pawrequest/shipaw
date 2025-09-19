from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Literal

from pydantic import BaseModel

from shipaw.agnostic.address import Address, Contact
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.services import ServiceDict, Services
from shipaw.agnostic.shipment import FullContact, Shipment

ConvertMode = Literal['dict', 'pydantic']

# @dataclass
# class ShippingProvider:
#     name: str
#     service_dict: ServiceDict
#     shipment_dict: Callable[[Shipment], dict]
#     send_request: Callable[[dict], ShipmentBookingResponseAgnost]
#     # handle_response: ClassVar[Callable[[BookingResponse], None]]
#


# class ShippingProvider(ABC):
#     service_dict: ServiceDict
#
#     @abstractmethod
#     def make_shipment_dict(self, shipment: Shipment) -> dict:
#         raise NotImplementedError
#
#     @abstractmethod
#     def send_request(self, ship_dict: dict | Shipment) -> ShipmentBookingResponseAgnost:
#         raise NotImplementedError
#
#     @abstractmethod
#     def handle_response(self, response: ShipmentBookingResponseAgnost) -> bool:
#         raise NotImplementedError


class ShippingProvider(ABC):
    service_dict: ServiceDict

    @staticmethod
    @abstractmethod
    def convert_contact(full_contact: FullContact, mode: ConvertMode = 'dict') -> dict | BaseModel:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def convert_address(full_contact: FullContact, mode: ConvertMode = 'dict') -> dict | BaseModel:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def convert_shipment(shipment: Shipment, mode: ConvertMode = 'dict') -> dict | BaseModel:
        raise NotImplementedError

    @abstractmethod
    def send_request(self, ship_dict: dict | Shipment) -> ShipmentBookingResponseAgnost:
        raise NotImplementedError

    @abstractmethod
    def handle_response(self, response: ShipmentBookingResponseAgnost) -> bool:
        raise NotImplementedError


def maybe_dict(obj: BaseModel, mode: ConvertMode) -> dict | object:
    if mode == 'pydantic':
        return obj
    elif mode == 'dict':
        return obj.model_dump(mode='json')
    else:
        raise ValueError(f'Invalid mode: {mode}')
