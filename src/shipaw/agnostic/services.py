from dataclasses import dataclass
from typing import Literal


@dataclass
class Services:
    NEXT_DAY: str
    NEXT_DAY_12: str
    NEXT_DAY_9: str


ServiceType = Literal['NEXT_DAY', 'NEXT_DAY_12', 'NEXT_DAY_9', 'SATURDAY']


type ServiceDict = dict[ServiceType, str]
