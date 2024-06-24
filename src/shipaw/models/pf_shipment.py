# from __future__ import annotations
import datetime as dt

from loguru import logger
from pawdantic.pawsql import optional_json_field, required_json_field
from pydantic import ValidationError, constr, field_validator

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

    @property
    def notifications_str(self) -> str:
        msg = (
            f'Recip Notifications = {self.recipient_contact.email_address}'
            f' + {self.recipient_contact.mobile_phone} '
            f'{self.recipient_contact.notifications}\n'
        )
        return msg

    @property
    def is_collection(self):
        return self.collection_info is not None

    def make_inbound(self):
        """OverWrites the recipient contact and address with the home contact and address"""
        logger.debug('Converting Shipment to Inbound')
        self.recipient_contact = pf_sett().home_contact
        self.recipient_address = pf_sett().home_address

    @field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').business_name
        return v


class ShipmentAwayCollection(Shipment):
    shipment_type: ShipmentType = ShipmentType.COLLECTION
    print_own_label: bool | None = None
    collection_info: CollectionInfo

    @property
    def notifications_str(self) -> str:
        msg = super().notifications_str
        msg += (
            f'Collection Notifications = {self.collection_info.collection_contact.email_address} '
            f'+ {self.collection_info.collection_contact.mobile_phone}'
        )
        return msg

    @classmethod
    def from_shipment(cls, shipment: Shipment, own_label=True):
        logger.debug('Converting Shipment to Collection')
        try:
            collection_contact = ContactCollection(**shipment.recipient_contact.model_dump(exclude={'notifications'}))
            collection_adddress = AddressCollection(**shipment.recipient_address.model_dump())
            collection_info = CollectionInfo(
                collection_address=collection_adddress,
                collection_contact=collection_contact,
                collection_time=pf_shared.DateTimeRange.null_times_from_date(shipment.shipping_date),
            )
            colly = cls(**shipment.model_dump(), collection_info=collection_info)

            colly.recipient_contact = pf_sett().home_contact
            colly.recipient_address = pf_sett().home_address
            colly.print_own_label = own_label

            return colly

        except ValidationError as e:
            logger.error(f'Error converting Shipment to Collection: {e}')
            raise e


class ShipmentAwayDropoff(Shipment):
    sender_contact: ContactSender
    sender_address: AddressSender

    @classmethod
    def from_shipment(cls, shipment: Shipment):
        logger.debug('Converting Shipment to Dropoff')
        try:
            sender_address = AddressSender(**shipment.recipient_address.model_dump())
            sender_contact = ContactSender(**shipment.recipient_contact.model_dump(exclude={'notifications'}))
            dropoff = cls(
                **shipment.model_dump(),
                sender_address=sender_address,
                sender_contact=sender_contact,
            )
            dropoff.recipient_contact = pf_sett().home_contact
            dropoff.recipient_address = pf_sett().home_address
            return dropoff
        except ValidationError as e:
            logger.error(f'Error converting Shipment to Dropoff: {e}')
            raise e
