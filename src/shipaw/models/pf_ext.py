from __future__ import annotations

import sqlmodel as sqm
from pawdantic import paw_types

from . import pf_shared


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


addr_lines_fields_set = {'address_line1', 'address_line2', 'address_line3'}


class AddressSender(pf_shared.BasePFType):
    address_line1: paw_types.truncated_printable_str_type(24)
    address_line2: paw_types.optional_truncated_printable_str_type(24)
    address_line3: paw_types.optional_truncated_printable_str_type(24)
    # address_line1: str
    # address_line2: str = ""
    # address_line3: str = ""
    town: str
    postcode: str
    country: str = 'GB'

    def to_collection(self):
        return AddressCollection(
            address_line1=self.address_line1,
            address_line2=self.address_line2,
            address_line3=self.address_line3,
            town=self.town,
            postcode=self.postcode,
            country=self.country,
        )

    @property
    def lines_dict(self):
        return {line_field: getattr(self, line_field) for line_field in sorted(self.lines_fields_set)}

    @property
    def lines_list(self):
        return list(self.lines_dict.values())

    @property
    def lines_set_vals(self):
        return {getattr(self, _) for _ in self.lines_fields_set}

    @property
    def lines_fields_set(self):
        return {_ for _ in addr_lines_fields_set if getattr(self, _)}

    @property
    def lines_str(self):
        return '\n'.join(self.lines_dict.values())

    @property
    def lines_str_oneline(self):
        return ', '.join(self.lines_dict.values())

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


AddTypes = AddressCollection | AddressRecipient


class PostOffice(pf_shared.BasePFType):
    post_office_id: str | None = None
    business: str | None = None
    address: AddressRecipient | None = None
    opening_hours: pf_shared.OpeningHours | None = None
    distance: float | None = None
    availability: bool | None = None
    position: pf_shared.Position | None = None
    booking_reference: str | None = None


class AddressChoice(pf_shared.BasePFType):
    address: AddressRecipient = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    score: int


class ConvenientCollect(pf_shared.BasePFType):
    postcode: str | None = None
    post_office: list[PostOffice] | None = None
    count: int | None = None
    post_office_id: str | None = None


class SpecifiedPostOffice(pf_shared.BasePFType):
    postcode: str | None = None
    post_office: list[PostOffice | None]
    count: int | None = None
    post_office_id: str | None = None


class CompletedReturnInfo(pf_shared.BasePFType):
    status: str
    shipment_number: str
    collection_time: pf_shared.DateTimeRange


class InBoundDetails(pf_shared.BasePFType):
    contract_number: str
    service_code: str
    total_shipment_weight: str | None = None
    enhancement: pf_shared.Enhancement | None = None
    reference_number1: str | None = None
    reference_number2: str | None = None
    reference_number3: str | None = None
    reference_number4: str | None = None
    reference_number5: str | None = None
    special_instructions1: str | None = None
    special_instructions2: str | None = None
    special_instructions3: str | None = None
    special_instructions4: str | None = None


class DeliveryOptions(pf_shared.BasePFType):
    convenient_collect: ConvenientCollect | None = None
    irts: bool | None = None
    letterbox: bool | None = None
    specified_post_office: SpecifiedPostOffice | None = None
    specified_neighbour: str | None = None
    safe_place: str | None = None
    pin: int | None = None
    named_recipient: bool | None = None
    address_only: bool | None = None
    nominated_delivery_date: str | None = None
    personal_parcel: str | None = None
