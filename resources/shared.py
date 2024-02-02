from dataclasses import dataclass
from typing import Protocol


class AddressRough(Protocol):
    postcode: str
    country_code: str


@dataclass
class AddressRoughDC:
    postcode: str
    country_code: str


class MessagesProtocol(Protocol):
    Code: str
    Description: str
