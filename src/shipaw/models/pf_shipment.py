# from __future__ import annotations
import datetime as dt
from typing import Annotated

import sqlmodel as sqm
import pydantic as _p
from pawdantic.pawsql import JSONColumn

from shipaw import ship_types
from shipaw.models import pf_lists, pf_models, pf_shared
from shipaw.models.pf_shared import Alert
from shipaw.models.pf_top import CollectionInfo, Contact
from shipaw.pf_config import pf_sett
from shipaw.ship_types import limit_daterange_no_weekends


class ShipmentReferenceFields(pf_shared.PFBaseModel):
    ...
    reference_number1: str | None = _p.Field(None, max_length=24)
    reference_number2: str | None = _p.Field(None, max_length=24)
    reference_number3: str | None = _p.Field(None, max_length=24)
    reference_number4: str | None = _p.Field(None, max_length=24)
    reference_number5: str | None = _p.Field(None, max_length=24)
    special_instructions1: str | None = _p.Field(None, max_length=25)
    special_instructions2: str | None = _p.Field(None, max_length=25)
    special_instructions3: str | None = _p.Field(None, max_length=25)
    special_instructions4: str | None = _p.Field(None, max_length=25)


class ShipmentRequest(ShipmentReferenceFields):
    # from settings
    contract_number: str = pf_sett().pf_contract_num_1
    department_id: int = pf_sett().department_id

    # from user input
    recipient_contact: Contact = sqm.Field(..., sa_column=sqm.Column(JSONColumn(Contact)))
    # recipient_contact: Contact = sqm.Field(..., sa_column=sqm.Column(PawdanticJSON(Contact)))
    recipient_address: pf_models.AddressRecipient = sqm.Field(
        ...,
        sa_column=sqm.Column(JSONColumn(pf_models.AddressRecipient))
    )
    total_number_of_parcels: int = 1
    shipping_date: dt.date = dt.date.today()
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24

    # inputs for collections
    shipment_type: ship_types.DeliveryKindEnum = 'DELIVERY'
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = sqm.Field(
        default=None,
        sa_column=sqm.Column(JSONColumn(CollectionInfo))
    )
    #
    # # extras
    enhancement: pf_shared.Enhancement | None = sqm.Field(
        default=None,
        sa_column=sqm.Column(JSONColumn(pf_shared.Enhancement))
    )
    delivery_options: pf_models.DeliveryOptions | None = sqm.Field(
        default=None,
        sa_column=sqm.Column(JSONColumn(pf_models.DeliveryOptions))
    )
    hazardous_goods: pf_lists.HazardousGoods | None = sqm.Field(
        default=None,
        sa_column=sqm.Column(JSONColumn(pf_lists.HazardousGoods))
    )
    consignment_handling: bool | None = None

    drop_off_ind: ship_types.DropOffIndEnum | None = None
    # exchange_instructions1: _p.constr(max_length=25) | None = None
    # exchange_instructions2: paw_types.truncated_printable_str_type(25) | None = None
    # exchange_instructions3: paw_types.truncated_printable_str_type(25) | None = None
    # exporter_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(pf_models.AddressRecipient)))
    # exporter_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(Contact)))
    # importer_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(pf_models.AddressRecipient)))
    # importer_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(Contact)))
    # in_bound_address: pf_models.AddressRecipient | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(pf_models.AddressRecipient)))
    # in_bound_contact: Contact | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(Contact)))
    # in_bound_details: pf_models.InBoundDetails | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(pf_models.InBoundDetails)))
    # international_info: InternationalInfo | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(InternationalInfo)))
    # pre_printed: bool | None = None
    #
    # request_id: int | None = None
    # returns: pf_shared.Returns | None = sqm.Field(default=None, sa_column=sqm.Column(JSONColumn(pf_shared.Returns)))

    # @_p.field_validator('shipping_date', mode='after')
    # def ship_date_validator(cls, v, values):
    #     if v < dt.date.today():
    #         logger.info(f'Shipping date {v} is in the past, using today')
    #         return dt.date.today()

    # @_p.field_validator('reference_number1', mode='after')
    # def ref_num_validator(cls, v, values):
    #     if not v:
    #         v = values.data.get('recipient_contact').business_name
    #     return v
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
