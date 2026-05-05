from __future__ import annotations

from pprint import pformat
from typing import Any

from loguru import logger
from royal_mail_combined.click_and_drop_api.models import (
    AddressRequest,
    AddressReturns,
    CreateOrderRequest,
    CreateOrdersRequest,
    CreateOrdersResponse,
    CustomerReference,
    GetOrderInfoResource,
    PostageDetailsRequest,
    RecipientDetailsRequest,
    ReturnShipment as RMReturnShipment,
    ReturnsRequest,
    Service,
    ShipmentPackageRequest,
)
from royal_mail_combined.click_and_drop_api.models.return_models import ReturnRequestContainer, ReturnResponseContainer
from royal_mail_combined.converters_no_import import tracking_link
from royal_mail_combined.core.consts_types import PackageFormat, RoyalMailServiceCodes, SendNotifcationsTo
from royal_mail_combined.core.helpers import should_split_rm_tracked_24
from royal_mail_combined.parcels_apis.collection_order.models import SenderDetailsPostDef

from shipaw.models.responses import CompletedShipmentResponse
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.models.shipment import Shipment, build_reference
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.utils.consts_enums import ShipDirection
from shipaw.utils.funcs import date_to_datetime


# Calls
async def address_lookup(postcode: str, search_string: str) -> list[Any]:
    """Return list of AddressRecordDef matching the address / postcode."""
    from shipaw.utils.funcs import compare_texts

    royalmail_provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    if not royalmail_provider:
        return []
    postcode = postcode.strip()

    summaries = royalmail_provider.client.address_search(search_string).addresses

    hits = []
    for summary in summaries:
        if summary.type != 'Address':
            continue
        try:
            rec = royalmail_provider.client.address_retrieve(summary.address_id)
            if compare_texts(rec.postal_code, postcode):
                hits.append(rec)
        except Exception as exc:
            logger.warning(f'Address retrieve failed for {summary.address_id}: {exc}')
    return hits


# Converters
def outbound_shipment(shipment: Shipment, service_code: RoyalMailServiceCodes) -> CreateOrdersRequest:
    postage_details = create_postage_details(shipment=shipment, service_code=service_code)
    if should_split_rm_tracked_24(service_code, shipment.boxes):
        return _create_outbound_split(postage_details, shipment)
    else:
        return _create_outbound_unsplit(postage_details, shipment)


def _create_outbound_unsplit(postage_details: PostageDetailsRequest, shipment: Shipment) -> CreateOrdersRequest:
    order = CreateOrderRequest(
        order_reference=build_reference(shipment.reference, 40, shipment.boxes, shipment.shipping_date),
        postage_details=postage_details,
        # billing_details = billing_details_from_fullcontact(SHIPAW_SETTINGS.full_contact)
        recipient=recipient_from_fullcontact(shipment.recipient),
        order_date=date_to_datetime(shipment.shipping_date),
        planned_despatch_date=date_to_datetime(shipment.shipping_date),
        subtotal=0,
        shipping_cost_charged=0,
        total=0,
        packages=create_packages(
            num_parcels=shipment.boxes, package_format=shipment.package_format, weight_kg=shipment.weight_kg
        ),
    )
    return CreateOrdersRequest(items=[order])


def _create_outbound_split(postage_details: PostageDetailsRequest, shipment: Shipment) -> CreateOrdersRequest:
    orders = [
        CreateOrderRequest(
            order_reference=build_reference(
                shipment.reference,
                40,
                shipment.boxes,
                shipment.shipping_date,
                box=i + 1,
            ),
            postage_details=postage_details,
            recipient=recipient_from_fullcontact(shipment.recipient),
            order_date=date_to_datetime(shipment.shipping_date),
            planned_despatch_date=date_to_datetime(shipment.shipping_date),
            subtotal=0,
            shipping_cost_charged=0,
            total=0,
            packages=create_packages(
                num_parcels=1, package_format=shipment.package_format, weight_kg=shipment.weight_kg
            ),
        )
        for i in range(shipment.boxes)
    ]
    return CreateOrdersRequest(items=orders)


# Inbound Shipment
def create_remote_shipment(shipment: Shipment, service_code: RoyalMailServiceCodes) -> ReturnRequestContainer:
    sender = returns_address_from_agnostic_fc(shipment.sender)
    recipient = returns_address_from_agnostic_fc(shipment.recipient)
    reqs = [
        ReturnsRequest(
            service=Service(service_code=service_code),
            shipment=RMReturnShipment(
                recipient_address=recipient,
                sender_address=sender,
                customer_reference=CustomerReference(
                    reference=build_reference(shipment.reference, 40, shipment.boxes, shipment.shipping_date, box=i + 1)
                ),
            ),
        )
        for i in range(shipment.boxes)
    ]
    return ReturnRequestContainer(return_requests=reqs)


