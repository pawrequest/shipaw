from pathlib import Path
from pprint import pformat

from fastapi import APIRouter, Body, Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from shipaw.config import SHIPAW_SETTINGS
from shipaw.fapi.ui_funcs import make_nice_str
from shipaw.fapi.alerts import Alert, AlertType, Alerts
from shipaw.fapi.backend import maybe_alert_apc, try_book_shipment, try_get_write_label
from shipaw.fapi.form_data import provider_from_form, shipment_request_form, shipment_request_form_json
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipawTemplate, ShipawTemplateResponse
from shipaw.logging import log_obj
from shipaw.models.shipment import Shipment
from shipaw.providers.registry import PROVIDER_REGISTER
from urllib.parse import unquote
from royal_mail_combined.parcels_apis.address.models import AddressRecordDef, AddressSummaryDef

router = APIRouter()


# router.mount('/static', StaticFiles(directory=str(SHIPAW_SETTINGS.static_dir)), name='static')


def get_version():
    from importlib.metadata import version, PackageNotFoundError

    try:
        return version('shipaw')
    except PackageNotFoundError:
        return 'unknown'


async def notify_version(request):
    alerts = Alerts.empty()
    sandbox = request.app.shipaw_settings.shipper_live == False
    if sandbox:
        live_msg = 'Test Mode - No Shipments will be booked'
        notification_type = AlertType.NOTIFICATION
    else:
        live_msg = 'Live Mode - Real Shipments will be booked'
        notification_type = AlertType.WARNING

    msg = f'Shipaw Version {get_version()} is in {live_msg}'
    logger.warning(msg)
    alerts += Alert(message=msg, type=notification_type)
    return alerts


def notify_dev() -> Alerts:
    alerts = Alerts.empty()
    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)
    return alerts


@router.post('/shipping_form', response_model=ShipawTemplateResponse)
async def shipping_form_api(request: Request, shipment: Shipment = Body(...)) -> ShipawTemplateResponse:
    log_obj(shipment, 'Shipment received at /ship_form:')

    alerts: Alerts = request.app.alerts
    alerts += notify_dev()
    alerts += await notify_version(request)

    tmplt = ShipawTemplate(template_path='shipping_form_container.html', context={'shipment': shipment})
    return ShipawTemplateResponse(template=tmplt, alerts=alerts)


@router.post('/order_summary', response_model=ShipawTemplateResponse)
async def order_summary_api(
        request: Request,
        shipment_request: ShipmentRequest = Depends(shipment_request_form),
) -> ShipawTemplateResponse:
    log_obj(shipment_request, 'ShipmentRequest received at shipaw/order_summary:')
    context = {'shipment_request': shipment_request}

    # check phone number
    # alerts = await maybe_alert_phone_number(shipment_request.shipment.remote_full_contact.contact.mobile_phone)
    # check not apc + dropoff
    alerts = await maybe_alert_apc(shipment_request)
    return ShipawTemplateResponse(
        template=ShipawTemplate(template_path='/order_summary.html', context=context),
        alerts=alerts,
    )


@router.post('/order_results', response_model=ShipawTemplateResponse)
async def order_results_api(
        request: Request,
        shipment_request: ShipmentRequest = Depends(shipment_request_form_json),
) -> ShipawTemplateResponse:
    shipment_response = await try_book_shipment(shipment_request)
    # await try_get_write_label(shipment_request, shipment_response)

    if shipment_response.alerts.errors:
        return await errored_shipment(shipment_response)

    log_obj(shipment_response, 'Shipment Booked')
    await try_get_write_label(shipment_request, shipment_response)

    if hasattr(request.app, 'callback'):
        await request.app.callback(shipment_request, shipment_response)

    shipment_response.template = ShipawTemplate(
        template_path='/order_results.html',
        context={'shipment_request': shipment_request, 'response': shipment_response},
    )
    return ShipawTemplateResponse.model_validate(shipment_response, from_attributes=True)


async def errored_shipment(shipment_response):
    log_obj(shipment_response.alerts, 'Errors booking shipment:')
    alerts = shipment_response.alerts
    shipment_response.template = ShipawTemplate(
        template_path='/alerts.html',
        context={'alerts': alerts},
    )
    return ShipawTemplateResponse.model_validate(shipment_response, from_attributes=True)


@router.get('/providers', response_class=JSONResponse)
async def providers():
    dflt = SHIPAW_SETTINGS.default_provider_name
    available = sorted(PROVIDER_REGISTER.keys(), key=lambda p: p != dflt)
    provider_response = {make_nice_str(_): _ for _ in available}
    return JSONResponse(provider_response)


@router.get('/provider_directions/{provider_name}', response_class=JSONResponse)
async def provider_directions(provider_name: str):
    provider = await provider_from_form(provider_name)
    directions = provider.valid_directions
    dir_dict = {make_nice_str(_.value): _.value for _ in directions}
    return JSONResponse(dir_dict)


@router.get('/provider_direction_services/{provider_name}/{direction}', response_class=JSONResponse)
async def provider_direction_services(provider_name: str, direction: str):
    provider = await provider_from_form(provider_name)
    dflt = provider.default_service
    available = sorted(provider.valid_direction_services.get(direction, []), key=lambda s: s.value != dflt)
    res_dir = {make_nice_str(_.name): _.value for _ in available}
    return JSONResponse(res_dir)


@router.get('/address_search/{search_text}', response_model=list[AddressSummaryDef])
async def address_search(search_text: str):
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    res = provider.client.address_search(search_text)
    # addresses = [_.model_dump(mode='json', by_alias=True) for _ in res.addresses]
    addresses = [_.model_dump(mode='json', by_alias=True) for _ in res.addresses]
    addr_string = pformat(res, indent=2)
    logger.debug(f'Address search for "{search_text}" returned:\n{addr_string}')
    return res.addresses


@router.get('/address_retrieve/{addr_id}', response_model=AddressRecordDef)
async def address_retrieve(addr_id: str):
    addr_id = unquote(addr_id)
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    res = provider.client.address_retrieve(addr_id)
    addr_string = pformat(res, indent=2)
    logger.debug(f'Address search for "{addr_id}" returned:\n{addr_string}')
    return res
