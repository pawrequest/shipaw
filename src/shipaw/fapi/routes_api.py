from pprint import pformat
from urllib.parse import unquote

from fastapi import APIRouter, Body, Depends
from loguru import logger
from royal_mail_combined.parcels_apis.address.models import (
    AddressRecordDef,
    AddressRecordDefPermissive,
    AddressSummaryDef,
    AddressesDef,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from shipaw.config import SHIPAW_SETTINGS
from shipaw.fapi.alerts import Alerts
from shipaw.fapi.backend import (
    errored_shipment,
    maybe_alert_apc,
    notify_dev,
    notify_version,
    resize_and_write_labels,
    try_book_shipment,
)
from shipaw.fapi.form_data import provider_from_form, shipment_request_form, shipment_request_form_json
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import CompletedShipmentResponse, ShipawTemplate, ShipawTemplateResponse
from shipaw.fapi.ui_funcs import make_nice_str
from shipaw.logging import log_obj, log_obj_text
from shipaw.models.shipment import Shipment
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.utils.consts_enums import RM_UNAVAIL

router = APIRouter()


@router.post('/shipping_form', response_model=ShipawTemplateResponse)
async def shipping_form_api(request: Request, shipment: Shipment = Body(...)) -> ShipawTemplateResponse:
    log_obj_text(shipment, 'Shipment received at /ship_form:')

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
    log_obj_text(shipment_request, 'ShipmentRequest received at shipaw/order_summary:')
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
    shipment_response: CompletedShipmentResponse = await try_book_shipment(shipment_request)
    if shipment_response.alerts.errors:
        return await errored_shipment(shipment_response)
    log_obj(shipment_response, 'Shipment Booked')

    await resize_and_write_labels(shipment_response.label_data, shipment_response.label_path)

    if hasattr(request.app, 'callback'):
        await request.app.callback(shipment_request, shipment_response)

    shipment_response.template = ShipawTemplate(
        template_path='/order_results.html',
        context={'shipment_request': shipment_request, 'response': shipment_response},
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
    logger.debug(f'Provider Services: {res_dir}')
    return JSONResponse(res_dir)


@router.get('/provider_direction_formats/{provider_name}/{direction}', response_class=JSONResponse)
async def provider_direction_formats(provider_name: str, direction: str):
    provider = await provider_from_form(provider_name)
    available = provider.valid_direction_formats.get(direction, [None])
    res_dir = {make_nice_str(_.name): _.value for _ in available}
    logger.debug(f'Provider Formats: {res_dir}')
    return JSONResponse(res_dir)


@router.get('/address_search/{search_text}', response_model=list[AddressSummaryDef])
async def address_search(search_text: str):
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    res = provider.client.address_search(search_text)
    logger.debug(f'Address search for "{search_text}" returned:\n{pformat(res, indent=2)}')
    return res.addresses


@router.get('/address_search_pc', response_model=list[AddressRecordDefPermissive])
async def address_search_pc(postcode: str, search_text: str):
    postcode = postcode.strip()
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    if not provider:
        logger.info(RM_UNAVAIL)
        return [AddressRecordDef(label=RM_UNAVAIL, address_id='')]
    res: AddressesDef = provider.client.address_search(f'{search_text}, {postcode}')
    logger.debug(
        f'Address search for {search_text} at postcode {postcode} returned {len(res.addresses)} addresses:\n'
        f'{",\n".join([addr.summary for addr in res.addresses])}'
    )
    hits = []
    for addr in res.addresses:
        if not addr.type == 'Address':
            logger.warning(f'Skipping "{addr.type}" type: {addr.summary}')
            continue
        retrieved: AddressRecordDef = provider.client.address_retrieve(addr.address_id)
        logger.info(f'Comparing retrieved postal code "{retrieved.postal_code}" with search postcode "{postcode}"')
        if retrieved.postal_code.strip() == postcode:
            hits.append(retrieved)
    logger.debug(
        f'{len(hits)} Address{"es" if len(hits) != 1 else ""} matched postcode "{postcode}":\n'
        f' {"\n".join([addr.label.replace("\n", ",") for addr in hits])}'
    )
    if len(hits) == 0:
        hits = [AddressRecordDefPermissive(label='No matching results', address_id='')]
    return hits


@router.get('/address_retrieve/{addr_id}', response_model=AddressRecordDefPermissive)
async def address_retrieve(addr_id: str):
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    if not provider:
        logger.info(RM_UNAVAIL)
        return AddressRecordDef(label=RM_UNAVAIL, address_id='')
    addr_id = unquote(addr_id)  # todo is this required?
    res: AddressRecordDef = provider.client.address_retrieve(addr_id)
    logger.debug(f'Address search for "{addr_id}" returned: {res.label}')
    return res


@router.get('/logs/stream')
async def logs_stream(request: Request):
    stream = request.app.state.log_stream

    async def event_source():
        async for chunk in stream.stream(replay=100):
            if await request.is_disconnected():
                break
            yield chunk

    return StreamingResponse(
        event_source(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )
