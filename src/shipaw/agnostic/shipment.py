import datetime as dt
from pathlib import Path

from shipaw.agnostic.address import FullContact
from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.services import ServiceType
from shipaw.agnostic.ship_types import ShipDirection


class Shipment(ShipawBaseModel):
    recipient: FullContact
    sender: FullContact | None = None  # default to account settings home address if None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection

    reference: str = ''

    service: ServiceType = 'NEXT_DAY'

    @property
    def remote_full_contact(self) -> FullContact:
        match self.direction:
            case ShipDirection.OUTBOUND:
                return self.recipient
            case ShipDirection.INBOUND:
                return self.sender
            case ShipDirection.DROPOFF:
                return self.sender
            case _:
                raise ValueError('Bad ShipDirection')



ShipmentOrDict = Shipment | dict
