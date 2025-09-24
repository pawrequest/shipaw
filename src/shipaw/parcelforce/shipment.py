import datetime as dt
from pathlib import Path
from typing import Self

from pydantic import constr

from shipaw.agnostic.address import Address as AddressAgnost
from shipaw.agnostic.ship_types import (
    DropOffInd,
    ShipDirection,
    ShipmentType,
)
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.parcelforce.address import (
    AddressCollection,
    AddressRecipient as PFAddress,
    AddressSender,
    Contact,
    ContactCollection,
    ContactSender,
)
from shipaw.parcelforce.config import pf_settings
from shipaw.parcelforce.lists import HazardousGoods
from shipaw.parcelforce.models import AddressRecipient, DeliveryOptions
from shipaw.parcelforce.services import ParcelforceServiceDict, ServiceCode
from shipaw.parcelforce.shared import DateTimeRange, Enhancement, PFBaseModel
from shipaw.parcelforce.top import CollectionInfo


class ShipmentReferenceFields(PFBaseModel):
    reference_number1: constr(max_length=24) | None = None
    reference_number2: constr(max_length=24) | None = None
    reference_number3: constr(max_length=24) | None = None
    reference_number4: constr(max_length=24) | None = None
    reference_number5: constr(max_length=24) | None = None
    special_instructions1: constr(max_length=25) | None = None
    special_instructions2: constr(max_length=25) | None = None
    special_instructions3: constr(max_length=25) | None = None
    special_instructions4: constr(max_length=25) | None = None


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


class Shipment(ShipmentReferenceFields):
    shipment_type: ShipmentType = ShipmentType.DELIVERY
    # from settings
    department_id: int = pf_settings().department_id
    contract_number: str = pf_settings().pf_contract_num_1

    recipient_contact: Contact
    recipient_address: AddressRecipient | AddressCollection
    total_number_of_parcels: int = 1
    shipping_date: dt.date
    service_code: ServiceCode = ServiceCode.EXPRESS24

    # subclasses
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = None
    sender_contact: ContactSender | None = None
    sender_address: AddressSender | None = None

    _label_file: Path | None = None  # must be private for xml serialization to exclude / expresslink to work

    # currently unused (but required by expresslink)
    enhancement: Enhancement | None = None
    delivery_options: DeliveryOptions | None = None
    hazardous_goods: HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: DropOffInd | None = None

    @classmethod
    def from_generic(
        cls,
        shipment: ShipmentAgnost | dict,
    ) -> Self | dict:
        shipment = ShipmentAgnost.model_validate(shipment)
        refs = ref_dict_from_str(shipment.reference)
        ref_nums = {'reference_number' + i: ref for ref, i in enumerate(refs)}
        service_code = ParcelforceServiceDict[shipment.service.upper()]
        ship_pf = cls(
            **ref_nums,
            recipient_contact=Contact.from_generic(
                shipment.recipient.contact, business_name=shipment.recipient.address.business_name
            ),
            recipient_address=AddressRecipient.from_generic(shipment.recipient.address),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=service_code,
        )

        if shipment.sender:
            ship_pf = cls.to_inbound(ship_pf, shipment)

        return ship_pf

    @classmethod
    def to_inbound(cls, ship_pf: Self, shipment: ShipmentAgnost) -> Self:
        """Modify ship_pf in place to be an inbound shipment / dropoff"""
        if shipment.direction not in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
            raise ValueError('Inbound shipment must be INBOUND or DROPOFF')

        contact = Contact.from_generic(shipment.sender.contact, business_name=shipment.sender.address.business_name)
        sender_address = AddressRecipient.from_generic(shipment.sender.address)
        if shipment.direction == ShipDirection.INBOUND:
            ship_pf.shipment_type = ShipmentType.COLLECTION
            ship_pf.print_own_label = True
            ship_pf.collection_info = CollectionInfo(
                collection_contact=ContactCollection(**contact.model_dump(exclude={'notifications'})),
                collection_address=sender_address,
                collection_time=DateTimeRange.null_times_from_date(ship_pf.shipping_date),
            )
        elif shipment.direction == ShipDirection.DROPOFF:
            ship_pf.sender_contact = ContactSender(
                **contact.model_dump(exclude={'notifications'}),
            )
            ship_pf.sender_address = sender_address
        return ship_pf

    def to_generic(self) -> ShipmentAgnost:
        raise NotImplementedError('to_generic not implemented for Parcelforce Shipment')

    def __str__(self):
        return f'{self.shipment_type} {f'from {self.collection_info.collection_address.address_line1} ' if self.collection_info else ''}to {self.recipient_address.address_line1}'


