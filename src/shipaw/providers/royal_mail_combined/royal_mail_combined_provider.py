from pprint import pformat
from typing import ClassVar, override

from loguru import logger
from royal_mail_combined import RoyalMailClient
from royal_mail_combined.click_and_drop_api.models import (
    CreateOrderRequest,
    CreateOrdersRequest,
    CreateOrdersResponse,
)
from royal_mail_combined.click_and_drop_api.models.return_models import ReturnRequestContainer, ReturnResponseContainer
from royal_mail_combined.config import RoyalMailSettingsGlobal
from royal_mail_combined.converters_no_import import tracking_link
from royal_mail_combined.core.consts_types import RoyalMailServiceCodes

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider_type
from shipaw.providers.royal_mail_combined.royal_mail_combined_funcs import (
    full_contact_from_rm,
    inbound_shipment_from_agnostic,
    outbound_shipment_from_agnostic,
)


def build_booking_response_inbound(rm_response: ReturnResponseContainer, shipment: Shipment):
    ids = ';'.join([order.shipment.unique_item_id for order in rm_response.created_orders])
    links = ';'.join([order.shipment.tracking_number for order in rm_response.created_orders])

    return ShipmentResponse(
        shipment=shipment,
        shipment_num=ids,
        tracking_link=links,
        data=rm_response.model_dump(),
        status='Success',
        success=True,
    )


def print_response_errors(rm_response: CreateOrdersResponse):
    logger.error(f'Errors booking outbound shipment: {pformat(rm_response.failed_orders, indent=2, width=120)}')


@register_provider_type
class RoyalMailProvider(ShippingProvider):
    settings: RoyalMailSettingsGlobal

    name: ClassVar[ProviderName] = ProviderName.ROYAL_MAIL
    settings_type: ClassVar[type[RoyalMailSettingsGlobal]] = RoyalMailSettingsGlobal
    service_codes_type: ClassVar[type[RoyalMailServiceCodes]] = RoyalMailServiceCodes
    default_service: ClassVar[RoyalMailServiceCodes] = RoyalMailServiceCodes.TRACKED_24
    valid_directions: ClassVar[list[ShipDirection]] = [
        ShipDirection.OUTBOUND,
        ShipDirection.INBOUND,
        ShipDirection.DROPOFF,
    ]

    valid_direction_services = {
        ShipDirection.OUTBOUND: {RoyalMailServiceCodes.TRACKED_24, RoyalMailServiceCodes.EXPRESS_24},
        ShipDirection.INBOUND: {RoyalMailServiceCodes.TRACKED_24_RTN},
        ShipDirection.DROPOFF: {RoyalMailServiceCodes.TRACKED_24_RTN},
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

        if shipment.direction == ShipDirection.OUTBOUND:
            return outbound_shipment_from_agnostic(shipment, provider_service)
        else:
            return inbound_shipment_from_agnostic(shipment, provider_service)

    @override
    def book_shipment_agnostic(self, shipment_request: ShipmentRequest) -> ShipmentResponse:
        shipment = shipment_request.shipment
        service = self.service_codes_type(shipment_request.service_code)

        resp = None
        match shipment_request.shipment.direction:
            case ShipDirection.OUTBOUND:
                order_create = outbound_shipment_from_agnostic(shipment, service)
                resp = self.client.book_outbound_shipment(order_create)
            case ShipDirection.DROPOFF:
                return_req_container = inbound_shipment_from_agnostic(shipment, service)
                resp = self.client.book_inbound_shipment(return_req_container)

            case ShipDirection.INBOUND:
                return_req_container = inbound_shipment_from_agnostic(shipment, service)
                resp = self.client.book_inbound_shipment_with_collection(
                    return_req_container, collection_date=shipment.shipping_date
                )
            case _:
                raise ValueError('Bad ShipDirection')

        if isinstance(resp, CreateOrdersResponse):
            built_response = self.build_booking_response_outbound(resp, shipment)
        elif isinstance(resp, ReturnResponseContainer):
            built_response = build_booking_response_inbound(resp, shipment)
        else:
            raise ValueError(f'Unexpected response type {type(resp)} from booking shipment')

        return built_response

    def build_booking_response_outbound(self, rm_response: CreateOrdersResponse, shipment: Shipment):
        if rm_response.errors_count > 0:
            print_response_errors(rm_response)

        success_idents = rm_response.success_idents
        labels = self.client.get_label_data(success_idents)
        fetched = self.client.fetch_specific_orders(success_idents)
        tracking_numbers = [order.tracking_number for order in fetched]
        tracking_links = [tracking_link(_) for _ in tracking_numbers]
        success = rm_response.errors_count == 0
        res = ShipmentResponse(
            label_data=labels,
            shipment=shipment,
            shipment_num=success_idents,
            tracking_link=', '.join(tracking_links),
            data=fetched.model_dump(),
            status='Success' if success else 'FAIL',
            success=success,
        )
        return res

    @override
    def fetch_label_content(self, shipment_num: str) -> bytes:
        return self.client.get_label_data(shipment_num)
