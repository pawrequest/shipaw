from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentResponse

CALLBACK_REGISTER: dict[str, Callable[['ShipmentRequest', 'ShipmentResponse'], Any]] = {}
