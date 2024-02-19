from __future__ import annotations

from typing import Optional

from pydantic import Field

from shipr.models.express.shared import BasePFType


class Contact(BasePFType):
    business_name: str = Field(...)
    email_address: str = Field(None)
    mobile_phone: str = Field(None)

    contact_name: Optional[str] = Field(None)
    telephone: Optional[str] = Field(None)
    fax: Optional[str] = Field(None)

    senders_name: Optional[str] = Field(None)
    # notifications: Optional[Notifications] = Field(None)


class Address(BasePFType):
    address_line1: str = Field(...)
    town: str = Field(None)
    postcode: str = Field(None)

    address_line2: Optional[str] = Field(None)
    address_line3: Optional[str] = Field(None)
    country: str = Field('GB')
