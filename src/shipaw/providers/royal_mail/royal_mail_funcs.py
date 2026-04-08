from pprint import pformat

from loguru import logger
from royal_mail_combined.click_and_drop_api.models import (
    AddressRequest,
    AddressReturns,
    BillingDetailsRequest,
    CreateOrderRequest,
    CreateOrdersResponse,
    CustomerReference,
    GetOrderInfoResource,
    PostageDetailsRequest,
    RecipientDetailsRequest,
    ReturnsRequest,
    Service,
    ShipmentPackageRequest,
)
from royal_mail_combined.click_and_drop_api.models import (
    ReturnShipment as RMReturnShipment,
)
from royal_mail_combined.click_and_drop_api.models.return_models import ReturnRequestContainer, ReturnResponseContainer
from royal_mail_combined.converters_no_import import tracking_link
from royal_mail_combined.core.consts_types import PackageFormat, RoyalMailServiceCodes, SendNotifcationsTo

from shipaw.config import SHIPAW_SETTINGS
from shipaw.fapi.responses import CompletedShipmentResponse
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.models.shipment import Shipment
from shipaw.utils.consts_enums import ShipDirection
from shipaw.utils.funcs import date_to_datetime


def build_booking_response_inbound(rm_response: ReturnResponseContainer, shipment: Shipment, label_data: bytes):
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


def print_response_errors(rm_response: CreateOrdersResponse):
    logger.error(f'Errors booking outbound shipment: {pformat(rm_response.failed_orders, indent=2, width=120)}')


def build_booking_response_outbound_f_fetched(
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


# def build_booking_response_outbound(
#     rm_response: CreateOrdersResponse, shipment: Shipment, label_data: bytes
# ) -> CompletedShipmentResponse:
#     success = rm_response.errors_count == 0
#     tracking_numbers = [order.tracking_number for order in rm_response.created_orders]
#     tracking_links = [tracking_link(_) for _ in tracking_numbers]
#     res = CompletedShipmentResponse(
#         shipment=shipment,
#         label_data=label_data,
#         shipment_num=rm_response.success_idents_str,
#         shipment_numbers=rm_response.success_ident_strs,
#         tracking_links=tracking_links,
#         data={_.order_identifier: _.model_dump() for _ in rm_response.created_orders},
#         status='Success' if success else 'FAIL',
#         success=success,
#     )
#     return res


def outbound_shipment_from_agnostic(shipment: Shipment, service_code: RoyalMailServiceCodes) -> CreateOrderRequest:
    billing_details = rm_billing_details_from_fc(SHIPAW_SETTINGS.full_contact)
    postage_details = create_postage_details(shipment=shipment, service_code=service_code)

    return CreateOrderRequest(
        order_reference=shipment.shipping_date.strftime('%d/%m') + ' ' + shipment.reference[0:34],
        postage_details=postage_details,
        billing=billing_details,
        recipient=rm_recipient_details_from_agnostic_fc(shipment.recipient),
        order_date=date_to_datetime(shipment.shipping_date),
        planned_despatch_date=date_to_datetime(shipment.shipping_date),
        subtotal=0,
        shipping_cost_charged=0,
        total=0,
        packages=create_packages(
            num_parcels=shipment.boxes, package_format=shipment.package_format, weight_kg=shipment.weight_kg
        ),
    )


def inbound_shipment_from_agnostic(shipment: Shipment, service_code: RoyalMailServiceCodes) -> ReturnRequestContainer:
    reqs = [
        ReturnsRequest(
            service=Service(service_code=service_code),
            shipment=RMReturnShipment(
                recipient_address=returns_address_from_agnostic_fc(shipment.recipient),
                sender_address=returns_address_from_agnostic_fc(shipment.sender),
                customer_reference=CustomerReference(reference=shipment.reference),
            ),
        )
        for _ in range(shipment.boxes)
    ]
    return ReturnRequestContainer(return_requests=reqs)


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
        SendNotifcationsTo.RECIPIENT if shipment.direction == ShipDirection.OUTBOUND else SendNotifcationsTo.BILLING
    )
    return PostageDetailsRequest(
        service_code=service_code,
        send_notifications_to=send_to,
        receive_email_notification=True,
        receive_sms_notification=True,
    )


def create_packages(*, num_parcels: int, package_format: PackageFormat, weight_kg: int):
    return [
        ShipmentPackageRequest(
            weight_in_grams=weight_kg * 1000,
            package_format_identifier=package_format,
        )
        for _ in range(num_parcels)
    ]


def rm_address_from_agnostic_fc(full_contact: FullContact) -> AddressRequest:
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


def rm_recipient_details_from_agnostic_fc(full_contact: FullContact) -> RecipientDetailsRequest:
    return RecipientDetailsRequest(
        address=rm_address_from_agnostic_fc(full_contact),
        phone_number=full_contact.contact.phone,
        email_address=full_contact.contact.email,
    )


def rm_billing_details_from_fc(full_contact: FullContact):
    return BillingDetailsRequest(
        address=rm_address_from_agnostic_fc(full_contact),
        phone_number=full_contact.contact.phone,
        email_address=full_contact.contact.email,
    )


def full_contact_from_rm(recipient: RecipientDetailsRequest) -> FullContact:
    return FullContact(
        contact=Contact(
            name=recipient.address.full_name,
            email=recipient.email_address,
            phone=recipient.phone_number,
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
