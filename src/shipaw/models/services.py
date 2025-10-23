from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, cast

from royal_mail_click_and_drop.v2.services import RoyalMailServiceCode


class AgnostServiceName(StrEnum):
    NEXT_DAY = 'NEXT_DAY'
    NEXT_DAY_12 = 'NEXT_DAY_12'
    NEXT_DAY_9 = 'NEXT_DAY_9'
    # SATURDAY = 'SATURDAY'


@dataclass
class Services:
    NEXT_DAY: ClassVar[str]
    NEXT_DAY_12: ClassVar[str]
    NEXT_DAY_9: ClassVar[str]
    SERVICE_CODES: ClassVar[type[StrEnum]]

    @classmethod
    def all_services(cls):
        return [(key, name) for key, name in cls.SERVICE_CODES.__members__.items()]

    def reverse_lookup(self, provider_code: str) -> str:
        for name in self.__class__.__annotations__:
            if getattr(self, name, None) == provider_code:
                return name
        raise ValueError(f'Invalid service code: {provider_code}')

    def lookup(self, agnostic_name: str) -> str:
        res = getattr(self, agnostic_name, None)
        # res1 = self.__dict__.get(agnostic_name)
        if not res:
            raise ValueError(f'Invalid service name: {agnostic_name}')
        return res


class SimpleServices:
    NEXT_DAY: ClassVar[str]
    NEXT_DAY_12: ClassVar[str]
    NEXT_DAY_9: ClassVar[str]
    SERVICE_CODES: ClassVar[type[StrEnum]]
    SERVICE_CODES_FULL: ClassVar[type[StrEnum]]

    @classmethod
    def all_services(cls, full=False) -> list[tuple[str, str]]:
        codes = cls.SERVICE_CODES_FULL if full else cls.SERVICE_CODES
        return [(_.name, cast(str, _.value)) for _ in codes]

    @classmethod
    def reverse_lookup(cls, provider_code: str) -> str:
        res = next(name for name in cls.__dict__.values() if name == provider_code)
        if not res:
            raise ValueError(f'Invalid service code: {provider_code}')
        return res

    @classmethod
    def lookup(cls, agnostic_name: str) -> str:
        res = getattr(cls, agnostic_name, None)
        if not res:
            raise ValueError(f'Invalid service name: {agnostic_name}')
        return res


class RoyalMailSimpleServices(SimpleServices):
    NEXT_DAY: ClassVar[str] = 'TOLP24'  # no signature... use 'TOLP24SF' for signature
    NEXT_DAY_12: ClassVar[str] = 'SD1OLP'  # £750 comp... use 'SD2OLP' for 1,000 or 'SD3OLP' for 2,500
    SERVICE_CODES: ClassVar[type[RoyalMailServiceCode]] = RoyalMailServiceCode
