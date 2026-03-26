from __future__ import annotations

from pathlib import Path

from apc_hypaship.error import apc_http_status_alerts
from httpx import HTTPStatusError
from loguru import logger
from pawdf.array_pdf.array_p import on_a4

from shipaw.fapi.alerts import Alert, AlertType, Alerts
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipawTemplate, ShipawTemplateResponse, ShipmentResponse
from shipaw.logging import log_obj
from shipaw.models.ship_types import ShipDirection

from shipaw.providers.provider_abc import ProviderName


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
    # await try_write_label(response)
    await try_write_label2(response)


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


# async def try_write_label(response: ShipmentResponse):
#     try:
#         await response.write_label_file()
#     except Exception as e:
#         logger.exception(f'Error writing label file: {e}')
#         response.alerts += Alert.from_exception(e)


async def try_write_label2(response: ShipmentResponse):
    try:
        label_content = response.label_data
        label_path = response.label_path
        await array_write_label_content(label_content, label_path)

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


async def array_write_label_content(label_content: bytes, label_path: Path):
    og_size_path = label_path.parent / 'original_size' / label_path.name
    og_size_path.parent.mkdir(parents=True, exist_ok=True)
    og_size_path.write_bytes(label_content)
    logger.info(f'Resizing {og_size_path} to A4 at {label_path}')
    on_a4(input_file=og_size_path, output_file=label_path)
    logger.info(f'Wrote label to {label_path}')


def get_version():
    from importlib.metadata import version, PackageNotFoundError

    try:
        return version('shipaw')
    except PackageNotFoundError:
        return 'unknown'


async def notify_version(request):
    alerts = Alerts.empty()
    sandbox = request.app.shipaw_settings.shipper_live is False
    if sandbox:
        live_msg = 'Test Mode - No Shipments will be booked'
        notification_type = AlertType.NOTIFICATION
    else:
        live_msg = 'Live Mode - Real Shipments will be booked'
        notification_type = AlertType.WARNING

    msg = f'Shipaw Version {get_version()} is in {live_msg}'
    logger.info(msg)
    alerts += Alert(message=msg, type=notification_type)
    return alerts


def notify_dev() -> Alerts:
    alerts = Alerts.empty()
    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version'
        logger.info(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)
    return alerts


async def errored_shipment(shipment_response):
    log_obj(shipment_response.alerts, 'Errors booking shipment:')
    alerts = shipment_response.alerts
    shipment_response.template = ShipawTemplate(
        template_path='/alerts.html',
        context={'alerts': alerts},
    )
    return ShipawTemplateResponse.model_validate(shipment_response, from_attributes=True)
