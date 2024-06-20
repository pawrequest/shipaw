# from __future__ import annotations
import datetime as dt

from loguru import logger
from pawdantic.pawsql import optional_json_field, required_json_field
from pydantic import constr, field_validator

from shipaw import ship_types
from shipaw.models import pf_shared
from shipaw.models.pf_lists import CollectionNotifications, HazardousGoods
from shipaw.models.pf_models import AddressCollection, AddressRecipient, DeliveryOptions
from shipaw.models.pf_shared import Enhancement
from shipaw.models.pf_top import CollectionContact, CollectionInfo, Contact
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

    # inputs for collections
    shipment_type: ShipmentType = ShipmentType.DELIVERY
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = optional_json_field(CollectionInfo)

    # # extras
    enhancement: Enhancement | None = optional_json_field(Enhancement)
    delivery_options: DeliveryOptions | None = optional_json_field(DeliveryOptions)
    hazardous_goods: HazardousGoods | None = optional_json_field(HazardousGoods)
    consignment_handling: bool | None = None

    drop_off_ind: ship_types.DropOffInd | None = None

    @property
    def is_collection(self):
        return self.collection_info is not None

    def make_collection(self, own_label: bool = True):
        logger.debug('Converting Shipment to Collection')
        self.shipment_type = ShipmentType.COLLECTION
        colcont = self.recipient_contact.model_dump()
        colcont['notifications'] = CollectionNotifications.standard_coll()
        colobj = CollectionContact.model_validate(colcont)

        self.collection_info = CollectionInfo(
            collection_address=self.recipient_address,
            collection_contact=colobj,
            collection_time=pf_shared.DateTimeRange.null_times_from_date(self.shipping_date),
        )
        self.print_own_label = own_label
        self.collection_info.collection_contact.senders_name = self.recipient_contact.contact_name
        self.make_inbound()

    def make_inbound(self):
        """OverWrites the recipient contact and address with the home contact and address"""
        logger.debug('Converting Shipment to Inbound')
        self.recipient_contact = pf_sett().home_contact
        self.recipient_address = pf_sett().home_address

    # @classmethod
    # def Collection(cls, **kwargs):
    #     shirpreq = cls(**kwargs)
    #     shirpreq.make_into_collection()
    #     return shirpreq

    @field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').business_name
        return v
