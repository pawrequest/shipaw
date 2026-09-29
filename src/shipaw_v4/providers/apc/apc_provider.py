from base64 import b64decode
from typing import ClassVar, override

from apc_hypaship.apc_client import APCClient
from apc_hypaship.config import APCSettings
from apc_hypaship.models.request.services import APCServiceCode
from apc_hypaship.models.response.common import APCException
from apc_hypaship.models.response.resp import BookingResponse

from shipaw.providers.apc.apc_funcs import to_apc_shipment
from shipaw.providers.registry import register_provider_type
from shipaw.models.requests import ShipmentRequest
from shipaw.models.responses import CompletedShipmentResponse, ShipmentResponse
from shipaw.logging import log_obj
from shipaw.utils.consts_enums import PackageFormat, ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost
from shipaw.providers.apc.response import errored_booking
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.utils.funcs import wait_for


@register_provider_type
class APCShippingProvider(ShippingProvider):
    settings: APCSettings

    name: ClassVar[ProviderName] = ProviderName.APC

    settings_type: ClassVar[type[APCSettings]] = APCSettings
    service_codes_type: ClassVar[type[APCServiceCode]] = APCServiceCode
    default_service: ClassVar[APCServiceCode] = APCServiceCode.PARCEL_1600
    _client: APCClient | None = None

    available_services = {
        ShipDirection.OUTBOUND: [APCServiceCode.PARCEL_1600, APCServiceCode.SATURDAY_PARCEL_1200],
        ShipDirection.INBOUND: [APCServiceCode.PARCEL_1600],
    }

    valid_direction_formats = {
        ShipDirection.OUTBOUND: [PackageFormat.PARCEL],
        ShipDirection.INBOUND: [PackageFormat.PARCEL],
        ShipDirection.DROPOFF: [PackageFormat.PARCEL],
    }

    @override
    def is_sandbox(self) -> bool:
        return 'training' in self.settings.base_url.lower()

    @property
    def client(self) -> APCClient:
        if self._client is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self._client = APCClient(settings=self.settings)
        return self._client

    @override
    def book_shipment_request(self, shipment_request: ShipmentRequest) -> 'ShipmentResponse':
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        # request_json = self.build_request_json(shipment)
        apc_response: BookingResponse | None = None
        apc_service_code = self.service_codes_type(shipment_request.service_code)
        shipment = shipment_request.shipment
        apc_shipment = to_apc_shipment(shipment, apc_service_code)
        log_obj(apc_shipment, 'APC Shipment Request')
        try:
            apc_response: BookingResponse = self.client.fetch_book_shipment(apc_shipment)
            label_data = wait_for(self.fetch_label_content, apc_response.orders.order.order_number, wait_for_type=bytes)
            return self.build_response(apc_response, shipment, label_data)
        except APCException as e:
            if apc_response:
                return errored_booking(shipment, apc_response)
            else:
                raise e

    def fetch_label_content(self, shipment_num: str) -> bytes:
        labl = self.client.fetch_label(shipment_num)
        return b64decode(labl.content)

    @staticmethod
    def build_response(resp: BookingResponse, shipment: ShipmentAgnost, label_data: bytes) -> CompletedShipmentResponse:
        orders = resp.orders
        order = orders.order
        return CompletedShipmentResponse(
            label_data=label_data,
            shipment=shipment,
            shipment_num=order.order_number,
            shipment_numbers=[order.order_number],
            tracking_links=[r'https://apc.hypaship.com/app/shared/customerordersoverview/index#search_form'],
            data=resp.model_dump(mode='json'),
            status=(str(orders.messages.code)),
            success=(orders.messages.code == 'SUCCESS'),
        )
