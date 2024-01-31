from enum import Enum, StrEnum, auto


class ShipDirection(StrEnum):
    IN = auto()
    OUT = auto()


class DateTimeMasks(Enum):
    DISPLAY = '%A - %B %#d'
    HIRE = '%d/%m/%Y'
    DB = '%Y-%m-%d'
    BUTTON = '%A \n%B %#d'
    FILE = '%Y-%m-%d_%H-%M-%S'
    COMMENCE = '%Y%m%d'


class ApiScope(StrEnum):
    SANDBOX = auto()
    PRODUCTION = auto()
