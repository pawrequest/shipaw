import json

from httpx import HTTPStatusError
from loguru import logger
from parcelforce_expresslink.client import ParcelforceClient

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.fapi.alerts import AlertType, Alert


def extract_http_error_message(exception: HTTPStatusError) -> str:
    if hasattr(exception, 'response') and exception.response is not None:
        return exception.response.text
    logger.warning('HTTPStatusError has no response attribute')
    return str(exception)


def extract_http_error_message_json(exception: HTTPStatusError) -> dict:
    error_string = extract_http_error_message(exception)
    try:
        error_data = json.loads(error_string)
        return error_data.get('Messages')

    except json.JSONDecodeError:
        logger.warning('Error.response.text is not valid JSON')
        return {'Code': error_string, 'Description': ''}


async def http_status_alerts(exception: HTTPStatusError) -> list[Alert]:
    error_dict = extract_http_error_message_json(exception)
    return [Alert(message=f'{error_dict.get('Code')}:  {error_dict.get('Description')}', type=AlertType.ERROR)]


async def try_book_shipment(shipment_request: ShipmentRequest) -> ShipmentBookingResponse:
    shipment_response = ShipmentBookingResponse(shipment=shipment_request.shipment)
    try:
        shipment_response = shipment_request.provider.book_shipment(shipment_request.shipment)

    except HTTPStatusError as e:
        for alert in await http_status_alerts(e):
            shipment_response.alerts += alert

    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        shipment_response.alerts += Alert.from_exception(e)

    return shipment_response


async def try_get_label_data(request: ShipmentRequest, response: ShipmentBookingResponse) -> bytes | None:
    try:
        if response.label_data is None and response.shipment_num:
            response.label_data = request.provider.get_label_content(response.shipment_num)
        return response.label_data

    except HTTPStatusError as e:
        for alert in await http_status_alerts(e):
            response.alerts += alert
        logger.exception(f'HTTP error getting label data')

    except Exception as e:
        logger.exception(f'Error getting label data')
        response.alerts += Alert.from_exception(e)

    return None


async def try_write_label(response: ShipmentBookingResponse):
    try:
        await response.write_label_file()
    except Exception as e:
        logger.exception(f'Error writing label file: {e}')
        response.alerts += Alert.from_exception(e)


async def try_get_write_label(request: ShipmentRequest, response: ShipmentBookingResponse):
    if not response.label_data:
        await try_get_label_data(request, response)
    await try_write_label(response)


def get_el_client() -> ParcelforceClient:
    try:
        return ParcelforceClient()
    except Exception as e:
        logger.error(f'Error getting Parcelforce ExpressLink Client: {e}')
        raise

