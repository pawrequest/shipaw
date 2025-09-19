from __future__ import annotations

from shipaw.agnostic.providers import ConvertMode, ShippingProvider, maybe_dict
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.ship_types import ShipDirection
from shipaw.agnostic.shipment import FullContact, Shipment as ShipmentAgnost
from shipaw.parcelforce.client import ELClient
from shipaw.parcelforce.combadge import CreateShipmentService
from shipaw.parcelforce.models import AddressRecipient
from shipaw.parcelforce.msg import ShipmentRequest, ShipmentResponse, log_booked_shipment
from shipaw.parcelforce.services import ParcelforceServiceDict
from shipaw.parcelforce.shipment import (
    Shipment as PFShipment,
    parcelforce_address,
    parcelforce_contact,
    parcelforce_shipment,
)
from shipaw.parcelforce.top import Contact as ContactPF


class ParcelforceProvider(ShippingProvider):
    service_dict: ServiceDict = ParcelforceServiceDict

    @staticmethod
    def convert_contact(
        full_contact: FullContact,
        mode: ConvertMode = 'dict',
    ) -> ContactPF | dict:
        obj = ContactPF(
            business_name=full_contact.contact.business_name,
            mobile_phone=full_contact.contact.mobile_phone,
            email_address=full_contact.contact.email_address,
            contact_name=full_contact.contact.contact_name,
        )
        return maybe_dict(obj, mode)

    @staticmethod
    def convert_address(
        full_contact: FullContact,
        mode: ConvertMode = 'dict',
    ) -> AddressRecipient | dict:
        obj = AddressRecipient(
            address_line1=full_contact.address.address_lines[0],
            address_line2=full_contact.address.address_lines[1],
            address_line3=full_contact.address.address_lines[2],
            town=full_contact.address.town,
            postcode=full_contact.address.postcode,
        )
        return maybe_dict(obj, mode)

    @staticmethod
    def convert_shipment(
        shipment: ShipmentAgnost | dict,
        mode: ConvertMode = 'dict',
    ) -> PFShipment | dict:
        if isinstance(shipment, dict):
            shipment = ShipmentAgnost.model_validate(shipment)
        ref_nums = {'reference_number' + i: ref for ref, i in enumerate(shipment.references)}
        service_code = ParcelforceProvider.service_dict[shipment.service.upper()]  # type: ignore (literals)
        ship = PFShipment(
            **ref_nums,
            recipient_contact=parcelforce_contact(shipment.recipient_contact),
            recipient_address=parcelforce_address(shipment.recipient_address),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=service_code,
        )
        match shipment.direction:
            case ShipDirection.OUTBOUND:
                res = PFShipment.model_validate(ship)
            case ShipDirection.INBOUND:
                res = ship.to_collection()
            case ShipDirection.DROPOFF:
                res = ship.to_dropoff()
            case _:
                raise ValueError('Invalid Ship Direction')

        return maybe_dict(res, mode)

    # @staticmethod
    # def make_shipment_dict(shipment: ShipmentAgnost) -> dict:
    #     return ParcelforceProvider.convert_shipment(shipment).model_dump(mode='json')

    def send_request(self, shipment: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        shipment = ShipmentAgnost.model_validate(shipment)
        shipment_pf = parcelforce_shipment(shipment)
        shipment_request = ShipmentRequest(requested_shipment=shipment_pf)
        el_client = ELClient()
        authorized_shipment = shipment_request.authenticated(el_client.settings.auth())
        back = el_client.backend(CreateShipmentService)
        resp: ShipmentResponse = back.createshipment(request=authorized_shipment.model_dump(by_alias=True))
        log_booked_shipment(shipment_request, resp)
        resp.handle_errors()
        return ShipmentBookingResponseAgnost(shipment_num=resp.shipment_num)

    def handle_response(self, response: ShipmentBookingResponseAgnost) -> bool:
        raise NotImplementedError
