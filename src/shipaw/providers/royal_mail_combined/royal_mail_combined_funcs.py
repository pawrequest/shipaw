from datetime import datetime, date

from royal_mail_click_and_drop import (
    AddressRequest as AddressRM,
    BillingDetailsRequest,
    PostageDetailsRequest,
    ShipmentPackageRequest,
)
from royal_mail_click_and_drop.models.address import RecipientDetailsRequest as ContactRM
from royal_mail_click_and_drop.models.shipment_package_request import PackageFormat
from royal_mail_click_and_drop.v2.consts import SendNotifcationsTo

from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment


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


def rm_address_from_agnostic_fc(full_contact: FullContact) -> AddressRM:
    return AddressRM(
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


def rm_recipient_details_from_agnostic_fc(full_contact: FullContact) -> ContactRM:
    return ContactRM(
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


def full_contact_from_rm(recipient: ContactRM) -> FullContact:
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
