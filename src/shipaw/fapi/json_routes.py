from pathlib import Path
from typing import Annotated

from combadge.core.errors import BackendError
from fastapi import APIRouter, Body, Depends
from loguru import logger
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.address import AddressChoice as AddressChoicePF, Contact as ContactPF
from shipaw.config import shipaw_settings
from shipaw.fapi.backend import get_el_client, try_book_shipment
from shipaw.fapi.form_data import shipment_request_from_form, shipment_request_from_json
from shipaw.fapi.requests import AddressRequest, ShipmentRequest
from shipaw.fapi.alerts import Alert, AlertType, Alerts, maybe_alert_phone_number
from shipaw.models.conversation import ShipmentConversation
from shipaw.models.logging import log_obj
from shipaw.models.shipment import Shipment
from shipaw.fapi.responses import ShipawTemplateResponse
from shipaw.models.address import Address, AddressChoice as AddressChoiceAgnost
from shipaw.providers.parcelforce_provider import address_from_agnostic, full_contact_from_provider_contact_address

router = APIRouter()


@router.post('/shipping_form', response_model=ShipawTemplateResponse)
async def ship_form(
    request: Request, shipment: Shipment = Body(...), context: dict | None = None
) -> ShipawTemplateResponse:
    log_obj(shipment, 'Shipment received at /ship_form:')
    alerts: Alerts = request.app.alerts

    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    if shipaw_settings().shipper_live:
        msg = 'Shipper Live is True - Real Shipments will be booked'
    else:
        msg = 'Shipper_live is False - No Shipments will be booked'
    logger.warning(msg)
    alerts += Alert(message=msg, type=AlertType.NOTIFICATION)

    ctx = {'shipment': shipment}
    return ShipawTemplateResponse(template_path='shipping_form_container.html', context=ctx, alerts=alerts)


@router.post('/order_summary', response_model=ShipawTemplateResponse)
async def order_summary(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_from_form),
) -> ShipawTemplateResponse:
    log_obj(shipment_request, 'ShipmentRequest received at /order_review:')
    alerts = await maybe_alert_phone_number(shipment_request.shipment.remote_full_contact.contact.mobile_phone)
    context = {'shipment_request': shipment_request}
    return ShipawTemplateResponse(template_path='/order_summary.html', context=context, alerts=alerts)


@router.post('/order_results', response_model=ShipawTemplateResponse)
async def order_results(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_from_json),
) -> ShipawTemplateResponse | RedirectResponse:
    shipment_response = await try_book_shipment(shipment_request)
    shipment_request.provider.handle_response(shipment_request, shipment_response)
    # if shipment_request.handler:
    #     await shipment_request.handler(shipment_request, shipment_response)
    conversation = ShipmentConversation(request=shipment_request, response=shipment_response)
    log_obj(conversation, 'ShipmentConversation at /order_confirm:')
    # redirect to URL provided in shipment_request
    if redirec := shipment_request.shipment.context.get('redirect') is not None:
        logger.info(f'Redirecting to {redirec} as per shipment_request context')
        return RedirectResponse(url=redirec)

    return ShipawTemplateResponse(
        template_path='/order_results.html',
        context={'shipment_response': shipment_response},
        alerts=request.app.alerts,
    )


@router.post('/addr_choices', response_model=list[AddressChoiceAgnost], response_class=JSONResponse)
async def get_addr_choices(
    request: Request,
    body: AddressRequest = Body(...),
    el_client: ParcelforceClient = Depends(get_el_client),
) -> list[AddressChoiceAgnost]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.

    Args:
        request: Request - FastAPI request object
        body: Address - request body containing postcode and optional address
        el_client: ELClient - Parcelforce ExpressLink client
    """
    postcode = body.postcode
    address_agnost = body.address
    pf_address = address_from_agnostic(address_agnost) if address_agnost else None
    log_obj(pf_address, 'Address received at /cand:')

    try:
        res = el_client.get_choices(postcode=postcode, address=pf_address)
        res_agnost = [await convert_choice(_) for _ in res]
        # log_objs(res_agnost, 'Address choices returned from /cand:')
        return res_agnost

    except BackendError as e:
        alert = Alert(
            message=f'Error fetching candidates: {e}',
            type=AlertType.ERROR,
        )
        request.app.alerts += alert  # todo is this received frontend?
        logger.warning(f'Error fetching candidates: {e}')
        addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error', business_name='Error')
        chc = AddressChoiceAgnost(address=addr, score=0)
        return [chc]


async def convert_choice(choice: AddressChoicePF) -> AddressChoiceAgnost:
    fc = full_contact_from_provider_contact_address(contact=ContactPF.empty(), address=choice.address)
    return AddressChoiceAgnost(address=fc.address, score=choice.score)

