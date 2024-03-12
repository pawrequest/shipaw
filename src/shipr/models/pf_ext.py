# from __future__ import annotations

import sqlmodel as sqm

from . import types, pf_shared


# if _ty.TYPE_CHECKING:
#     pass


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


addr_lines_set = sorted({'address_line1', 'address_line2', 'address_line3'})


class BaseAddress(pf_shared.BasePFType):
    address_line1: types.TruncatedSafeStr(24)
    address_line2: types.TruncatedSafeMaybeStr(24)
    address_line3: types.TruncatedSafeMaybeStr(24)
    # address_line1: str
    # address_line2: str = ""
    # address_line3: str = ""
    town: str
    postcode: str
    country: str = 'GB'

    @property
    def lines_dict(self):
        return {_: getattr(self, _) for _ in addr_lines_set}

    @property
    def lines_list(self):
        return list(self.lines_dict.values())

    @property
    def lines_set(self):
        return {getattr(self, _) for _ in addr_lines_set}

    @property
    def lines_str(self):
        return '\n'.join(self.lines_dict.values())

    # def address_lines_dict(self):
    #     return {
    #         "address_line1": self.address_line1,
    #         "address_line2": self.address_line2,
    #         "address_line3": self.address_line3,
    #     }


class AddressSender(BaseAddress):
    ...


class AddressRecipient(BaseAddress):
    address_line1: types.TruncatedSafeStr(40)
    address_line2: types.TruncatedSafeMaybeStr(50)
    address_line3: types.TruncatedSafeMaybeStr(60)
    town: types.TruncatedSafeStr(30)


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
    post_office: list[PostOffice | None]
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
