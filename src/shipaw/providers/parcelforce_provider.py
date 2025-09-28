from __future__ import annotations

from types import MappingProxyType

from pydantic import BaseModel

from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.provider import ShippingProvider, register_provider
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost

#
from parcelforce_expresslink.types import ShipmentType
from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.combadge import CreateShipmentService
from parcelforce_expresslink.request_response import ShipmentRequest, ShipmentResponse
from parcelforce_expresslink.address import (
    AddressBase,
    AddressRecipient,
    Contact as ContactPF,
)
from parcelforce_expresslink.shipment import Shipment as ShipmentPF

PARCELFORCE_SERVICES = Services(
    NEXT_DAY='SND',
    NEXT_DAY_12='S12',
    NEXT_DAY_9='09',
)

ParcelforceServiceDict = {
    'NEXT_DAY': 'SND',
    'NEXT_DAY_12': 'S12',
    'NEXT_DAY_9': '09',
}

PF_SERVICE_MAP = MappingProxyType(
    {
        'NEXT_DAY': 'SND',
        'NEXT_DAY_12': 'S12',
        'NEXT_DAY_9': '09',
    }
)


def get_pf_service_dict():
    return ParcelforceServiceDict


def address_from_agnostic[addr_type: AddressBase](
    address: AddressAgnost, cls: type[addr_type] = AddressRecipient
) -> addr_type:
    return cls(
        address_line1=address.address_lines[0],
        address_line2=address.address_lines[1] if len(address.address_lines) > 1 else None,
        address_line3=address.address_lines[2] if len(address.address_lines) > 2 else None,
        town=address.town,
        postcode=address.postcode,
        country=address.country,
    )


def address_from_agnostic_fc[addr_type: AddressBase](cls: type[addr_type], full_contact: FullContact) -> addr_type:
    return address_from_agnostic(full_contact.address, cls)


def contact_from_agnostic_fc[contact_type: ContactPF](
    cls: type[contact_type], full_contact: FullContact
) -> contact_type:
    return cls(
        business_name=full_contact.address.business_name,
        contact_name=full_contact.contact.contact_name,
        email_address=full_contact.contact.email_address,
        mobile_phone=full_contact.contact.mobile_phone,
    )


def full_contact_from_provider_contact_address(contact: ContactPF, address: AddressBase) -> FullContact:
    return FullContact(
        address=AddressAgnost(
            business_name=contact.business_name,
            address_lines=[
                line for line in [address.address_line1, address.address_line2, address.address_line3] if line
            ],
            town=address.town,
            postcode=address.postcode,
            country=address.country,
        ),
        contact=ContactAgnost(
            contact_name=contact.contact_name,
            email_address=contact.email_address,
            mobile_phone=contact.mobile_phone,
        ),
    )


def split_string_into_chunks(s, chunk_size):
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def ref_dict_from_str(ref_string: str) -> dict[str, str]:
    refs = split_string_into_chunks(ref_string, 24)
    if len(refs) > 5:
        raise ValueError('Reference too long, maximum 120 characters allowed')
    ref_nums = {f'reference_number{i}': ref for i, ref in enumerate(refs, start=1)}
    return ref_nums


def join_refs(refs: dict[str, str]) -> str:
    refs = [refs.get(f'reference_number{i+1}', '') for i in range(len(refs))]
    return ''.join(refs).strip()


def parcelforce_shipment_from_agnostic(
    shipment: ShipmentAgnost | dict,
) -> ShipmentPF | dict:
    shipment = ShipmentAgnost.model_validate(shipment)
    refs = ref_dict_from_str(shipment.reference)
    service_code = PARCELFORCE_SERVICES.lookup(shipment.service)
    ship_pf = ShipmentPF(
        **refs,
        recipient_contact=contact_from_agnostic_fc(ContactPF, shipment.recipient),
        recipient_address=address_from_agnostic_fc(AddressRecipient, shipment.recipient),
        total_number_of_parcels=shipment.boxes,
        shipping_date=shipment.shipping_date,
        service_code=service_code,
    )
    ship_pf = set_pf_shipment_direction(ship_pf)

    return ship_pf


def set_pf_shipment_direction(ship_pf):
    direction = parcelforce_shipment_direction(ship_pf)
    if direction == ShipDirection.OUTBOUND:  # todo fragile here
        pass
    elif direction == ShipDirection.DROPOFF:
        ship_pf = ship_pf.to_dropoff()
    elif direction == ShipDirection.INBOUND:
        ship_pf = ship_pf.to_inbound()
    else:
        raise ValueError(f'Wrong ShipDirection? {direction}')
    return ship_pf


def parcelforce_shipment_to_agnostic(shipment: ShipmentPF) -> ShipmentAgnost:
    return ShipmentAgnost(
        recipient=full_contact_from_provider_contact_address(shipment.recipient_contact, shipment.recipient_address),
        sender=full_contact_from_provider_contact_address(shipment.sender_contact, shipment.sender_address)
        if shipment.sender_contact and shipment.sender_address
        else None,
        boxes=shipment.total_number_of_parcels,
        shipping_date=shipment.shipping_date,
        direction=parcelforce_shipment_direction(shipment),
        reference=', '.join(
            filter(
                None,
                [
                    shipment.reference_number1,
                    shipment.reference_number2,
                    shipment.reference_number3,
                    shipment.reference_number4,
                    shipment.reference_number5,
                ],
            )
        ),
    )


def parcelforce_shipment_direction(pf_shipment: ShipmentPF):
    if pf_shipment.shipment_type == ShipmentType.DELIVERY:
        if pf_shipment.sender_address is None:
            return ShipDirection.OUTBOUND
        else:
            return ShipDirection.DROPOFF
    elif pf_shipment.shipment_type == ShipmentType.COLLECTION:
        return ShipDirection.INBOUND
    else:
        raise ValueError()


def book_ship(shipment: dict | ShipmentAgnost) -> ShipmentBookingResponse:
    shipment = ShipmentAgnost.model_validate(shipment)
    shipment_pf = parcelforce_shipment_from_agnostic(shipment)
    shipment_request_pf = ShipmentRequest(requested_shipment=shipment_pf)

    el_client = ParcelforceClient()
    authorized_shipment = shipment_request_pf.authenticate_from_settings()
    ship_req = authorized_shipment.model_dump(by_alias=True)

    back = el_client.backend(CreateShipmentService)
    resp: ShipmentResponse = back.createshipment(request=ship_req)
    resp.handle_errors()

    resp_agnost = ShipmentBookingResponse(
        shipment=shipment,
        shipment_num=resp.shipment_num,
        tracking_link=resp.tracking_link(),
        data=resp.model_dump(),
        status=resp.status,
        success=resp.success,
        label_data=el_client.get_label_content(resp.shipment_num),
    )

    return resp_agnost


# @dataclass
@register_provider
class ParcelforceShippingProvider(ShippingProvider):
    name = 'PARCELFORCE'
    service_map = PF_SERVICE_MAP

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        return parcelforce_shipment_from_agnostic(shipment)

    def agnostic_shipment(self, shipment: ShipmentPF) -> Shipment:
        return parcelforce_shipment_to_agnostic(shipment)

    def book_shipment(self, shipment: dict | ShipmentAgnost) -> ShipmentBookingResponse:
        return book_ship(shipment)

    def get_label_content(self, shipment_num: str) -> bytes:
        el_client = ParcelforceClient()
        return el_client.get_label_content(shipment_num)

