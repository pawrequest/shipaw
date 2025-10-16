from typing import ClassVar, override

from pydantic import BaseModel, Field
from royal_mail_click_and_drop import CreateOrdersRequest, CreateOrdersResponse, ShipmentPackageRequest
from royal_mail_click_and_drop.config import RoyalMailSettings
from royal_mail_click_and_drop.models.address import (
    AddressRequest as AddressRM,
    RecipientDetailsRequest as ContactRM,
)
from royal_mail_click_and_drop.models.create_orders_request import CreateOrderRequest
from royal_mail_click_and_drop.v2.client import RoyalMailClient, RoyalMailServiceCode

from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.logging import log_obj
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ShippingProvider
from shipaw.providers.royal_mail.provider_funcs import date_to_datetime


class RoyalMailServices(Services):
    NEXT_DAY = 'parcel'
    NEXT_DAY_12 = ''
    NEXT_DAY_9 = ''

    @override
    def lookup(self, agnostic_name: str) -> RoyalMailServiceCode:
        return RoyalMailServiceCode(super().lookup(agnostic_name))


ROYAL_MAIL_SERVICES = RoyalMailServices(NEXT_DAY='parcel', NEXT_DAY_12='', NEXT_DAY_9='')


def create_packages(*, num_parcels: int, service: RoyalMailServiceCode):
    if not service == RoyalMailServices.NEXT_DAY:
        raise NotImplementedError('only next day available atm')
    return [
        ShipmentPackageRequest(
            weight_in_grams=10000,
            package_format_identifier=service,
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


class RoyalMailProvider(ShippingProvider):
    name: ClassVar[str] = 'ROYAL_MAIL'
    services = ROYAL_MAIL_SERVICES
    settings_type: ClassVar[type[RoyalMailSettings]] = RoyalMailSettings
    settings: RoyalMailSettings
    _client: RoyalMailClient | None = None
    responses: list[CreateOrdersResponse] = Field(default_factory=list)

    def is_sandbox(self) -> bool:
        return False

    @property
    def client(self) -> RoyalMailClient:
        if self._client is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self._client = RoyalMailClient(settings=self.settings)
        return self._client

    def provider_shipment(self, shipment: Shipment) -> CreateOrdersRequest:
        if shipment.direction != ShipDirection.OUTBOUND:
            # todo: implement inbound / dropoff
            raise NotImplementedError('only outbound shipments are supported for Royal Mail')
        return CreateOrdersRequest(
            items=[
                CreateOrderRequest(
                    recipient=rm_recipient_details_from_agnostic_fc(shipment.recipient),
                    order_date=date_to_datetime(shipment.shipping_date),
                    planned_despatch_date=date_to_datetime(shipment.shipping_date),
                    subtotal=1000,
                    shipping_cost_charged=0,
                    total=1000,
                    packages=create_packages(
                        num_parcels=shipment.boxes, service=self.services.lookup(shipment.service)
                    ),
                )
            ]
        )
    #
    # def agnostic_shipment(self, orders_req: CreateOrdersRequest) -> Shipment:
    #     order = orders_req.items[0]
    #     return Shipment(
    #         recipient=full_contact_from_rm(order.recipient),
    #         boxes=len(order.packages),
    #         shipping_date=order.planned_despatch_date.date(),
    #         direction=ShipDirection.OUTBOUND,
    #         reference=order.order_reference,
    #         service=self.services.reverse_lookup(order.packages[0].package_format_identifier),
    #     )

    def build_booking_request(self, shipment: Shipment) -> CreateOrdersRequest:
        shipment_rm = self.provider_shipment(shipment)
        log_obj(shipment_rm, 'Royal Mail Shipment Request')
        return shipment_rm

    def book_shipment(self, shipment: Shipment) -> ShipmentBookingResponse:
        ship = self.build_booking_request(shipment)
        resp = self.client.book_shipment(ship)
        return self.build_booking_response(resp, shipment)

    def build_booking_response(self, rm_response: CreateOrdersResponse, shipment):
        """without label data"""
        if rm_response.errors_count > 0:
            raise RuntimeError()
        order = rm_response.created_orders[0]
        track_num = order.tracking_number
        success = rm_response.errors_count == 0
        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=order.order_identifier,
            tracking_link=self.settings.tracking_link(track_num),
            data=rm_response.model_dump(),
            status='Success' if success else 'FAIL',
            success=success,
        )

    def fetch_label_content(self, order_ident_str: str) -> bytes:
        return self.client.get_label_content(order_ident_str)
