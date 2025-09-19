import datetime as dt
from pathlib import Path

from loguru import logger
from pydantic import ValidationError, constr, model_validator

from shipaw.agnostic import ship_types
from shipaw.agnostic.shipment import Shipment as _Shipment
from shipaw.agnostic.address import Address as _Address
from shipaw.parcelforce.lists import HazardousGoods
from shipaw.parcelforce.models import (
    AddressCollection,
    AddressRecipient,
    AddressRecipient as PFAddress,
    AddressSender,
    DeliveryOptions,
)
from shipaw.parcelforce.services import ParcelforceServiceDict, ParcelforceServices
from shipaw.parcelforce.shared import DateTimeRange, Enhancement, PFBaseModel, ServiceCode
from shipaw.parcelforce.top import CollectionInfo, Contact, ContactCollection, ContactSender
from shipaw.parcelforce.pf_config import pf_sett
from shipaw.agnostic.ship_types import ShipDirection, ShipmentType, get_ship_direction


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


class Shipment(ShipmentReferenceFields):
    shipment_type: ShipmentType = ShipmentType.DELIVERY
    # from settings
    department_id: int = pf_sett().department_id
    contract_number: str = pf_sett().pf_contract_num_1

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
    drop_off_ind: ship_types.DropOffInd | None = None

    def __str__(self):
        return f'{self.shipment_type} {f'from {self.collection_info.collection_address.address_line1} ' if self.collection_info else ''}to {self.recipient_address.address_line1}'

    @property
    def notifications_str(self) -> str:
        return self.recipient_contact.notifications_str

    @model_validator(mode='after')
    def ref_num_validator(self):
        self.reference_number1 = self.reference_number1 or self.recipient_contact.business_name[:24]
        return self

    @property
    def direction(self) -> ShipDirection:
        return get_ship_direction(self.model_dump())

    @property
    def remote_contact(self):
        match self.direction:
            case ShipDirection.OUTBOUND:
                return self.recipient_contact
            case ShipDirection.INBOUND:
                return self.collection_info.collection_contact
            case ShipDirection.DROPOFF:
                return self.sender_contact
            case _:
                raise ValueError('Bad ShipDirection')

    @property
    def remote_address(self):
        match self.direction:
            case ShipDirection.OUTBOUND:
                return self.recipient_address
            case ShipDirection.INBOUND:
                return self.collection_info.collection_address
            case ShipDirection.DROPOFF:
                return self.sender_address
            case _:
                raise ValueError('Bad ShipDirection')

    @property
    def label_dir(self):
        return pf_sett().label_dir / self.direction

    @property
    def label_stem(self):
        ln = (
            (
                f'Parcelforce {self.shipment_type.title()} Label '
                f'{f'from {self.collection_info.collection_contact.business_name} ' if self.collection_info else ''}'
                f'to {self.recipient_contact.business_name}'
                f' on {self.shipping_date}'
            )
            .replace(' ', '_')
            .replace('/', '_')
            .replace(':', '-')
            .replace(',', '')
            .replace('.', '_')
        )
        return ln

    @property
    def label_path(self):
        return (self.label_dir / self.label_stem).with_suffix('.pdf')

    @property
    def label_file(self):
        if self._label_file is None:
            self._label_file = unused_path(self.label_path)
        return self._label_file

    def to_dropoff(
        self, home_contact=pf_sett().home_contact, home_address=pf_sett().home_address
    ) -> 'ShipmentAwayDropoff':
        try:
            return ShipmentAwayDropoff.model_validate(
                self.model_copy(
                    update={
                        'recipient_contact': home_contact,
                        'recipient_address': home_address,
                        'sender_contact': ContactSender(**self.remote_contact.model_dump(exclude={'notifications'})),
                        'sender_address': AddressSender(**self.remote_address.model_dump(exclude_none=True)),
                    }
                ),
                from_attributes=True,
            )
        except ValidationError as e:
            logger.error(f'Error converting Shipment to Dropoff: {e}')
            raise e

    def to_collection(
        self, home_contact=pf_sett().home_contact, home_address=pf_sett().home_address, own_label=True
    ) -> 'ShipmentAwayCollection':
        try:
            return ShipmentAwayCollection.model_validate(
                self.model_copy(
                    update={
                        'shipment_type': ShipmentType.COLLECTION,
                        'print_own_label': own_label,
                        'collection_info': CollectionInfo(
                            collection_address=AddressCollection(**self.remote_address.model_dump()),
                            collection_contact=ContactCollection.model_validate(
                                self.remote_contact.model_dump(exclude={'notifications'})
                            ),
                            collection_time=DateTimeRange.null_times_from_date(self.shipping_date),
                        ),
                        'recipient_contact': home_contact,
                        'recipient_address': home_address,
                    }
                ),
                from_attributes=True,
            )
        except ValidationError as e:
            logger.error(f'Error converting Shipment to Collection: {e}')
            raise e


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


def unused_path(filepath: Path):
    def numbered_filepath(number: int):
        return filepath if not number else filepath.with_stem(f'{filepath.stem}_{number}')

    incremented = 0
    lpath = numbered_filepath(incremented)
    while lpath.exists():
        incremented += 1
        logger.warning(f'FilePath {lpath} already exists')
        lpath = numbered_filepath(incremented)
    logger.debug(f'Using FilePath={lpath}')
    return lpath


def parcelforce_contact(contact: Contact) -> Contact:
    return Contact(
        business_name=contact.business_name,
        mobile_phone=contact.mobile_phone,
        email_address=contact.email_address,
        contact_name=contact.contact_name,
    )


def parcelforce_address(address: _Address) -> PFAddress:
    return PFAddress(
        address_line1=address.address_lines[0],
        address_line2=address.address_lines[1],
        address_line3=address.address_lines[2],
        town=address.town,
        postcode=address.postcode,
    )


def parcelforce_shipment(shipment: _Shipment | dict):
    if isinstance(shipment, dict):
        shipment = _Shipment.model_validate(shipment)
    ref_nums = {'reference_number' + i: ref for ref, i in enumerate(shipment.references)}
    service_code = ParcelforceServiceDict[shipment.service.upper()]
    ship = Shipment(
        **ref_nums,
        recipient_contact=parcelforce_contact(shipment.recipient_contact),
        recipient_address=parcelforce_address(shipment.recipient_address),
        total_number_of_parcels=shipment.boxes,
        shipping_date=shipment.shipping_date,
        service_code=service_code,
    )
    match shipment.direction:
        case ShipDirection.OUTBOUND:
            return Shipment.model_validate(ship)
        case ShipDirection.INBOUND:
            return ship.to_collection()
        case ShipDirection.DROPOFF:
            return ship.to_dropoff()
        case _:
            raise ValueError('Invalid Ship Direction')

