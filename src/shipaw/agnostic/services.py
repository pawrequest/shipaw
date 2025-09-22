from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


@dataclass
class Services:
    NEXT_DAY: str
    NEXT_DAY_12: str
    NEXT_DAY_9: str


ServiceType = Literal['NEXT_DAY', 'NEXT_DAY_12', 'NEXT_DAY_9', 'SATURDAY']


type ServiceDict = dict[ServiceType, str]

#
# class ServiceEnum(ABC, StrEnum):
#     NEXT_DAY = 'NEXT_DAY'
#     NEXT_DAY_12 = 'NEXT_DAY_12'
#     NEXT_DAY_9 = 'NEXT_DAY_9'
#     SATURDAY = 'SATURDAY'

    # @classmethod
    # def reverse_lookup(cls):
    #     return cls.NEXT_DAY

# def str_enum_reverse_lookup(enu, s: str):
#     reverse_map = {e.value: e.name for e in enu}
#     return reverse_map[s]


#

# @dataclass
# class ServiceClass(ABC):
#     NEXT_DAY: str
#     NEXT_DAY_12: str
#     NEXT_DAY_9: str
#
#
# class ServiceClassAPC(ServiceClass):
#     NEXT_DAY = 'N'
#     NEXT_DAY_12 = 'D'
#
#
# #
# #
# #
# #
#
# from typing import TypedDict
#
#
# class ServiceDict2(TypedDict):
#     NEXT_DAY: str
#     NEXT_DAY_12: str
#     NEXT_DAY_9: str
#
#
# APCServiceDict2: ServiceDict2 = {'NEXT_DAY': 'ND16', 'NEXT_DAY_12': 'ND12', 'NEXT_DAY_9': 'ND9'}
#
#
# def from_provider_code(code: str) -> str:
#     reverse_map = {v: k for k, v in APCServiceDict2.items()}
#     return reverse_map[code]
