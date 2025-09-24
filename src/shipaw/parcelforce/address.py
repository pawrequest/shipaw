from typing import Self

import pydantic
from pawdantic import paw_types
from pydantic import constr

from shipaw.agnostic.address import Address as AddressAgnost, Contact as ContactAgnost
from shipaw.agnostic.ship_types import MyPhone
from shipaw.parcelforce.notifications import CollectionNotifications, RecipientNotifications
from shipaw.parcelforce.shared import PFBaseModel


class Contact(PFBaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: paw_types.truncated_printable_str_type(30)
    notifications: RecipientNotifications | None = RecipientNotifications.standard_recip()

    def to_generic(self) -> ContactAgnost:
        return ContactAgnost(
            contact_name=self.contact_name,
            email_address=self.email_address,
            mobile_phone=self.mobile_phone,
        )

    @classmethod
    def from_generic(cls, contact: ContactAgnost, business_name: str) -> Self:
        return cls(
            business_name=business_name,
            contact_name=contact.contact_name,
            email_address=contact.email_address,
            mobile_phone=contact.mobile_phone,
        )

    @property
    def notifications_str(self) -> str:
        msg = f'Recip Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg


class ContactCollection(Contact):
    senders_name: paw_types.optional_truncated_printable_str_type(25)
    # senders_name: constr(max_length=25) | None = None
    telephone: MyPhone | None = None
    notifications: CollectionNotifications | None = CollectionNotifications.standard_coll()

    @property
    def notifications_str(self) -> str:
        msg = f'Collecton Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @pydantic.model_validator(mode='after')
    def tel_is_none(self):
        if not self.telephone:
            self.telephone = self.mobile_phone
        return self

    # @classmethod
    # def from_contact(cls, contact: Contact):
    #     return cls(
    #         **contact.model_dump(exclude={'notifications'}),
    #         senders_name=contact.contact_name,


class ContactSender(Contact):
    business_name: paw_types.optional_truncated_printable_str_type(25)
    # business_name: constr(max_length=25)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: paw_types.optional_truncated_printable_str_type(25)

    telephone: MyPhone | None = None
    senders_name: paw_types.optional_truncated_printable_str_type(25) | None = None
    notifications: None = None


class ContactTemporary(Contact):
    business_name: str = ''
    contact_name: str = ''
    mobile_phone: MyPhone | None = None
    email_address: str = ''
    telephone: MyPhone | None = None
    senders_name: str = ''

    @pydantic.model_validator(mode='after')
    def fake(self):
        for field, value in self.model_dump().items():
            if not value:
                value = '========='
                if field == 'email_address':
                    value = f'{value}@f======f.com'
                setattr(self, field, value)
        return self


def address_string_to_dict(address_str: str) -> dict[str, str]:
    addr_lines = address_str.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {
        'address_line1': addr_lines[0],
        'address_line2': addr_lines[1],
        'address_line3': addr_lines[2],
    }


class AddressBase(PFBaseModel):
    address_line1: paw_types.truncated_printable_str_type(24)
    address_line2: paw_types.optional_truncated_printable_str_type(24)
    address_line3: paw_types.optional_truncated_printable_str_type(24)
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    country: str = 'GB'

    def to_generic(self, business_name) -> AddressAgnost:
        return AddressAgnost(
            address_lines=[line for line in [self.address_line1, self.address_line2, self.address_line3] if line],
            town=self.town,
            postcode=self.postcode,
            country=self.country,
            business_name=business_name,
        )

    @classmethod
    def from_generic(cls, address: AddressAgnost) -> Self:
        return cls(
            address_line1=address.address_lines[0],
            address_line2=address.address_lines[1] if len(address.address_lines) > 1 else None,
            address_line3=address.address_lines[2] if len(address.address_lines) > 2 else None,
            town=address.town,
            postcode=address.postcode,
            country=address.country,
        )

    @property
    def lines_dict(self):
        return {line_field: getattr(self, line_field) for line_field in sorted(self.lines_fields_set)}

    @property
    def lines_fields_set(self):
        return {_ for _ in addr_lines_fields_set if getattr(self, _)}

    @property
    def lines_str(self):
        return '\n'.join(self.lines_dict.values())

    @property
    def lines_str_oneline(self):
        return ', '.join(self.lines_dict.values())


class AddressSender(AddressBase):
    ...

    # def address_lines_dict(self):
    #     return {
    #         "address_line1": self.address_line1,
    #         "address_line2": self.address_line2,
    #         "address_line3": self.address_line3,
    #     }


class AddressCollection(AddressSender):
    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(40)
    address_line3: paw_types.optional_truncated_printable_str_type(40)
    town: paw_types.truncated_printable_str_type(30)


class AddressRecipient(AddressCollection):
    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)


class AddressTemporary(AddressRecipient):
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    town: str | None = None
    postcode: str | None = None


class AddressChoice[T: AddressCollection | AddressRecipient](PFBaseModel):
    address: T
    # address: T = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    score: int


addr_lines_fields_set = {'address_line1', 'address_line2', 'address_line3'}
AddTypes = AddressRecipient | AddressCollection
