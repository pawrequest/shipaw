from pydantic import conlist, constr, field_validator

from shipaw.agnostic.base import ShipawBaseModel


class Contact(ShipawBaseModel):
    business_name: str
    mobile_phone: str
    email_address: str
    contact_name: str


class Address(ShipawBaseModel):
    address_lines: list[str] = conlist(item_type=str, max_length=3, min_length=1)
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    country: str = 'GB'

    @field_validator('address_lines', mode='after')
    def check_address_lines(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one address line is required')
        if len(v) > 3:
            v[2] = ', '.join(v[2:])
        if len(v) < 3:
            v += [''] * (3 - len(v))
        return v[:3]
