from __future__ import annotations


from parcelforce_expresslink.models.address import AddressBase, AddressRecipient, AddressSender
from parcelforce_expresslink.models.contact import Contact as ContactPF, ContactSender
from parcelforce_expresslink.models.shipment import Shipment as ShipmentPF

from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost


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


def parcelforce_full_contact(contact: ContactPF, address: AddressBase) -> FullContact:
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


def parcelforce_shipment_to_agnostic(shipment: ShipmentPF) -> ShipmentAgnost:
    sender = None
    if shipment.direction == ShipDirection.INBOUND:
        address = shipment.collection_info.collection_address
        contact = shipment.collection_info.collection_contact
        sender = parcelforce_full_contact(contact, address)
    elif shipment.direction == ShipDirection.DROPOFF:
        address = shipment.sender_address
        contact = shipment.sender_contact
        sender = parcelforce_full_contact(contact, address)

    return ShipmentAgnost(
        recipient=parcelforce_full_contact(shipment.recipient_contact, shipment.recipient_address),
        sender=sender,
        boxes=shipment.total_number_of_parcels,
        shipping_date=shipment.shipping_date,
        direction=shipment.direction,
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


def add_sender(ship_pf, shipment):
    ship_pf.sender_contact = contact_from_agnostic_fc(ContactSender, shipment.sender)
    ship_pf.sender_address = address_from_agnostic_fc(AddressSender, shipment.sender)


def convert_shipment_by_direction(ship_pf: ShipmentPF, shipment: ShipmentAgnost):
    if shipment.direction == ShipDirection.OUTBOUND:
        return
    add_sender(ship_pf, shipment)  # make dropoff
    if shipment.direction == ShipDirection.INBOUND:
        ship_pf.change_sender_to_collection()  # make inbound collection


def join_refs(refs: dict[str, str]) -> str:
    refs = [refs.get(f'reference_number{i + 1}', '') for i in range(len(refs))]
    return ''.join(refs).strip()
