import time
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Self, TYPE_CHECKING

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from shipaw.models.base import ShipawBaseModel
from shipaw.models.services2 import enum_as_tups, enum_lookup, enum_reverse_lookup
from shipaw.models.shipment import Shipment

if TYPE_CHECKING:
    from shipaw.fapi.responses import ShipmentBookingResponse
    from shipaw.fapi.requests import ShipmentRequest


class ProviderName(StrEnum):
    PARCELFORCE = 'PARCELFORCE'
    ROYAL_MAIL = 'ROYAL_MAIL'
    APC = 'APC'


class HasServiceCodes(ABC):
    service_codes_type: ClassVar[type[StrEnum]]
    default_service: ClassVar[StrEnum]

    @classmethod
    def lookup_service(cls, service_name: str):
        return enum_lookup(enum_type=cls.service_codes_type, attr_name=service_name)

    @classmethod
    def reverse_lookup_service(cls, service_code: str):
        return enum_reverse_lookup(enum_type=cls.service_codes_type, attr_value=service_code)

    @classmethod
    def services_as_tups(cls) -> list[tuple[str, str]]:
        return enum_as_tups(cls.service_codes_type)


class HasLabels(ABC):
    @staticmethod
    @abstractmethod
    def fetch_label_content(shipment_num: str) -> bytes: ...

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

    async def wait_fetch_label_as(self, shipment_num: str, tries=10) -> bytes:
        for i in range(tries):
            try:
                time.sleep(1)
                label_data = self.fetch_label_content(shipment_num=shipment_num)
                assert label_data is not None
                return label_data
            except AssertionError:
                print(f'Label not ready yet for {shipment_num}, retrying...')
        raise RuntimeError(f'Label not ready after {tries}retries for {shipment_num}')


class ShippingProvider(ShipawBaseModel, HasServiceCodes, HasLabels, ABC):
    name: ClassVar[ProviderName]

    settings: BaseSettings
    settings_type: ClassVar[type[BaseSettings]]

    # services: ClassVar[Services]
    service_codes_type: ClassVar[type[StrEnum]]
    default_service: ClassVar[StrEnum]

    @classmethod
    def from_env_path(cls, env_file: Path) -> Self:
        settings = cls.settings_type(_env_file=env_file)
        return cls(settings=settings)

    @abstractmethod
    def is_sandbox(self) -> bool: ...

    @staticmethod
    @abstractmethod
    def provider_shipment(shipment: Shipment, service_code: StrEnum) -> BaseModel:
        """Takes agnostic Shipment object and returns provider Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def agnostic_shipment(shipment: BaseModel) -> Shipment:
        """Takes provider Shipment object and returns agnostic Shipment object"""
        ...

    @staticmethod
    @abstractmethod
    def book_shipment_agnostic(shipment_request: 'ShipmentRequest') -> 'ShipmentBookingResponse': ...

    # @staticmethod
    # async def booking_response_callback(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
    #     """Do after booking, e.g. log, write label file, etc."""
    #     log_obj(response, 'Shipment Booked')
    #     try:
    #         if response.label_data is None and response.shipment_num:
    #             logger.info('Fetching missing label data...')
    #             response.label_data = request.provider.fetch_label_content(response.shipment_num)
    #         await response.write_label_file()
    #     except Exception as e:
    #         logger.exception(f'Error getting or writing label data: {e}')
