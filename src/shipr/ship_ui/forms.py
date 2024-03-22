from __future__ import annotations

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


class ContactAndAddressForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: str
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'
