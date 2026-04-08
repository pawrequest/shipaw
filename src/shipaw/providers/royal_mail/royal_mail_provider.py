import base64
from typing import ClassVar, override

from royal_mail_combined import RoyalMailClient
from royal_mail_combined.click_and_drop_api.models import (
    CreateOrderRequest,
    CreateOrdersRequest,
)
from royal_mail_combined.click_and_drop_api.models.return_models import ReturnRequestContainer
from royal_mail_combined.config import RoyalMailSettingsGlobal
from royal_mail_combined.core.consts_types import RoyalMailServiceCodes

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import CompletedShipmentResponse
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider_type
from shipaw.providers.royal_mail.royal_mail_funcs import (
    build_booking_response_inbound,
    build_booking_response_outbound_f_fetched,
    full_contact_from_rm,
    inbound_shipment_from_agnostic,
    outbound_shipment_from_agnostic,
    print_response_errors,
)
from shipaw.utils.consts_enums import PackageFormat, ShipDirection
from shipaw.utils.label_file import merge_pdf_bytes


@register_provider_type
class RoyalMailProvider(ShippingProvider):
    settings: RoyalMailSettingsGlobal

    name: ClassVar[ProviderName] = ProviderName.ROYAL_MAIL
    settings_type: ClassVar[type[RoyalMailSettingsGlobal]] = RoyalMailSettingsGlobal
    service_codes_type: ClassVar[type[RoyalMailServiceCodes]] = RoyalMailServiceCodes

    valid_directions: ClassVar[list[ShipDirection]] = [
        ShipDirection.OUTBOUND,
        ShipDirection.INBOUND,
        ShipDirection.DROPOFF,
    ]

    default_service: ClassVar[RoyalMailServiceCodes] = RoyalMailServiceCodes.EXPRESS_24
    valid_direction_services: ClassVar[dict[ShipDirection, list[RoyalMailServiceCodes]]] = {
        ShipDirection.OUTBOUND: [
            RoyalMailServiceCodes.TRACKED_24,
            RoyalMailServiceCodes.EXPRESS_24,
            RoyalMailServiceCodes.SPECIAL_1PM,
            RoyalMailServiceCodes.EXPRESS_10,
            RoyalMailServiceCodes.EXPRESS_AM,
        ],
        ShipDirection.INBOUND: [RoyalMailServiceCodes.TRACKED_24_RTN],
        ShipDirection.DROPOFF: [RoyalMailServiceCodes.TRACKED_24_RTN],
    }

    valid_direction_formats: ClassVar[dict[ShipDirection, list[PackageFormat]]] = {
        ShipDirection.OUTBOUND: [PackageFormat.PARCEL, PackageFormat.SMALL_PARCEL],
        ShipDirection.INBOUND: [PackageFormat.PARCEL],
        ShipDirection.DROPOFF: [PackageFormat.PARCEL],
    }

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
    def provider_shipment(
        self, shipment: Shipment, service_code: RoyalMailServiceCodes
    ) -> CreateOrderRequest | ReturnRequestContainer:
        provider_service = self.service_codes_type(service_code)
        match shipment.direction:
            case ShipDirection.OUTBOUND:
                return outbound_shipment_from_agnostic(shipment, provider_service)
            case ShipDirection.DROPOFF | ShipDirection.INBOUND:
                return inbound_shipment_from_agnostic(shipment, provider_service)

    @override
    def book_shipment_request(self, shipment_request: ShipmentRequest) -> CompletedShipmentResponse:
        shipment = shipment_request.shipment
        service = self.service_codes_type(shipment_request.service_code)
        shipdir = shipment_request.shipment.direction
        if shipdir == ShipDirection.OUTBOUND:
            return self._book_outbound(service, shipment)
        elif shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
            return self._book_inbound_or_dropoff(service, shipment)
        else:
            raise ValueError(f'Invalid shipment direction "{shipdir}"')

    def _book_inbound_or_dropoff(self, service: RoyalMailServiceCodes, shipment: Shipment) -> CompletedShipmentResponse:
        returns_container = inbound_shipment_from_agnostic(shipment, service)
        if shipment.direction == ShipDirection.INBOUND:
            resp = self.client.book_inbound_collection(returns_container, collection_date=shipment.shipping_date)
        else:
            resp = self.client.book_inbound_dropoff(returns_container)
        labels_bytes = [base64.b64decode(order.label) for order in resp.created_orders]
        combined_label_bytes = merge_pdf_bytes(labels_bytes)
        return build_booking_response_inbound(resp, shipment, combined_label_bytes)

    def _book_outbound(self, service: RoyalMailServiceCodes, shipment: Shipment) -> CompletedShipmentResponse:
        order_create = outbound_shipment_from_agnostic(shipment, service)
        booking_response = self.client.book_outbound(order_create)
        if booking_response.errors_count > 0:
            print_response_errors(booking_response)
        label_data: bytearray = self.client.get_label_data(booking_response.success_idents_str)
        fetched_response = self.client.fetch_specific_orders(booking_response.success_idents_str)
        return build_booking_response_outbound_f_fetched(fetched_response, shipment, label_data)
        # return build_booking_response_outbound(resp, shipment, label_data)
