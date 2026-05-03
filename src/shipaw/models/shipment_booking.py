from typing import TYPE_CHECKING

from shipaw.models.base import ShipawBaseModel

if TYPE_CHECKING:
    ...
from shipaw.models.requests import ShipmentRequest
from shipaw.models.responses import ShipmentResponse


class ShipmentBooking(ShipawBaseModel):
    request: 'ShipmentRequest'
    response: 'ShipmentResponse'
