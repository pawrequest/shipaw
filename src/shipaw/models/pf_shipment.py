# from __future__ import annotations
import datetime as dt

from pawdantic.pawsql import optional_json_field, required_json_field
from pydantic import constr, field_validator

from shipaw import ship_types
from shipaw.models import pf_shared
from shipaw.models.pf_lists import HazardousGoods
from shipaw.models.pf_models import AddressCollection, AddressRecipient, DeliveryOptions
from shipaw.models.pf_shared import Enhancement
from shipaw.models.pf_top import CollectionInfo, Contact
from shipaw.pf_config import pf_sett


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


class ShipmentRequest(ShipmentReferenceFields):
    # from settings
    contract_number: str = pf_sett().pf_contract_num_1
    department_id: int = pf_sett().department_id

    # from user input
    recipient_contact: Contact = required_json_field(Contact)
    # recipient_contact: Contact = sqm.Field(..., sa_column=sqm.Column(PawdanticJSON(Contact)))
    recipient_address: AddressRecipient | AddressCollection = required_json_field(AddressRecipient)
    total_number_of_parcels: int = 1
    shipping_date: dt.date = dt.date.today()
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24

    # inputs for collections
    shipment_type: ship_types.DeliveryKindEnum = 'DELIVERY'
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = optional_json_field(CollectionInfo)
    #
    # # extras
    enhancement: Enhancement | None = optional_json_field(Enhancement)
    delivery_options: DeliveryOptions | None = optional_json_field(DeliveryOptions)
    hazardous_goods: HazardousGoods | None = optional_json_field(HazardousGoods)
    consignment_handling: bool | None = None

    drop_off_ind: ship_types.DropOffIndEnum | None = None
    # exchange_instructions1: _p.constr(max_length=25) | None = None
    # exchange_instructions2: paw_types.truncated_printable_str_type(25) | None = None
    # exchange_instructions3: paw_types.truncated_printable_str_type(25) | None = None
    # exporter_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(pf_models.AddressRecipient)))
    # exporter_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(Contact)))
    # importer_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(pf_models.AddressRecipient)))
    # importer_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(Contact)))
    # in_bound_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(pf_models.AddressRecipient)))
    # in_bound_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(Contact)))
    # in_bound_details: pf_models.InBoundDetails | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(pf_models.InBoundDetails)))
    # international_info: InternationalInfo | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(InternationalInfo)))
    # pre_printed: bool | None = None
    #
    # request_id: int | None = None
    # returns: pf_shared.Returns | None = sqm.Field(default=None, sa_column=sqm.Column(PydanticJSONColumn(pf_shared.Returns)))

    # @_p.field_validator('shipping_date', mode='after')
    # def ship_date_validator(cls, v, values):
    #     if v < dt.date.today():
    #         logger.info(f'Shipping date {v} is in the past, using today')
    #         return dt.date.today()

    @field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').business_name
        return v
    #
    # @_p.model_validator(mode='after')
    # def check_collection_info(self):
    #     if self.shipment_type == 'COLLECTION':
    #         assert isinstance(
    #             self.collection_info, CollectionInfo
    #         ), 'collection_info is required for collection shipments'
    #         assert self.print_own_label is not None, 'print_own_label is required for collection shipments'
    #         if self.shipping_date <= dt.date.today():
    #             logger.info(
    #                 f'Shipping date {self.shipping_date} must be in the future. using tomorrow'
    #             )
    #             self.shipping_date = min(COLLECTION_WEEKDAYS)
    #     return self
    #
    # @property
    # def label_path(self):
    #     label_str = rf'Parcelforce {self.shipment_type.title()} Label for {self.recipient_contact.business_name} at {self.recipient_address.address_line1} on {self.shipping_date}'
    #     safe_label_str = re.sub(r'[<>:"/\\|?*]', '_', label_str)
    #     sett = pf_config.pf_sett()
    #     return (sett.label_dir / safe_label_str).with_suffix('.pdf')

# class ShipmentRequestDB(ShipmentRequest, table=True):
#     id: int | None = sqm.Field(primary_key=True)