# Responses
def booking_response_inbound(rm_response: ReturnResponseContainer, shipment: Shipment, label_data: bytes):
    return CompletedShipmentResponse(
        label_data=label_data,
        shipment=shipment,
        shipment_num=rm_response.unique_ids_str,
        shipment_numbers=rm_response.unique_ids,
        tracking_links=rm_response.tracking_links,
        collection_id=rm_response.collection_response.collection_order_id if rm_response.collection_response else None,
        data=rm_response.model_dump(),
        status='Success',
        success=True,
    )


def booking_response_outbound(
    fetched: list[GetOrderInfoResource], shipment: Shipment, label_data: bytes
) -> CompletedShipmentResponse:
    tracking_numbers = [order.tracking_number for order in fetched]
    tracking_links = [tracking_link(_) for _ in tracking_numbers]
    idents = [_.order_identifier for _ in fetched]
    idents_s = map(str, idents)
    res = CompletedShipmentResponse(
        order_identifiers=idents,
        shipment=shipment,
        label_data=label_data,
        shipment_num=';'.join(idents_s),
        shipment_numbers=tracking_numbers,
        tracking_links=tracking_links,
        data={_.order_identifier: _.model_dump() for _ in fetched},
        status='Success',
        success=True,
    )
    return res


# Helpers
def print_response_errors(rm_response: CreateOrdersResponse):
    logger.error(f'Errors booking outbound shipment: {pformat(rm_response.failed_orders, indent=2, width=120)}')


def returns_address_from_agnostic_fc(full_contact: FullContact):
    names = full_contact.contact.name.split()
    first = names[0]
    last = ' '.join(names[1:]) if len(names) > 1 else ''
    return AddressReturns(
        title='',
        first_name=first,
        last_name=last,
        company_name=full_contact.address.business_name,
        address_line1=full_contact.address.address_lines[0],
        address_line2=full_contact.address.address_lines[1] if len(full_contact.address.address_lines) > 1 else None,
        address_line3=full_contact.address.address_lines[2] if len(full_contact.address.address_lines) > 2 else None,
        city=full_contact.address.town,
        county=full_contact.address.county,
        postcode=full_contact.address.postcode,
        country=full_contact.address.country,
        email=full_contact.contact.email,
    )


def create_postage_details(shipment: Shipment, service_code):
    send_to = (
        SendNotifcationsTo.RECIPIENT
        if shipment.direction in [ShipDirection.OUTBOUND, ShipDirection.THIRD_PARTY]
        else SendNotifcationsTo.BILLING
    )
    return PostageDetailsRequest(
        service_code=service_code,
        send_notifications_to=send_to,
        receive_email_notification=True,
        receive_sms_notification=True,
    )


def create_packages(*, num_parcels: int, package_format: PackageFormat, weight_kg: int) -> list[ShipmentPackageRequest]:
    return [
        ShipmentPackageRequest(
            weight_in_grams=weight_kg * 1000,
            package_format_identifier=package_format,
        )
        for _ in range(num_parcels)
    ]


def address_from_fullcontact(full_contact: FullContact) -> AddressRequest:
    return AddressRequest(
        full_name=full_contact.contact.name,
        company_name=full_contact.address.business_name,
        address_line1=full_contact.address.address_lines[0],
        address_line2=full_contact.address.address_lines[1] if len(full_contact.address.address_lines) > 1 else None,
        address_line3=full_contact.address.address_lines[2] if len(full_contact.address.address_lines) > 2 else None,
        city=full_contact.address.town,
        county=full_contact.address.county,
        postcode=full_contact.address.postcode,
        country_code=full_contact.address.country,
    )


def recipient_from_fullcontact(full_contact: FullContact) -> RecipientDetailsRequest:
    return RecipientDetailsRequest(
        address=address_from_fullcontact(full_contact),
        phone_number=full_contact.contact.mobile_phone or full_contact.contact.phone_number,
        email_address=full_contact.contact.email,
    )


# def billing_details_from_fullcontact(full_contact: FullContact):
#     return BillingDetailsRequest(
#         address=address_from_fullcontact(full_contact),
#         phone_number=full_contact.contact.phone_number,
#         email_address=full_contact.contact.email,
#     )


def sender_details_from_fullcontact(full_contact: FullContact):
    return SenderDetailsPostDef(
        sender_name=full_contact.contact.name,
        sender_email=full_contact.contact.email,
    )


def fullcontact_from_recipient(recipient: RecipientDetailsRequest) -> FullContact:
    return FullContact(
        contact=Contact(
            name=recipient.address.full_name,
            phone_number=recipient.phone_number,
            email=recipient.email_address,
            mobile_phone=recipient.phone_number,
        ),
        address=Address(
            business_name=recipient.address.company_name,
            address_lines=[
                line
                for line in [
                    recipient.address.address_line1,
                    recipient.address.address_line2,
                    recipient.address.address_line3,
                ]
                if line
            ],
            town=recipient.address.city,
            county=recipient.address.county,
            postcode=recipient.address.postcode,
            country=recipient.address.country_code,
        ),
    )
