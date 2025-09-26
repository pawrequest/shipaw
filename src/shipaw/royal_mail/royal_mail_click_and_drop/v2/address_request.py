from __future__ import annotations

import re  # noqa: F401

from royal_mail_click_and_drop.models.base import RMBaseModel

from shipaw.agnostic.address import Address as AddressAgnost
from shipaw.agnostic.ship_types import str_type


class AddressRequest(RMBaseModel):
    full_name: str_type(210) = None
    company_name: str_type(100) | None = None
    address_line1: str_type(100)
    address_line2: str_type(100) | None = None
    address_line3: str_type(100) | None = None
    city: str_type(100)
    county: str_type(100) | None = None
    postcode: str_type(20) | None = None
    country_code: str_type(3) = 'GB'

    @classmethod
    def from_generic(cls, addr: AddressAgnost) -> AddressRequest:
        return cls(
            # full_name=addr.full_name,
            company_name=addr.business_name,
            **addr.get_address_lines_dict('address_line'),
            city=addr.town,
            county=addr.town,
            postcode=addr.postcode,
            country_code=addr.country,
        )

    def to_generic(self) -> AddressAgnost:
        return AddressAgnost(
            business_name=self.company_name,
            address_lines=[_ for _ in [self.address_line1, self.address_line2, self.address_line3] if _],
            town=self.city,
            postcode=self.postcode,
            country=self.country_code or 'GB',
        )
