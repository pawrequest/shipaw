from __future__ import annotations

from typing import ClassVar, override

from parcelforce_expresslink.address import AddressRecipient, Contact as ContactPF
from parcelforce_expresslink.combadge import CreateShipmentService
from parcelforce_expresslink.request_response import ShipmentRequest, ShipmentResponse as ShipmentResponsePF

#
from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.shipment import Shipment as ShipmentPF

from shipaw.models.services import Services
from shipaw.providers.providers import ShippingProvider, register_provider
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost
from shipaw.providers.parcelforce.provider_funcs import (
    PARCELFORCE_SERVICES,
    address_from_agnostic_fc,
    shipment_directed,
    contact_from_agnostic_fc,
    parcelforce_shipment_to_agnostic,
    ref_dict_from_str,
    ParcelforceServices,
)


# @dataclass
@register_provider
class ParcelforceShippingProvider(ShippingProvider):
    name = 'PARCELFORCE'
    services: ClassVar[ParcelforceServices] = PARCELFORCE_SERVICES
    settings_type: ClassVar[type[ParcelforceSettings]] = ParcelforceSettings
    settings: ParcelforceSettings | None = None
    _client: ParcelforceClient | None = None

    @property
    def client(self) -> ParcelforceClient:
        if self._client is None:
            if self.settings is None:
                raise ValueError('Settings must be set before using the client')
            self._client = ParcelforceClient(settings=self.settings)
        return self._client

    @override
    def provider_shipment(self, shipment: Shipment) -> ShipmentPF:
        shipment = ShipmentAgnost.model_validate(shipment)
        ship_pf = ShipmentPF(
            **ref_dict_from_str(shipment.reference),
            recipient_contact=contact_from_agnostic_fc(ContactPF, shipment.recipient),
            recipient_address=address_from_agnostic_fc(AddressRecipient, shipment.recipient),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=self.services.lookup(shipment.service),
            contract_number=self.settings.pf_contract_num_1,
        )
        return shipment_directed(ship_pf)

    @override
    def agnostic_shipment(self, shipment: ShipmentPF) -> Shipment:
        return parcelforce_shipment_to_agnostic(shipment)

    def build_booking_request(self, shipment: ShipmentAgnost) -> ShipmentRequest:
        shipment_pf = self.provider_shipment(shipment)
        shipment_request_pf = ShipmentRequest(requested_shipment=shipment_pf)
        authorized_shipment = shipment_request_pf.authenticate(*self.settings.get_auth_secrets())
        return authorized_shipment

    @override
    def book_shipment(self, shipment: ShipmentAgnost) -> ShipmentBookingResponse:
        ship_req = self.build_booking_request(shipment)
        pf_response = self.make_pf_book_request(ship_req)
        return self.build_booking_response(pf_response, shipment)

    def build_booking_response(self, pf_response, shipment):
        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=pf_response.shipment_num,
            tracking_link=self.settings.tracking_link(pf_response.shipment_num),
            data=pf_response.model_dump(),
            status=pf_response.status,
            success=pf_response.success,
            label_data=self.get_label_content(pf_response.shipment_num),
        )

    def make_pf_book_request(self, ship_req):
        back = self.client.backend(CreateShipmentService)
        pf_response: ShipmentResponsePF = back.createshipment(request=ship_req)
        pf_response.handle_errors()
        return pf_response

    @override
    def get_label_content(self, shipment_num: str) -> bytes:
        return self.client.get_label_content(shipment_num)

