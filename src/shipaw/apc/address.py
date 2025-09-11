from .shared import APCBaseModel


class Contact(APCBaseModel):
    person_name: str
    phone_number: str
    mobile_number: str | None = None
    email: str | None


class AddressRough(APCBaseModel):
    postal_code: str
    country_code: str = 'GB'


class Address(AddressRough):
    company_name: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    county: str
    contact: Contact


class AddressDelivery(Address):
    instructions: str
