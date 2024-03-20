from __future__ import annotations

import typing as _t

import pydantic as _p

from pawdantic import paw_types
from shipr import models as s_mod


class ContactForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: paw_types.truncated_printable_str_type(50)
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    @classmethod
    def with_default(cls, contact: s_mod.Contact):
        class _ContactSelect(cls):
            business_name: paw_types.default_gen(
                paw_types.truncated_printable_str_type(40), default=contact.business_name
            )
            email_address: paw_types.default_gen(
                paw_types.truncated_printable_str_type(50), default=contact.email_address
            )
            mobile_phone: paw_types.default_gen(str, default=contact.mobile_phone)
            contact_name: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(30), default=contact.contact_name
            )

        return _ContactSelect


class AddressForm(_p.BaseModel):
    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'

    @classmethod
    def with_default(cls, address: s_mod.AddressRecipient):
        class _AddressSelect(cls):
            address_line1: _t.Annotated[
                paw_types.truncated_printable_str_type(40), _p.Field(default=address.address_line1)]

            address_line1: paw_types.default_gen(
                paw_types.truncated_printable_str_type(40), default=address.address_line1
            )
            address_line2: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(50), default=address.address_line2
            )
            address_line3: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(60), default=address.address_line3
            )
            town: paw_types.default_gen(
                paw_types.truncated_printable_str_type(30), default=address.town
            )
            postcode: paw_types.default_gen(str, default=address.postcode)
            country: paw_types.default_gen(str, default=address.country)

        return _AddressSelect


class ContactAndAddressForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: paw_types.truncated_printable_str_type(50)
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'

    @classmethod
    def with_default(cls, contact: s_mod.Contact, address: s_mod.AddressRecipient):
        class _ContactAddressSelect(cls):
            business_name: paw_types.default_gen(
                paw_types.truncated_printable_str_type(40), default=contact.business_name
            )
            email_address: paw_types.default_gen(
                paw_types.truncated_printable_str_type(50), default=contact.email_address
            )
            mobile_phone: paw_types.default_gen(str, default=contact.mobile_phone)
            contact_name: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(30), default=contact.contact_name
            )

            address_line1: paw_types.default_gen(
                paw_types.truncated_printable_str_type(40), default=address.address_line1
            )
            address_line2: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(50), default=address.address_line2
            )
            address_line3: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(60), default=address.address_line3
            )
            town: paw_types.default_gen(
                paw_types.truncated_printable_str_type(30), default=address.town
            )
            postcode: paw_types.default_gen(str, default=address.postcode)
            country: paw_types.default_gen(str, default=address.country)

        return _ContactAddressSelect
