import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, ClassVar, Self, TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shipaw.models.base import ShipawBaseModel

# from shipaw.fapi.backend import try_get_write_label
from shipaw.models.logging import log_obj
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

#
# class ShipProv:
#     name: str
#     services: Services
#     provider_shipment: ProviderShipmentFn
#     agnostic_shipment: AgnosticShipmentFn
#     book_shipment: BookingFn
#     get_label_content: Callable[[str], bytes]
#
#     def __init__(
#         self,
#         name: str,
#         services: Services,
#         provider_shipment: ProviderShipmentFn,
#         agnostic_shipment: AgnosticShipmentFn,
#         book_shipment: BookingFn,
#         get_label_content: Callable[[str], bytes],
#     ) -> None:
#         self.name = name
#         self.services = services
#         self.provider_shipment = provider_shipment
#         self.agnostic_shipment = agnostic_shipment
#         self.book_shipment = book_shipment
#         self.get_label_content = get_label_content


# @dataclass
class ShippingProvider(ABC, ShipawBaseModel):
    name: ClassVar[str]
    # service_map: ClassVar[MappingProxyType]
    services: ClassVar[Services]
    settings_type: ClassVar[type[BaseSettings]]
    settings: BaseSettings | None = None

    def wait_label(self, shipment_num: str) -> bytes:
        for i in range(10):
            try:
                time.sleep(1)
                label_data = self.get_label_content(shipment_num=shipment_num)
                assert label_data is not None
                return label_data
            except AssertionError as e:
                print(f'Label not ready yet for {shipment_num}, retrying...')
        raise RuntimeError(f'Label not ready after retries for {shipment_num}')

    @classmethod
    def from_env(cls, env_file: Path) -> Self:
        settings = cls.settings_type(_env_file=env_file)
        return cls(settings=settings)

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
    async def handle_response_async(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
        log_obj(response, 'Shipment Booked')
        try:
            if response.label_data is None and response.shipment_num:
                response.label_data = request.provider.get_label_content(response.shipment_num)
            await response.write_label_file()
        except Exception as e:
            logger.exception(f'Error getting or writing label data: {e}')


PROVIDER_REGISTER: dict[str, type[ShippingProvider]] = {}


def register_provider(cls: type[ShippingProvider]) -> type[ShippingProvider]:
    if not issubclass(cls, ShippingProvider):
        raise TypeError('Can only register subclasses of ShippingProvider')
    PROVIDER_REGISTER[str(cls.name)] = cls
    return cls
