from pydantic import constr, field_validator, model_validator

from shipaw.models.base import ShipawBaseModel


class Contact(ShipawBaseModel):
    name: str
    email: str
    mobile_phone: str
    phone_number: str | None = None

    @classmethod
    def empty(cls):
        return cls(name='', email='', mobile_phone='')

    @model_validator(mode='after')
    def phone_is_none(self):
        if not self.phone_number:
            self.phone_number = self.mobile_phone
        return self

    @field_validator('mobile_phone', mode='after')
    def clean_mobile_phone(cls, v):
        return v.replace(' ', '').replace('-', '')


class Address(ShipawBaseModel):
    business_name: str
    address_line1: str
    address_line2: str | None = None
    address_line3: str | None = None
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    county: str | None = None
    country: str = 'GB'

    @classmethod
    def empty(cls):
        return cls(business_name='', address_line1='', town='', postcode='')

    @property
    def address_lines(self) -> list[str]:
        return [line for line in [self.address_line1, self.address_line2, self.address_line3] if line]

    def get_address_lines_dict(self, prefix='address_line') -> dict[str, str]:
        return {f'{prefix}{i + 1}': line for i, line in enumerate(self.address_lines) if line}

    @property
    def search_string(self):
        return ', '.join([self.business_name] + self.address_lines + [self.town, self.postcode])


class FullContact(ShipawBaseModel):
    contact: Contact
    address: Address

    @classmethod
    def empty(cls):
        return cls(contact=Contact.empty(), address=Address.empty())


class AddressChoice(ShipawBaseModel):
    address: Address
    score: int
