import datetime as dt
from typing import Protocol

from shipaw.models.address_contact import FullContact
from shipaw.utils.consts_enums import ShipDirection


class ShipmentProtocol(Protocol):
    recipient: FullContact
    sender: FullContact | None
    boxes: int
    shipping_date: dt.date
    direction: ShipDirection
    reference: str

    @property
    def remote_full_contact(self) -> FullContact:
        match self.direction:
            case ShipDirection.OUTBOUND:
                return self.recipient
            case ShipDirection.INBOUND | ShipDirection.DROPOFF:
                return self.sender
            case _:
                raise ValueError('Bad ShipDirection')