class ShipmentAwayCollection(Shipment):
    shipment_type: ShipmentType = ShipmentType.COLLECTION
    print_own_label: bool = True
    collection_info: CollectionInfo

    @property
    def notifications_str(self) -> str:
        return self.recipient_contact.notifications_str + self.collection_info.collection_contact.notifications_str


class ShipmentAwayDropoff(Shipment):
    sender_contact: ContactSender
    sender_address: AddressSender


def parcelforce_contact(contact: Contact) -> Contact:
    return Contact(
        business_name=contact.business_name,
        mobile_phone=contact.mobile_phone,
        email_address=contact.email_address,
        contact_name=contact.contact_name,
    )


def parcelforce_address(address: AddressAgnost) -> PFAddress:
    return PFAddress(
        address_line1=address.address_lines[0],
        address_line2=address.address_lines[1],
        address_line3=address.address_lines[2],
        town=address.town,
        postcode=address.postcode,
    )


#
# def parcelforce_shipment(shipment: Shipment | dict):
#     if isinstance(shipment, dict):
#         shipment = _Shipment.model_validate(shipment)
#     ref_nums = {'reference_number' + i: ref for ref, i in enumerate(shipment.references)}
#     service_code = ParcelforceServiceDict[shipment.service.upper()]
#     ship = Shipment(
#         **ref_nums,
#         recipient_contact=parcelforce_contact(shipment.recipient_contact),
#         recipient_address=parcelforce_address(shipment.recipient_address),
#         total_number_of_parcels=shipment.boxes,
#         shipping_date=shipment.shipping_date,
#         service_code=service_code,
#     )
#     match shipment.direction:
#         case ShipDirection.OUTBOUND:
#             return Shipment.model_validate(ship)
#         case ShipDirection.INBOUND:
#             return ship.to_collection()
#         case ShipDirection.DROPOFF:
#             return ship.to_dropoff()
#         case _:
#             raise ValueError('Invalid Ship Direction')
#


# @property
# def direction(self) -> ShipDirection:
#     return get_ship_direction(self.model_dump())

# @property
# def remote_contact(self):
#     match self.direction:
#         case ShipDirection.OUTBOUND:
#             return self.recipient_contact
#         case ShipDirection.INBOUND:
#             return self.collection_info.collection_contact
#         case ShipDirection.DROPOFF:
#             return self.sender_contact
#         case _:
#             raise ValueError('Bad ShipDirection')

# @property
# def remote_address(self):
#     match self.direction:
#         case ShipDirection.OUTBOUND:
#             return self.recipient_address
#         case ShipDirection.INBOUND:
#             return self.collection_info.collection_address
#         case ShipDirection.DROPOFF:
#             return self.sender_address
#         case _:
#             raise ValueError('Bad ShipDirection')

#

# def to_dropoff(self, home_full_contact=None) -> 'ShipmentAwayDropoff':
#     home_full_contact = home_full_contact or shipaw_settings().full_contact
#     home_contact = ParcelforceProvider.provider_contact(home_full_contact)
#     home_address = ParcelforceProvider.provider_address(home_full_contact)
#     try:
#         return ShipmentAwayDropoff.model_validate(
#             self.model_copy(
#                 update={
#                     'recipient_contact': home_contact,
#                     'recipient_address': home_address,
#                     'sender_contact': ContactSender(**self.remote_contact.model_dump(exclude={'notifications'})),
#                     'sender_address': AddressSender(**self.remote_address.model_dump(exclude_none=True)),
#                 }
#             ),
#             from_attributes=True,
#         )
#     except ValidationError as e:
#         logger.error(f'Error converting Shipment to Dropoff: {e}')
#         raise e

# def to_collection(
#     self, home_contact=pf_sett().home_contact, home_address=pf_sett().home_address, own_label=True
# ) -> 'ShipmentAwayCollection':
#     try:
#         res = ShipmentAwayCollection.model_validate(
#             self.model_copy(
#                 update={
#                     'shipment_type': ShipmentType.COLLECTION,
#                     'print_own_label': own_label,
#                     'collection_info': CollectionInfo(
#                         collection_address=AddressCollection(**self.remote_address.model_dump()),
#                         collection_contact=ContactCollection.model_validate(
#                             self.remote_contact.model_dump(exclude={'notifications'})
#                         ),
#                         collection_time=DateTimeRange.null_times_from_date(self.shipping_date),
#                     ),
#                     'recipient_contact': home_contact,
#                     'recipient_address': home_address,
#                 }
#             ),
#             from_attributes=True,
#         )
#         return res
#     except ValidationError as e:
#         logger.error(f'Error converting Shipment to Collection: {e}')
#         raise e

