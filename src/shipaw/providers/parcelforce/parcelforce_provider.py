from __future__ import annotations

from typing import ClassVar, override

from parcelforce_expresslink.client.combadge import CreateShipmentService
from parcelforce_expresslink.client.request_response import (
    ShipmentRequest as ShipmentRequestParcelforce,
    ShipmentResponse as ShipmentResponsePF,
)

#
from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.expresslink_client import ParcelforceClient
from parcelforce_expresslink.models.address import (
    AddressRecipient,
)
from parcelforce_expresslink.models.contact import Contact as ContactPF
from parcelforce_expresslink.models.services import ServiceCode
from parcelforce_expresslink.models.shipment import Shipment as ShipmentPF

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.logging import log_obj
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost
from shipaw.providers.parcelforce.parcelforce_funcs import (
    address_from_agnostic_fc,
    contact_from_agnostic_fc,
    convert_shipment_by_direction,
    parcelforce_shipment_to_agnostic,
    ref_dict_from_str,
)
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import register_provider_type


@register_provider_type
class ParcelforceShippingProvider(ShippingProvider):
    name = ProviderName.PARCELFORCE
    settings_type: ClassVar[type[ParcelforceSettings]] = ParcelforceSettings
    settings: ParcelforceSettings
    service_codes_type: ClassVar[type[ServiceCode]] = ServiceCode
    default_service: ClassVar[ServiceCode] = ServiceCode.EXPRESS24
    _client: ParcelforceClient | None = None

    valid_directions: ClassVar[list[ShipDirection]] = [
        ShipDirection.OUTBOUND,
        ShipDirection.INBOUND,
        ShipDirection.DROPOFF,
    ]

    def is_sandbox(self) -> bool:
        return 'test' in self.settings.pf_endpoint.lower()

    @property
    def client(self) -> ParcelforceClient:
        if self._client is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self._client = ParcelforceClient(settings=self.settings)
        return self._client

    @override
    def provider_shipment(self, shipment: ShipmentAgnost, service_code: ServiceCode) -> ShipmentPF:
        ship_pf = ShipmentPF(
            **ref_dict_from_str(shipment.reference),
            recipient_contact=contact_from_agnostic_fc(ContactPF, shipment.recipient),
            recipient_address=address_from_agnostic_fc(AddressRecipient, shipment.recipient),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=service_code,
            contract_number=self.settings.pf_contract_num_1,
            print_own_label=shipment.own_label,
        )
        convert_shipment_by_direction(ship_pf, shipment)
        return ship_pf

    @override
    def agnostic_shipment(self, shipment: ShipmentPF) -> Shipment:
        return parcelforce_shipment_to_agnostic(shipment)

    def provider_shipment_request(self, shipment_request: ShipmentRequest) -> ShipmentRequestParcelforce:
        service_code = ServiceCode(shipment_request.service_code)
        provider_shipment = self.provider_shipment(shipment_request.shipment, service_code=service_code)
        provider_shipment_request = ShipmentRequestParcelforce(requested_shipment=provider_shipment)
        log_obj(provider_shipment_request, 'ParcelForce Shipment Request')
        authorized_shipment = provider_shipment_request.authenticate(*self.settings.get_auth_secrets())
        return authorized_shipment

    @override
    def book_shipment_agnostic(self, shipment_request: ShipmentRequest) -> ShipmentResponse:
        ship_req = self.provider_shipment_request(shipment_request)
        pf_response = self.book_shipment_provider(ship_req)
        return self.build_booking_response(pf_response, shipment_request.shipment)

    def build_booking_response(self, pf_response, shipment):
        """without label data"""
        return ShipmentResponse(
            shipment=shipment,
            shipment_num=pf_response.shipment_num,
            tracking_link=self.settings.tracking_link(pf_response.shipment_num),
            data=pf_response.model_dump(),
            status=pf_response.status,
            success=pf_response.success,
        )

    def book_shipment_provider(self, ship_req: ShipmentRequestParcelforce):
        back = self.client.backend(CreateShipmentService)
        pf_response: ShipmentResponsePF = back.createshipment(request=ship_req)
        pf_response.handle_errors()
        return pf_response

    @override
    def fetch_label_content(self, shipment_num: str) -> bytes:
        return self.client.get_label_content(shipment_num)
