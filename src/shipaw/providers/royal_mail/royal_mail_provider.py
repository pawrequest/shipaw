from typing import ClassVar

from loguru import logger
from pydantic import Field
from royal_mail_click_and_drop import (
    CreateOrdersRequest,
    CreateOrdersResponse,
)
from royal_mail_click_and_drop.config import RoyalMailSettings
from royal_mail_click_and_drop.models.create_orders_request import CreateOrderRequest
from royal_mail_click_and_drop.models.shipment_package_request import PackageFormat
from royal_mail_click_and_drop.v2.client import RoyalMailClient

from shipaw.config import ShipawSettings
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.logging import log_obj
from shipaw.models.services import AgnostServiceName
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider
from shipaw.providers.royal_mail.provider_funcs import (
    ROYAL_MAIL_SERVICES,
    create_packages,
    create_postage_details,
    date_to_datetime,
    full_contact_from_rm,
    rm_billing_details_from_fc,
    rm_recipient_details_from_agnostic_fc,
)


@register_provider
class RoyalMailProvider(ShippingProvider):
    name: ClassVar[ProviderName] = ProviderName.ROYAL_MAIL
    services = ROYAL_MAIL_SERVICES
    settings_type: ClassVar[type[RoyalMailSettings]] = RoyalMailSettings
    settings: RoyalMailSettings
    _client: RoyalMailClient | None = None
    responses: list[CreateOrdersResponse] = Field(default_factory=list)

    def is_sandbox(self) -> bool:
        # Royal mail do not have a test environment. that's fun
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
        if shipment.service not in (AgnostServiceName.NEXT_DAY, AgnostServiceName.NEXT_DAY_12):
            raise NotImplementedError('only NEXT_DAY service is implemented for Royal Mail')
        shipaw_settings = ShipawSettings.from_env('SHIPAW_ENV')
        billing_details = rm_billing_details_from_fc(shipaw_settings.full_contact)
        postage_details = create_postage_details(shipment=shipment)

        return CreateOrdersRequest(
            items=[
                CreateOrderRequest(
                    order_reference=shipment.reference,
                    postage_details=postage_details,
                    billing=billing_details,
                    recipient=rm_recipient_details_from_agnostic_fc(shipment.recipient),
                    order_date=date_to_datetime(shipment.shipping_date),
                    planned_despatch_date=date_to_datetime(shipment.shipping_date),
                    subtotal=1000,
                    shipping_cost_charged=0,
                    total=1000,
                    packages=create_packages(num_parcels=shipment.boxes, package_format=PackageFormat.PARCEL),
                )
            ]
        )

    @staticmethod
    def agnostic_shipment(orders_req: CreateOrdersRequest) -> Shipment:
        order = orders_req.items[0]
        return Shipment(
            recipient=full_contact_from_rm(order.recipient),
            boxes=len(order.packages),
            shipping_date=order.planned_despatch_date.date(),
            direction=ShipDirection.OUTBOUND,
            reference=order.order_reference,
            # service=ROYAL_MAIL_SERVICES.reverse_lookup(order.packages[0].package_format_identifier),
            service=ROYAL_MAIL_SERVICES.reverse_lookup(order.postage_details.service_code),
        )

    def build_booking_request(self, shipment: Shipment) -> CreateOrdersRequest:
        shipment_rm = self.provider_shipment(shipment)
        log_obj(shipment_rm, 'Royal Mail Shipment Request')
        return shipment_rm

    def book_shipment(self, shipment: Shipment) -> ShipmentBookingResponse:
        ship = self.build_booking_request(shipment)
        resp = self.client.book_shipment(ship)
        logger.warning(f'{resp.created_orders_idents}')
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
