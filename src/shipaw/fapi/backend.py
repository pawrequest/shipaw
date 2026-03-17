from apc_hypaship.error import apc_http_status_alerts
from httpx import HTTPStatusError
from loguru import logger

from shipaw.fapi.alerts import Alert, AlertType, Alerts
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.ship_types import ShipDirection

# from shipaw.providers.parcelforce.parcelforce_funcs import parcelforce_full_contact
from shipaw.providers.provider_abc import ProviderName


# from parcelforce_expresslink.models.address import AddressChoice as AddressChoicePF
# from parcelforce_expresslink.models.contact import Contact as ContactPF


async def try_book_shipment(shipment_request: ShipmentRequest) -> ShipmentResponse:
    shipment_response = ShipmentResponse(shipment=shipment_request.shipment)
    try:
        shipment_response = shipment_request.provider.book_shipment_agnostic(shipment_request)

    except HTTPStatusError as e:
        await maybe_apc_response_error(e, shipment_request, shipment_response)

    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        shipment_response.alerts += Alert.from_exception(e)

    return shipment_response


async def try_get_write_label(request: ShipmentRequest, response: ShipmentResponse):
    if not response.label_data:
        await try_get_label_data(request, response)
    await try_write_label(response)


async def try_get_label_data(request: ShipmentRequest, response: ShipmentResponse) -> None:
    try:
        if response.label_data is not None:
            logger.info('Label data already present, not fetching')
        else:
            if response.shipment_num:
                response.label_data = await request.provider.wait_fetch_label_async(response.shipment_num)
            else:
                logger.warning('No shipment number to fetch label data')

    except HTTPStatusError as e:
        await maybe_apc_response_error(e, request, response)

    except Exception as e:
        logger.exception('Error getting label data')
        response.alerts += Alert.from_exception(e)


async def try_write_label(response: ShipmentResponse):
    try:
        await response.write_label_file()
    except Exception as e:
        logger.exception(f'Error writing label file: {e}')
        response.alerts += Alert.from_exception(e)


async def maybe_apc_response_error(e: HTTPStatusError, shipment_request, shipment_response):
    if shipment_request.provider_name == ProviderName.APC:
        for alert in await apc_http_status_alerts(e):
            shipment_response.alerts += alert
    else:
        logger.exception(e)
        shipment_response.alerts += Alert.from_exception(e)


async def maybe_alert_apc(shipment_request):
    alerts = Alerts.empty()
    if (
        shipment_request.provider_name == ProviderName.APC
        and shipment_request.shipment.direction == ShipDirection.DROPOFF
    ):
        alerts += Alert(
            message='APC does not support drop-off shipments - please select Outbound or Inbound Collection',
            type=AlertType.ERROR,
        )
    return alerts


# async def convert_choice(choice: AddressChoicePF) -> AddressChoiceAgnost:
#     fc = parcelforce_full_contact(contact=ContactPF.empty(), address=choice.address)
#     return AddressChoiceAgnost(address=fc.address, score=choice.score)
