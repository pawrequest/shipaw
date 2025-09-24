from typing import TYPE_CHECKING

from shipaw.agnostic.base import ShipawBaseModel

if TYPE_CHECKING:
    ...
from shipaw.agnostic.requests import ShipmentRequestAgnost
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost


class ShipmentConversation(ShipawBaseModel):
    request: 'ShipmentRequestAgnost'
    response: 'ShipmentBookingResponseAgnost'
