import base64
from typing import ClassVar, override

from royal_mail_combined import RoyalMailClient
from royal_mail_combined.config import RoyalMailSettingsGlobal
from royal_mail_combined.core.consts_types import RoyalMailServiceCodes

from shipaw.models.requests import ShipmentRequest
from shipaw.models.responses import CompletedShipmentResponse
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider_type
from shipaw.providers.royal_mail.royal_mail_funcs import (
    booking_response_inbound,
    booking_response_outbound,
    create_remote_shipment,
    outbound_shipment,
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
    available_services = {
        ShipDirection.OUTBOUND: [
            RoyalMailServiceCodes.TRACKED_24,
            RoyalMailServiceCodes.EXPRESS_24,
            RoyalMailServiceCodes.SPECIAL_1PM,
            RoyalMailServiceCodes.EXPRESS_10,
            RoyalMailServiceCodes.EXPRESS_AM,
        ],
        ShipDirection.INBOUND: [RoyalMailServiceCodes.TRACKED_24_RTN],
        ShipDirection.DROPOFF: [RoyalMailServiceCodes.TRACKED_24_RTN],
        ShipDirection.THIRD_PARTY: [RoyalMailServiceCodes.TRACKED_24_RTN],
    }

    valid_direction_formats = {
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

    @override
    def book_shipment_request(self, shipment_request: ShipmentRequest) -> CompletedShipmentResponse:
        shipment = shipment_request.shipment
        service = self.service_codes_type(shipment_request.service_code)
        shipdir = shipment_request.shipment.direction
        if shipdir == ShipDirection.OUTBOUND:
            return self._book_outbound(service, shipment)
        else:
            return self._book_remote(service, shipment)

    def _book_remote(self, service: RoyalMailServiceCodes, shipment: Shipment) -> CompletedShipmentResponse:
        returns_container = create_remote_shipment(shipment, service)
        if shipment.direction in [ShipDirection.INBOUND, ShipDirection.THIRD_PARTY]:
            resp = self.client.book_inbound_with_collection(returns_container, collection_date=shipment.shipping_date)
        elif shipment.direction == ShipDirection.DROPOFF:
            resp = self.client.book_inbound_shipping(returns_container)
        else:
            raise ValueError(f'Invalid shipment direction "{shipment.direction}"')
        labels_bytes = [base64.b64decode(order.label) for order in resp.created_orders]
        combined_label_bytes = merge_pdf_bytes(labels_bytes)
        return booking_response_inbound(resp, shipment, combined_label_bytes)

    def _book_outbound(self, service: RoyalMailServiceCodes, shipment: Shipment) -> CompletedShipmentResponse:
        orders_request = outbound_shipment(shipment, service)
        booking_response = self.client.book_outbound(orders_request)
        if booking_response.errors_count > 0:
            print_response_errors(booking_response)
        label_data: bytearray = self.client.get_label_data(booking_response.success_idents_str)
        fetched_response = self.client.fetch_specific_orders(booking_response.success_idents_str)
        return booking_response_outbound(fetched_response, shipment, label_data)
