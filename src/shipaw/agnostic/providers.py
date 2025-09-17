from dataclasses import dataclass
from typing import Callable

from shipaw.agnostic.services import ServiceDict, Services
from shipaw.agnostic.shipment import Shipment


@dataclass
class ShippingProvider:
    name: str
    service_dict: ServiceDict
    # services: Services
    shipment_dict: Callable[[Shipment], dict]
    # service_codes: ClassVar[dict[ServiceType, str]]
    # build_request: ClassVar[Callable[[dict], BookingResponse]]
    # handle_response: ClassVar[Callable[[BookingResponse], None]]


def convert_shipment(shipment: Shipment, provider: ShippingProvider):
    return provider.shipment_dict(shipment)


def service_code_fetch(shipment: Shipment, provider: ShippingProvider):
    service_code = provider.service_dict.get(shipment.service)
    return service_code
