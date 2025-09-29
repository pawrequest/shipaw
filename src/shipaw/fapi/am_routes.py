# from combadge.core.errors import BackendError
# from fastapi import APIRouter, Body, Depends
# from loguru import logger
# from starlette.requests import Request
# from starlette.responses import HTMLResponse, JSONResponse
# from parcelforce_expresslink.address import AddressChoice as AddressChoicePF, AddressRecipient, Contact as ContactPF
# from parcelforce_expresslink.client import ParcelforceClient
#
# from shipaw.models.address import Address, AddressChoice as AddressChoiceAgnost, Contact
# from shipaw.config import shipaw_settings
# from shipaw.fapi.models.requests import ShipmentRequest
# from shipaw.models.responses import Alert, AlertType, Alerts
# from .models.request_response import AddressRequest
# from ..providers.parcelforce_provider import full_contact_from_provider_contact_address
#
# router = APIRouter()
#
#
# #
# # @router.post('/order_review1', response_class=HTMLResponse)
# # async def order_review(
# #     request: Request,
# #     shipment: Shipment = Depends(shipment_f_form),
# #     record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
# #     provider_name: ProviderName = Form(...),
# # ) -> HTMLResponse:
# #     alerts = await maybe_alert_phone_number(shipment)
# #     logger.info('Shipment Form Posted')
# #     template = 'ship/order_summary.html'
# #     ship_req = ShipmentRequestAgnost(shipment=shipment, provider_name=provider_name)
# #     return amherst_settings().templates.TemplateResponse(
# #         template, {'request': request, 'shipment_request': ship_req, 'record': record, 'alerts': alerts}
# #     )
#
#
# async def maybe_alert_phone_number(contact: Contact):
#     """Alert if phone number is not 11 digits or does not start with 01, 02 or 07. (parcelforce requirement)"""
#     alerts = Alerts.empty()
#     if len(contact.mobile_phone) != 11 or not contact.mobile_phone[1] in [
#         '1',
#         '2',
#         '7',
#     ]:
#         alerts += Alert(
#             type=AlertType.WARNING,
#             message='The Mobile phone number must be 11 digits and begin with 01, 02 or 07, no SMS will be sent',
#         )
#     return alerts
#
#
# @router.post('/post_confirm', response_class=HTMLResponse)
# async def order_confirm2(
#     request: Request,
#     shipment_req: ShipmentRequest = Depends(shipment_req_str_to_shipment2),
#     record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
# ) -> HTMLResponse:
#     logger.info('Booking Shipment')
#     shipment_response = await try_book_shipment(shipment_req)
#     shipment_req.provider.handle_response(shipment_req, shipment_response)
#
#     if not shipment_response or not shipment_response.success:
#         logger.error(f'Booking failed')
#         return amherst_settings().templates.TemplateResponse(
#             'alerts.html',
#             {
#                 'request': request,
#                 'alerts': shipment_response.alerts,
#                 'shipment': shipment_req.shipment,
#                 'record': record,
#             },
#         )
#
#     # get label
#     await shipment_response.write_label_file()
#
#     # update commence
#     await try_update_cmc(record, shipment_req.shipment, shipment_response)
#
#     return amherst_settings().templates.TemplateResponse(
#         'ship/order_results.html',
#         {
#             'request': request,
#             'shipment': shipment_req.shipment,
#             'response': shipment_response,
#             'alerts': shipment_response.alerts,
#         },
#     )
#
#
# # @router.get('/home_mobile_phone', response_class=PlainTextResponse)
# # async def home_mobile_phone():
# #     return shipaw_settings().mobile_phone
#
#
# @router.get('/home_mobile_phone', response_class=HTMLResponse)
# async def home_mobile_phone():
#     mobile_phone = shipaw_settings().mobile_phone
#     return f"""
#     <input type="tel" id="mobile_phone" name="mobile_phone" value="{mobile_phone}" required>
#     """
#
#
#
#
# @router.post('/cand', response_model=list[AddressChoiceAgnost], response_class=JSONResponse)
# async def get_addr_choices(
#     request: Request,
#     body: AddressRequest = Body(...),
#     el_client: ParcelforceClient = Depends(get_el_client),
# ) -> list[AddressChoiceAgnost]:
#     """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.
#
#     Args:
#         request: Request - FastAPI request object
#         body: Address - request body containing postcode and optional address
#         el_client: ELClient - Parcelforce ExpressLink client
#     """
#     # address = ParcelforceShippingProvider.provider_address(address)
#     postcode = body.postcode
#     address_agnost = body.address
#     pf_address = (
#         AddressRecipient(
#             address_line1=address_agnost.address_lines[0],
#             address_line2=address_agnost.address_lines[1] if len(address_agnost.address_lines) > 1 else '',
#             address_line3=address_agnost.address_lines[2] if len(address_agnost.address_lines) > 2 else '',
#             town=address_agnost.town,
#             postcode=address_agnost.postcode,
#             country=address_agnost.country,
#         )
#         if address_agnost
#         else None
#     )
#
#     try:
#         res = el_client.get_choices(postcode=postcode, address=pf_address)
#         res_agnost = [await convert_choice(_) for _ in res]
#         return res_agnost
#     except BackendError as e:
#         alert = Alert(
#             message=f'Error fetching candidates: {e}',
#             type=AlertType.ERROR,
#         )
#         request.app.alerts += alert  # todo is this received frontend?
#         logger.warning(f'Error fetching candidates: {e}')
#         addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error', business_name='Error')
#         chc = AddressChoiceAgnost(address=addr, score=0)
#         return [chc]
#
#
# async def convert_choice(choice: AddressChoicePF) -> AddressChoiceAgnost:
#     fc = full_contact_from_provider_contact_address(contact=ContactPF.empty(), address=choice.address)
#     return AddressChoiceAgnost(
#         address=fc.address,
#         score=choice.score,
#     )
