from typing import Annotated, Self

from pydantic import BaseModel, StringConstraints, constr
from websockets import Protocol

from .shared import APCBaseModel
from ..agnostic.address import Address as AddressAgnost, Contact as ContactAgnost
from ..agnostic.ship_types import ConvertMode, pydantic_export

STR_64 = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=64),
]


class Convertable(Protocol):
    def to_generic(self, mode: ConvertMode = 'pydantic') -> BaseModel | dict: ...

    @classmethod
    def from_generic(cls, obj: BaseModel, mode: ConvertMode = 'pydantic') -> Self: ...


class Contact(APCBaseModel):
    person_name: str
    phone_number: str
    mobile_number: str | None = None
    email: str | None

    def to_generic(self, mode: ConvertMode = 'pydantic') -> ContactAgnost | dict:
        obj = ContactAgnost(
            contact_name=self.person_name,
            mobile_phone=self.mobile_number or self.phone_number,
            email_address=self.email,
            business_name='',
        )
        return pydantic_export(obj, mode)

    @classmethod
    def from_generic(cls, contact: ContactAgnost, mode: ConvertMode = 'pydantic') -> Self | dict:
        obj = Contact(
            person_name=contact.contact_name,
            mobile_number=contact.mobile_phone,
            email=contact.email_address,
            phone_number=contact.mobile_phone,
        )
        return pydantic_export(obj, mode)


class Address(APCBaseModel):
    company_name: str = constr(max_length=34)
    # address_line_1: str = constr(max_length=64)
    address_line_1: STR_64
    address_line_2: STR_64 | None = None
    city: str
    county: str | None = None
    postal_code: str
    country_code: str = 'GB'

    contact: Contact

    @classmethod
    def from_generic(cls, address: AddressAgnost, contact: ContactAgnost, mode: ConvertMode = 'pydantic') -> Self | dict:
        obj = Address(
            postal_code=address.postcode,
            address_line_1=address.address_lines[0],
            address_line_2=', '.join(address.address_lines[1:]),
            city=address.town,
            company_name=contact.business_name,
            contact=Contact.from_generic(contact),
        )
        return pydantic_export(obj, mode)

    def to_generic(self, mode: ConvertMode = 'pydantic') -> AddressAgnost | dict:
        obj = AddressAgnost(
            postcode=self.postal_code,
            address_lines=[self.address_line_1] + ([self.address_line_2] if self.address_line_2 else []),
            town=self.city,
            country='GB',
        )
        return pydantic_export(obj, mode)


class AddressDelivery(Address):
    instructions: str


# def apc_address(address: AddressAgnost, contact: ContactAgnost) -> Address:
#     return Address(
#         postal_code=address.postcode,
#         address_line_1=address.address_lines[0],
#         address_line_2=', '.join(address.address_lines[1:]),
#         city=address.town,
#         contact=apc_contact(contact),
#         company_name=contact.business_name,
#     )


def apc_contact(contact: ContactAgnost) -> Contact:
    return Contact(
        person_name=contact.contact_name,
        phone_number=contact.mobile_phone,
        mobile_number=contact.mobile_phone,
        email=contact.email_address,
    )
