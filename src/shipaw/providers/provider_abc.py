import time
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import ClassVar, TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from shipaw.models.base import ShipawBaseModel
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment

if TYPE_CHECKING:
    from shipaw.fapi.responses import ShipmentResponse
    from shipaw.fapi.requests import ShipmentRequest


class ProviderName(StrEnum):
    # PARCELFORCE = 'PARCELFORCE'
    ROYAL_MAIL = 'ROYAL_MAIL'
    APC = 'APC'


class HasServiceCodes(ABC):
    service_codes_type: ClassVar[type[StrEnum]]
    default_service: ClassVar[StrEnum]

    @classmethod
    def lookup_service(cls, service_name: str):
        return cls.service_codes_type[service_name]

    @classmethod
    def reverse_lookup_service(cls, service_code: str):
        return cls.service_codes_type(service_code).name

    @classmethod
    def services_as_tups(cls) -> list[tuple[str, str]]:
        return [(e.name, str(e.value)) for e in cls.service_codes_type]

    @classmethod
    def services_as_dict(cls) -> dict[str, str]:
        return dict(cls.service_codes_type.__members__.items())


class HasLabels(ABC):
    @abstractmethod
    def fetch_label_content(self, shipment_num: str) -> bytes: ...

    def wait_fetch_label(self, shipment_num: str, tries=10) -> bytes:
        for i in range(tries):
            try:
                time.sleep(1)  # let API process booking
                label_data = self.fetch_label_content(shipment_num=shipment_num)
                assert label_data is not None, f'Label not ready yet for {shipment_num}, retrying...'
                return label_data
            except AssertionError:
                pass
        raise RuntimeError(f'Label not ready after {tries} retries for {shipment_num}')

    async def wait_fetch_label_async(self, shipment_num: str, tries=10) -> bytes:
        for i in range(tries):
            try:
                time.sleep(1)
                label_data = self.fetch_label_content(shipment_num=shipment_num)
                assert label_data is not None
                return label_data
            except AssertionError:
                print(f'Label not ready yet for {shipment_num}, retrying...')
        raise RuntimeError(f'Label not ready after {tries}retries for {shipment_num}')


class ShippingProvider(HasServiceCodes, HasLabels, ABC, ShipawBaseModel):
    name: ClassVar[ProviderName]
    settings: BaseSettings
    settings_type: ClassVar[type[BaseSettings]]
    valid_directions: ClassVar[list[ShipDirection]]

    valid_direction_services: ClassVar[dict[ShipDirection, set[StrEnum]]] = Field(default_factory=dict)

    @property
    @abstractmethod
    def client(self):
        raise NotImplementedError

    @abstractmethod
    def is_sandbox(self) -> bool: ...

    @staticmethod
    @abstractmethod
    def provider_shipment(shipment: Shipment, service_code: StrEnum) -> BaseModel:
        """Takes Shipaw's agnostic Shipment object and returns provider-specific Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def agnostic_shipment(shipment: BaseModel) -> Shipment:
        """Takes provider-specific Shipment object and returns Shipaw's agnostic Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def book_shipment_agnostic(shipment_request: 'ShipmentRequest') -> 'ShipmentResponse': ...
