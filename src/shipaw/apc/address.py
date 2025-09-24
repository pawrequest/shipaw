from typing import Self

from pydantic import constr

from .shared import APCBaseModel
from ..agnostic.address import Address as AddressAgnost, Contact as ContactAgnost
from ..agnostic.ship_types import STR_64


class Contact(APCBaseModel):
    person_name: str
    phone_number: str
    mobile_number: str | None = None
    email: str | None

    def to_generic(self) -> ContactAgnost:
        return ContactAgnost(
            contact_name=self.person_name,
            mobile_phone=self.mobile_number or self.phone_number,
            email_address=self.email,
            phone_number=self.phone_number,
        )

    @classmethod
    def from_generic(cls, contact: ContactAgnost) -> Self:
        return Contact(
            person_name=contact.contact_name,
            mobile_number=contact.mobile_phone,
            email=contact.email_address,
            phone_number=contact.phone_number or contact.mobile_phone,
        )


class Address(APCBaseModel):
    company_name: str = constr(max_length=34)
    address_line_1: STR_64
    address_line_2: STR_64 | None = None
    city: str
    county: str | None = None
    postal_code: str
    country_code: str = 'GB'

    contact: Contact

    @classmethod
    def from_generic(cls, address: AddressAgnost, contact: ContactAgnost) -> Self:
        addr_lines = [line for line in address.address_lines if line]
        return Address(
            postal_code=address.postcode,
            address_line_1=addr_lines[0],
            address_line_2=', '.join(addr_lines[1:]),
            city=address.town,
            company_name=address.business_name,
            contact=Contact.from_generic(contact),
        )

    def to_generic(self) -> AddressAgnost:
        return AddressAgnost(
            postcode=self.postal_code,
            address_lines=[self.address_line_1] + ([self.address_line_2] if self.address_line_2 else []),
            town=self.city,
            country='GB',
            business_name=self.company_name,
        )


class AddressDelivery(Address):
    instructions: str



