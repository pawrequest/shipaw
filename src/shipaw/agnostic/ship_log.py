from loguru import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shipaw.agnostic.requests import ShipmentRequestAgnost
    from shipaw.agnostic.responses import ShipmentBookingResponseAgnost


def log_booked_shipment(request: 'ShipmentRequestAgnost', response: 'ShipmentBookingResponseAgnost'):
    if hasattr(response, 'shipment_num') and response.shipment_num:
        logger.info(
            f'BOOKED {request.shipment.direction.title()} shipment# {response.shipment_num} for {','.join(request.shipment.remote_full_contact.address.address_lines)}'
        )
    else:
        logger.warning('Something Wrong with booking, no shipment number returned?')
