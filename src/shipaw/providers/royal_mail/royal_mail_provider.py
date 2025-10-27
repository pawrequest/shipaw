from typing import ClassVar, override

from loguru import logger
from royal_mail_click_and_drop import (
    CreateOrdersRequest,
    CreateOrdersResponse,
)
from royal_mail_click_and_drop.config import RoyalMailSettings
from royal_mail_click_and_drop.models.create_orders_request import CreateOrderRequest
from royal_mail_click_and_drop.models.shipment_package_request import PackageFormat
from royal_mail_click_and_drop.v2.client import RoyalMailClient
from royal_mail_click_and_drop.v2.services import RoyalMailServiceCode

from shipaw.config import ShipawSettings
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.logging import log_obj
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider_type
from shipaw.providers.royal_mail.royal_mail_funcs import (
    create_packages,
    create_postage_details,
    date_to_datetime,
    full_contact_from_rm,
    rm_billing_details_from_fc,
    rm_recipient_details_from_agnostic_fc,
)


@register_provider_type
class RoyalMailProvider(ShippingProvider):
    settings: RoyalMailSettings

    name: ClassVar[ProviderName] = ProviderName.ROYAL_MAIL
    settings_type: ClassVar[type[RoyalMailSettings]] = RoyalMailSettings
    service_codes_type: ClassVar[type[RoyalMailServiceCode]] = RoyalMailServiceCode
    default_service: ClassVar[RoyalMailServiceCode] = RoyalMailServiceCode.EXPRESS_24
    valid_directions: ClassVar[list[ShipDirection]] = [ShipDirection.OUTBOUND]

    _client: RoyalMailClient | None = None

    @override
    def is_sandbox(self) -> bool:
        # Royal mail do not have a test environment. that's fun
        return False

    @property
    @override
    def client(self) -> RoyalMailClient:
        if self._client is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self._client = RoyalMailClient(settings=self.settings)
        return self._client

    @classmethod
    @override
    def agnostic_shipment(cls, orders_req: CreateOrdersRequest) -> Shipment:
        order = orders_req.items[0]
        return Shipment(
            recipient=full_contact_from_rm(order.recipient),
            boxes=len(order.packages),
            shipping_date=order.planned_despatch_date.date(),
            direction=ShipDirection.OUTBOUND,
            reference=order.order_reference,
        )

    @override
    def provider_shipment(self, shipment: Shipment, service_code: RoyalMailServiceCode) -> CreateOrdersRequest:
        if shipment.direction != ShipDirection.OUTBOUND:
            # todo: implement inbound / dropoff
            raise NotImplementedError('only outbound shipments are supported for Royal Mail')
        shipaw_settings = ShipawSettings.from_env('SHIPAW_ENV')
        billing_details = rm_billing_details_from_fc(shipaw_settings.full_contact)
        postage_details = create_postage_details(shipment=shipment, service_code=service_code)

        return CreateOrdersRequest(
            items=[
                CreateOrderRequest(
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
            ]
        )

    def provider_shipment_request(self, shipment_request: ShipmentRequest) -> CreateOrdersRequest:
        provider_service = self.service_codes_type(shipment_request.service_code)
        shipment_rm = self.provider_shipment(shipment_request.shipment, provider_service)
        log_obj(shipment_rm, 'Royal Mail Shipment Request')
        return shipment_rm

    @override
    def book_shipment_agnostic(self, shipment_request: ShipmentRequest) -> ShipmentResponse:
        shipment = shipment_request.shipment
        provider_shipment_request = self.provider_shipment_request(shipment_request)
        resp = self.client.book_shipment(provider_shipment_request)
        logger.warning(f'BOOKED SHIPMENTS: {resp.created_orders_idents}')
        return self.build_booking_response(resp, shipment)

    def build_booking_response(self, rm_response: CreateOrdersResponse, shipment):
        """without label data"""
        if rm_response.errors_count > 0:
            raise RuntimeError()
        order = rm_response.created_orders[0]
        track_num = order.tracking_number if order.tracking_number else ''
        success = rm_response.errors_count == 0
        return ShipmentResponse(
            shipment=shipment,
            shipment_num=str(order.order_identifier),
            tracking_link=self.settings.tracking_link(track_num),
            data=rm_response.model_dump(),
            status='Success' if success else 'FAIL',
            success=success,
        )

    @override
    def fetch_label_content(self, shipment_num: str) -> bytes:
        return self.client.get_label_content(shipment_num)
