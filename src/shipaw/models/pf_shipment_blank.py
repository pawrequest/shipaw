import datetime as dt
from functools import partial

from loguru import logger
from pydantic import ValidationError, constr, model_validator

from shipaw import ship_types
from shipaw.models import pf_shared
from shipaw.models.pf_lists import HazardousGoods
from shipaw.models.pf_models import AddressCollection, AddressRecipient, AddressSender, DeliveryOptions
from shipaw.models.pf_shared import Enhancement
from shipaw.models.pf_top import CollectionInfo, Contact, ContactCollection, ContactSender
from shipaw.pf_config import pf_sett
from shipaw.ship_types import ShipmentType


class ShipmentReferenceFields(pf_shared.PFBaseModel):
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
    # from settings
    contract_number: str
    department_id: int

    recipient_contact: Contact
    recipient_address: AddressRecipient | AddressCollection
    total_number_of_parcels: int = 1
    shipping_date: dt.date
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24

    shipment_type: ShipmentType = ShipmentType.DELIVERY

    # subclasses
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = None
    sender_contact: ContactSender | None = None
    sender_address: AddressSender | None = None

    # unused
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
    def pf_label_filestem(self):
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


def to_collection_blank(shipment: Shipment, home_contact, home_address, own_label=True) -> ShipmentAwayCollection:
    try:
        return ShipmentAwayCollection.model_validate(
            shipment.model_copy(
                update={
                    'shipment_type': ShipmentType.COLLECTION,
                    'print_own_label': own_label,
                    'collection_info': CollectionInfo(
                        collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
                        collection_contact=ContactCollection.model_validate(
                            shipment.recipient_contact.model_dump(exclude={'notifications'})
                        ),
                        collection_time=pf_shared.DateTimeRange.null_times_from_date(shipment.shipping_date),
                    ),
                    'recipient_contact': home_contact,
                    'recipient_address': home_address,
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Collection: {e}')
        raise e


def to_dropoff_blank(shipment: Shipment, home_contact, home_address) -> ShipmentAwayDropoff:
    try:
        return ShipmentAwayDropoff.model_validate(
            shipment.model_copy(
                update={
                    'recipient_contact': home_contact,
                    'recipient_address': home_address,
                    'sender_contact': ContactSender(**shipment.recipient_contact.model_dump(exclude={'notifications'})),
                    'sender_address': AddressSender(**shipment.recipient_address.model_dump(exclude_none=True)),
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Dropoff: {e}')
        raise e


to_dropoff = partial(to_dropoff_blank, home_address=pf_sett().home_address, home_contact=pf_sett().home_contact)
to_collection = partial(to_collection_blank, home_address=pf_sett().home_address, home_contact=pf_sett().home_contact)
