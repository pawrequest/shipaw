from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self, TYPE_CHECKING

from agnostic.logging import log_booked_shipment
from agnostic.services import ServiceDict
from agnostic.shipment import Shipment

if TYPE_CHECKING:
    from shipaw.agnostic.requests import ShipmentRequestAgnost
    from shipaw.agnostic.responses import ShipmentBookingResponseAgnost


class ConvertableShipment(ABC):
    @classmethod
    @abstractmethod
    def from_agnostic(cls, shipment: Shipment) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_agnostic(self) -> Shipment:
        raise NotImplementedError


# ProviderShipmentType = TypeVar('ProviderShipmentType', bound=ConvertableShipment)
# ProviderShipmentType = ConvertableShipment


def provider_shipment(ship_type: type[ConvertableShipment], shipment: Shipment) -> ConvertableShipment:
    return ship_type.from_agnostic(shipment)


@dataclass
class ProviderInterface(ABC):
    name: str
    service_dict: ServiceDict
    shipment_type: type[ConvertableShipment]

    @staticmethod
    @abstractmethod
    def book_shipment(shipment: dict | Shipment) -> ShipmentBookingResponseAgnost: ...

    @staticmethod
    def handle_response(request: 'ShipmentRequestAgnost', response: 'ShipmentBookingResponseAgnost'):
        log_booked_shipment(request, response)

    @staticmethod
    @abstractmethod
    def get_label_content(shipment_num: str) -> bytes: ...


PROVIDER_REGISTER: dict[str, type[ProviderInterface]] = {}


def register_provider(cls: type[ProviderInterface]) -> type[ProviderInterface]:
    PROVIDER_REGISTER[cls.name] = cls
    return cls
