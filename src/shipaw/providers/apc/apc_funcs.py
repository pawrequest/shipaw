from __future__ import annotations

from apc_hypaship.error import apc_http_status_alerts
from apc_hypaship.models.request.address import Address, Contact
from httpx import HTTPStatusError
from loguru import logger

from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.models.address import Address as AddressAgnost
from shipaw.models.address import Contact as ContactAgnost
from shipaw.models.address import FullContact
from shipaw.providers.provider_abc import ProviderName
from shipaw.utils.consts_enums import ShipDirection


def address_from_agnostic_fc[addr_type: Address](cls: type[addr_type], full_contact: FullContact) -> addr_type:
    lines_ = [_ for _ in full_contact.address.address_lines[1:] if _]
    lines = ', '.join(lines_)
    return cls(
        company_name=full_contact.address.business_name,
        address_line_1=full_contact.address.address_lines[0],
        address_line_2=lines,
        city=full_contact.address.town,
        postal_code=full_contact.address.postcode,
        country_code=full_contact.address.country,
        contact=Contact(
            person_name=full_contact.contact.contact_name,
            email=full_contact.contact.email_address,
            mobile_number=full_contact.contact.mobile_phone,
            phone_number=full_contact.contact.phone_number or full_contact.contact.mobile_phone,
        ),
    )


def contact_from_agnostic_fc[contact_type: Contact](cls: type[contact_type], full_contact: FullContact) -> contact_type:
    return cls(
        person_name=full_contact.contact.contact_name,
        email=full_contact.contact.email_address,
        mobile_number=full_contact.contact.mobile_phone,
        phone_number=full_contact.contact.phone_number,
    )


def full_contact_from_apc_contact_address(contact: Contact, address: Address) -> FullContact:
    return FullContact(
        address=AddressAgnost(
            business_name=address.company_name,
            address_lines=[line for line in [address.address_line_1, address.address_line_2] if line],
            town=address.city,
            postcode=address.postal_code,
            country=address.country_code,
        ),
        contact=ContactAgnost(
            contact_name=contact.person_name,
            email_address=contact.email,
            mobile_phone=contact.mobile_number,
            phone_number=contact.phone_number or contact.mobile_number,
        ),
    )


async def apc_shipment_request_alerts(shipment_request) -> Alerts:
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


async def add_apc_response_errors_to_shipment_response_alerts(e: HTTPStatusError, shipment_request, shipment_response):
    if shipment_request.provider_name == ProviderName.APC:
        for alert in await apc_http_status_alerts(e):
            shipment_response.alerts += alert
    else:
        logger.exception(e)
        shipment_response.alerts += Alert.from_exception(e)
