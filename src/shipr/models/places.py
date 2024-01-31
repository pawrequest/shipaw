from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class PostCode(BaseModel):
    postcode: str


class AddressBasic(BaseModel):
    postcode: PostCode
    name_or_number: str


class Address:
    line1: str
    line2: Optional[str]
    line3: Optional[str]
    county: str
    company_name: Optional[str] = None
    building_name: Optional[str] = None
    country_code: str = 'GB'

    @classmethod
    def from_basic(cls, basic: AddressBasic):
        ...


def parse_address_string(str_address: str):
    str_address = str_address.lower()
    words = str_address.split(" ")
    if 'unit' in ' '.join(words[:2]):
        first_block = ' '.join(words[:2])
    else:
        first_block = words[0].split(",")[0]
    first_char = first_block[0]
    firstline = str_address.split("\n")[0].strip()

    return first_block if first_char.isnumeric() else firstline


@dataclass
class Contact:
    email: str
    telephone: str
    name: str
