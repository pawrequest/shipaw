from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Self, TYPE_CHECKING

from pydantic import BaseModel

from shipaw.models.logging import log_booked_shipment
from shipaw.models.services import Services
from shipaw.models.shipment import Shipment

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse


class ConvertableShipment(ABC, BaseModel):
    @classmethod
    @abstractmethod
    def from_agnostic(cls, shipment: Shipment) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_agnostic(self) -> Shipment:
        raise NotImplementedError


# class ProviderShipment(ConvertableShipment, ABC):
#     agnostic_shipment: Shipment
#     provider_shipment: ConvertableShipment


ProviderShipmentFn = Callable[[Shipment], BaseModel]
AgnosticShipmentFn = Callable[[BaseModel], Shipment]
BookingFn = Callable[[dict | Shipment], 'ShipmentBookingResponseAgnost']


class ShipProv:
    name: str
    services: Services
    provider_shipment: ProviderShipmentFn
    agnostic_shipment: AgnosticShipmentFn
    book_shipment: BookingFn
    get_label_content: Callable[[str], bytes]

    def __init__(
        self,
        name: str,
        services: Services,
        provider_shipment: ProviderShipmentFn,
        agnostic_shipment: AgnosticShipmentFn,
        book_shipment: BookingFn,
        get_label_content: Callable[[str], bytes],
    ) -> None:
        self.name = name
        self.services = services
        self.provider_shipment = provider_shipment
        self.agnostic_shipment = agnostic_shipment
        self.book_shipment = book_shipment
        self.get_label_content = get_label_content


# @dataclass
class ShippingProvider(ABC):
    name: ClassVar[str]
    # service_map: ClassVar[MappingProxyType]
    services: Services

    @staticmethod
    @abstractmethod
    def provider_shipment(shipment: Shipment) -> BaseModel:
        """Takes agnostic Shipment object and returns provider Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def agnostic_shipment(shipment: BaseModel) -> Shipment:
        """Takes provider Shipment object and returns agnostic Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def book_shipment(shipment: dict | Shipment) -> 'ShipmentBookingResponse': ...

    @staticmethod
    @abstractmethod
    def get_label_content(shipment_num: str) -> bytes: ...

    @staticmethod
    def handle_response(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
        log_booked_shipment(request, response)

    def get_shipment_alias_dict(self, shipment: Shipment | dict) -> dict:
        shipment = shipment.model_validate(shipment)
        shipment = self.provider_shipment(shipment)
        shipment_alias = shipment.model_dump(mode='json', by_alias=True)
        return shipment_alias


PROVIDER_REGISTER: dict[str, type[ShippingProvider]] = {}


def register_provider(cls: type[ShippingProvider]) -> type[ShippingProvider]:
    PROVIDER_REGISTER[str(cls.name)] = cls
    return cls
