from typing import Callable

from shipaw.models.requests import ShipmentRequest
from shipaw.models.responses import ShipmentResponse

ShipmentCallbackFn = Callable[[ShipmentRequest, ShipmentResponse], None]

CALLBACK_REGISTER: dict[str, ShipmentCallbackFn] = {}


def register_callback(name: str):
    def decorator(func: ShipmentCallbackFn):
        CALLBACK_REGISTER[name] = func
        return func

    return decorator
