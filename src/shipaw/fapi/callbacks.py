from typing import Any, TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.models.responses import ShipmentResponse

CALLBACK_REGISTER: dict[str, Callable[['ShipmentRequest', 'ShipmentResponse'], Any]] = {}
