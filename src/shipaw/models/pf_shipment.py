# from __future__ import annotations
import datetime as dt

from loguru import logger
from pawdantic.pawsql import optional_json_field, required_json_field
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
    contract_number: str = pf_sett().pf_contract_num_1
    department_id: int = pf_sett().department_id

    # from user input
    recipient_contact: Contact = required_json_field(Contact)
    recipient_address: AddressRecipient | AddressCollection = required_json_field(AddressRecipient)
    total_number_of_parcels: int = 1
    shipping_date: dt.date
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24

    shipment_type: ShipmentType = ShipmentType.DELIVERY

    # # extras
    enhancement: Enhancement | None = optional_json_field(Enhancement)
    delivery_options: DeliveryOptions | None = optional_json_field(DeliveryOptions)
    hazardous_goods: HazardousGoods | None = optional_json_field(HazardousGoods)
    consignment_handling: bool | None = None

    drop_off_ind: ship_types.DropOffInd | None = None

    # unused
    print_own_label: None = None
    collection_info: None = None
    sender_contact: None = None
    sender_address: None = None

    @property
    def notifications_str(self) -> str:
        msg = (
            f'Recip Notifications = {self.recipient_contact.email_address}'
            f' + {self.recipient_contact.mobile_phone} '
            f'{self.recipient_contact.notifications}\n'
        )
        return msg

    def make_inbound(self):
        """OverWrites the recipient contact and address with the home contact and address"""
        logger.debug('Converting Shipment to Inbound')
        self.recipient_contact = pf_sett().home_contact
        self.recipient_address = pf_sett().home_address

    @model_validator(mode='after')
    def ref_num_validator(self):
        self.reference_number1 = self.reference_number1 or self.recipient_contact.business_name[:24]
        return self


class ShipmentAwayCollection(Shipment):
    shipment_type: ShipmentType = ShipmentType.COLLECTION
    print_own_label: bool = True
    collection_info: CollectionInfo

    @property
    def notifications_str(self) -> str:
        msg = super().notifications_str
        msg += (
            f'Collection Notifications = {self.collection_info.collection_contact.email_address} '
            f'+ {self.collection_info.collection_contact.mobile_phone}'
        )
        return msg


class ShipmentAwayDropoff(Shipment):
    sender_contact: ContactSender
    sender_address: AddressSender


def to_collection(shipment: Shipment, own_label=True) -> ShipmentAwayCollection:
    try:
        return ShipmentAwayCollection.model_validate(
            shipment.model_copy(
                update={
                    'shipment_type': ShipmentType.COLLECTION,
                    'print_own_label': own_label,
                    'collection_info': CollectionInfo(
                        collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
                        collection_contact=ContactCollection(
                            **shipment.recipient_contact.model_dump(exclude={'notifications'})
                        ),
                        collection_time=pf_shared.DateTimeRange.null_times_from_date(shipment.shipping_date),
                    ),
                    'recipient_contact': pf_sett().home_contact,
                    'recipient_address': pf_sett().home_address,
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Collection: {e}')
        raise e


def to_dropoff(shipment: Shipment) -> ShipmentAwayDropoff:
    try:
        return ShipmentAwayDropoff.model_validate(
            shipment.model_copy(
                update={
                    'recipient_contact': pf_sett().home_contact,
                    'recipient_address': pf_sett().home_address,
                    'sender_contact': ContactSender(**shipment.recipient_contact.model_dump(exclude={'notifications'})),
                    'sender_address': AddressSender(**shipment.recipient_address.model_dump()),
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Dropoff: {e}')
        raise e
