import datetime as dt

from pydantic import Field

from shipaw.agnostic.address import Address, Contact
from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.services import ServiceType
from shipaw.agnostic.ship_types import ShipDirection


class FullContact(ShipawBaseModel):
    contact: Contact
    address: Address


class Shipment(ShipawBaseModel):
    recipient_contact: Contact
    recipient_address: Address

    sender_contact: Contact | None = None
    sender_address: Address | None = None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection

    reference: str = ''
    references: list[str] = Field(default_factory=list)

    service: ServiceType


class Shipment2(ShipawBaseModel):
    recipient: FullContact
    sender: FullContact | None = None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection

    reference: str = ''
    references: list[str] = Field(default_factory=list)

    service: ServiceType


ShipmentOrDict = Shipment | dict
