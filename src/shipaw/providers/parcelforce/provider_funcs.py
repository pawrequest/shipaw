from __future__ import annotations

from typing import override, cast

from parcelforce_expresslink.address import AddressBase, AddressRecipient, Contact as ContactPF
from parcelforce_expresslink.services import ServiceCode
from parcelforce_expresslink.shipment import Shipment as ShipmentPF
from parcelforce_expresslink.types import ShipmentType

from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost


class ParcelforceServices(Services):
    NEXT_DAY: ServiceCode = 'SND'
    NEXT_DAY_12: ServiceCode = 'S12'
    NEXT_DAY_9: ServiceCode = '09'

    @override
    def lookup(self, agnostic_name: str) -> ServiceCode:
        return ServiceCode(super().lookup(agnostic_name))


PARCELFORCE_SERVICES = ParcelforceServices(
    NEXT_DAY='SND',
    NEXT_DAY_12='S12',
    NEXT_DAY_9='09',
)


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


# def parcelforce_shipment_from_agnostic(shipment: ShipmentAgnost | dict, contract_number: str) -> ShipmentPF | dict:
#     ship_pf = ShipmentPF(
#         **ref_dict_from_str(shipment.reference),
#         recipient_contact=contact_from_agnostic_fc(ContactPF, shipment.recipient),
#         recipient_address=address_from_agnostic_fc(AddressRecipient, shipment.recipient),
#         total_number_of_parcels=shipment.boxes,
#         shipping_date=shipment.shipping_date,
#         service_code=PARCELFORCE_SERVICES.lookup(shipment.service),
#         contract_number=contract_number,
#     )
#     return shipment_directed(ship_pf)


def parcelforce_shipment_to_agnostic(shipment: ShipmentPF) -> ShipmentAgnost:
    return ShipmentAgnost(
        recipient=full_contact_from_provider_contact_address(shipment.recipient_contact, shipment.recipient_address),
        sender=full_contact_from_provider_contact_address(shipment.sender_contact, shipment.sender_address)
        if shipment.sender_contact and shipment.sender_address
        else None,
        boxes=shipment.total_number_of_parcels,
        shipping_date=shipment.shipping_date,
        direction=shipment_direction(shipment),
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


# def book_shipment(shipment: ShipmentAgnost) -> ShipmentBookingResponse:
#     shipment_pf = parcelforce_shipment_from_agnostic(shipment)
#     shipment_request_pf = ShipmentRequest(requested_shipment=shipment_pf)
#
#     el_client = ParcelforceClient.from_env()
#     authorized_shipment = shipment_request_pf.authenticate_from_settings()
#     ship_req = authorized_shipment.model_dump(by_alias=True)
#
#     back = el_client.backend(CreateShipmentService)
#     pf_response: ShipmentResponse = back.createshipment(request=ship_req)
#     pf_response.handle_errors()
#
#     resp_agnost = ShipmentBookingResponse(
#         shipment=shipment,
#         shipment_num=pf_response.shipment_num,
#         tracking_link=pf_response.tracking_link(),
#         data=pf_response.model_dump(),
#         status=pf_response.status,
#         success=pf_response.success,
#         label_data=el_client.get_label_content(pf_response.shipment_num),
#     )
#
#     return resp_agnost


def shipment_direction(shipment: ShipmentPF) -> ShipDirection:
    if shipment.shipment_type == ShipmentType.DELIVERY:
        if shipment.sender_address is None:
            return ShipDirection.OUTBOUND
        else:
            return ShipDirection.DROPOFF
    elif shipment.shipment_type == ShipmentType.COLLECTION:
        return ShipDirection.INBOUND
    else:
        raise ValueError()


def shipment_directed(shipment: ShipmentPF) -> ShipmentPF:
    return convert_shipment(shipment, shipment_direction(shipment))