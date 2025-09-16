import datetime as dt
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, conlist, constr
from shipaw.ship_types import ShipDirection

from shipaw.parcelforce.pf_shared import ServiceCode


class APCBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )


class ShippingService(APCBaseModel):
    name: str
    code: str


class Contact(APCBaseModel):
    business_name: str
    mobile_phone: str
    email_address: str
    contact_name: str


class Address(APCBaseModel):
    address_lines: list[str] = conlist(item_type=str, max_length=3, min_length=1)
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    country: str = 'GB'


class Shipment(APCBaseModel):
    recipient_contact: Contact
    recipient_address: Address

    sender_contact: Contact | None = None
    sender_address: Address | None = None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection

    reference: str = ''
    references: list[str] = Field(default_factory=list)

    service: ShippingService


class ShippingProvider(Enum):
    PARCELFORCE = 1
    APC = 2
