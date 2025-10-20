from typing import Any, TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse

CALLBACK_REGISTER: dict[str, Callable[['ShipmentRequest', 'ShipmentBookingResponse'], Any]] = {}