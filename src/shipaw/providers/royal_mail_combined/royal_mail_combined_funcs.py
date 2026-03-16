from datetime import datetime, date

from royal_mail_combined.click_and_drop_api.models import (
    AddressRequest,
    AddressReturns,
    BillingDetailsRequest,
    CreateOrderRequest,
    CreateOrdersRequest,
    CustomerReference,
    PostageDetailsRequest,
    RecipientDetailsRequest,
    ReturnsRequest,
    Service,
    ShipmentPackageRequest,
    ReturnShipment as RMReturnShipment,
)
from royal_mail_combined.core.consts_types import PackageFormat, RoyalMailServiceCodes, SendNotifcationsTo

from shipaw.config import ShipawSettings
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment


def outbound_shipment_from_agnostic(shipment: Shipment, service_code: RoyalMailServiceCodes) -> CreateOrderRequest:
    shipaw_settings = ShipawSettings.from_env('SHIPAW_ENV')
    billing_details = rm_billing_details_from_fc(shipaw_settings.full_contact)
    postage_details = create_postage_details(shipment=shipment, service_code=service_code)

    return CreateOrderRequest(
        order_reference=shipment.reference,
        postage_details=postage_details,
        billing=billing_details,
        recipient=rm_recipient_details_from_agnostic_fc(shipment.recipient),
        order_date=date_to_datetime(shipment.shipping_date),
        planned_despatch_date=date_to_datetime(shipment.shipping_date),
        subtotal=0,
        shipping_cost_charged=0,
        total=0,
        packages=create_packages(num_parcels=shipment.boxes, package_format=PackageFormat.PARCEL),
    )


def inbound_shipment_from_agnostic(shipment: Shipment, service_code: RoyalMailServiceCodes) -> ReturnsRequest:
    return ReturnsRequest(
        service=Service(service_code=service_code),
        shipment=RMReturnShipment(
            recipient_address=returns_address_from_agnostic_fc(shipment.recipient),
            sender_address=returns_address_from_agnostic_fc(shipment.sender),
            customer_reference=CustomerReference(reference=shipment.reference)
        )
    )


def returns_address_from_agnostic_fc(full_contact: FullContact):
    first, last = full_contact.contact.contact_name.split()
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
        email=full_contact.contact.email_address,
    )


def date_to_datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())


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


def create_packages(*, num_parcels: int, package_format: PackageFormat):
    return [
        ShipmentPackageRequest(
            weight_in_grams=10000,
            package_format_identifier=package_format,
        )
        for _ in range(num_parcels)
    ]


def rm_address_from_agnostic_fc(full_contact: FullContact) -> AddressRequest:
    return AddressRequest(
        full_name=full_contact.contact.contact_name,
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
        phone_number=full_contact.contact.mobile_phone or full_contact.contact.phone_number,
        email_address=full_contact.contact.email_address,
    )


def rm_billing_details_from_fc(full_contact: FullContact):
    return BillingDetailsRequest(
        address=rm_address_from_agnostic_fc(full_contact),
        phone_number=full_contact.contact.phone_number,
        email_address=full_contact.contact.email_address,
    )


def full_contact_from_rm(recipient: RecipientDetailsRequest) -> FullContact:
    return FullContact(
        contact=Contact(
            contact_name=recipient.address.full_name,
            phone_number=recipient.phone_number,
            email_address=recipient.email_address,
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
