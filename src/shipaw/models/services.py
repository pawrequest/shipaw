from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar


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

    def reverse_lookup(self, provider_code: str) -> str:
        for name in self.__class__.__annotations__:
            if getattr(self, name, None) == provider_code:
                return name
        raise ValueError(f'Invalid service code: {provider_code}')
    #
    # def reverse_lookup(self, provider_code: str) -> str:
    #     res = next((name for name, code in self.__dict__.items() if code == provider_code), None)
    #     if not res:
    #         raise ValueError(f'Invalid service code: {provider_code}')
    #     return res

    def lookup(self, agnostic_name: str) -> str:
        res = getattr(self, agnostic_name)
        # res1 = self.__dict__.get(agnostic_name)
        if not res:
            raise ValueError(f'Invalid service name: {agnostic_name}')
        return res
