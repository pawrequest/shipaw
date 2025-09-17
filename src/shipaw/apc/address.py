from typing import Annotated

from pydantic import StringConstraints, constr


from .shared import APCBaseModel
from ..agnostic.address import Address as _Address, Contact as _Contact

STR_64 = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=64),
]


class Contact(APCBaseModel):
    person_name: str
    phone_number: str
    mobile_number: str | None = None
    email: str | None


class Address(APCBaseModel):
    company_name: str = constr(max_length=34)
    address_line_1: str = constr(max_length=64)
    address_line_1: STR_64
    address_line_2: STR_64 | None = None
    city: str
    county: str | None = None
    postal_code: str
    country_code: str = 'GB'

    contact: Contact

    @classmethod
    def from_generic(cls, address:_Address, contact:_Contact):
        return Address(
            postal_code=address.postcode,
            address_line_1=address.address_lines[0],
            address_line_2=', '.join(address.address_lines[1:]),
            city=address.town,
            contact=apc_contact(contact),
            company_name=contact.business_name,
        )


class AddressDelivery(Address):
    instructions: str


def apc_address(address: _Address, contact: _Contact) -> Address:
    return Address(
        postal_code=address.postcode,
        address_line_1=address.address_lines[0],
        address_line_2=', '.join(address.address_lines[1:]),
        city=address.town,
        contact=apc_contact(contact),
        company_name=contact.business_name,
    )


def apc_contact(contact: _Contact) -> Contact:
    return Contact(
        person_name=contact.contact_name,
        phone_number=contact.mobile_phone,
        mobile_number=contact.mobile_phone,
        email=contact.email_address,
    )
