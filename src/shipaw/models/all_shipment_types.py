from __future__ import annotations

import datetime as dt

import pydantic as _p
from loguru import logger

from shipaw import ship_types
from shipaw.models import pf_ext, pf_lists, pf_shared
from shipaw.models.pf_top import CollectionInfo, Contact, InternationalInfo
from shipaw.pf_config import pf_sett


class ShipmentReferenceFields(pf_shared.BasePFType):
    reference_number1: _p.constr(max_length=24) | None = None  # first 14 visible on label
    reference_number2: _p.constr(max_length=24) | None = None
    reference_number3: _p.constr(max_length=24) | None = None
    reference_number4: _p.constr(max_length=24) | None = None
    reference_number5: _p.constr(max_length=24) | None = None
    special_instructions1: _p.constr(max_length=25) | None = None
    special_instructions2: _p.constr(max_length=25) | None = None
    special_instructions3: _p.constr(max_length=25) | None = None
    special_instructions4: _p.constr(max_length=25) | None = None


class AllShipmentTypes(ShipmentReferenceFields):
    """Model for all shipment types.

    Minimum required fields:
    - recipient_contact
    - recipient_address

    """
    # from settings
    contract_number: str = pf_sett().pf_contract_num_1
    department_id: int = pf_sett().department_id

    # from user input
    recipient_contact: Contact
    recipient_address: pf_ext.AddTypes
    total_number_of_parcels: int = 1
    shipping_date: dt.date = dt.date.today()
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24

    # inputs for collections
    shipment_type: ship_types.DeliveryKind = 'DELIVERY'
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = None

    # notes and extras
    enhancement: pf_shared.Enhancement | None = None
    delivery_options: pf_ext.DeliveryOptions | None = None

    hazardous_goods: pf_lists.HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: ship_types.DropOffInd | None = None
    exchange_instructions1: _p.constr(max_length=25) | None = None
    exchange_instructions2: _p.constr(max_length=25) | None = None
    exchange_instructions3: _p.constr(max_length=25) | None = None
    exporter_address: pf_ext.AddressRecipient | None = None
    exporter_contact: Contact | None = None
    importer_address: pf_ext.AddressRecipient | None = None
    importer_contact: Contact | None = None
    in_bound_address: pf_ext.AddressRecipient | None = None
    in_bound_contact: Contact | None = None
    in_bound_details: pf_ext.InBoundDetails | None = None
    international_info: InternationalInfo | None = None
    pre_printed: bool | None = None

    request_id: int | None = None
    returns: pf_shared.Returns | None = None

    # @_p.field_validator('shipping_date', mode='after')
    # def ship_date_validator(cls, v, values):
    #     if v < dt.date.today():
    #         logger.info(f'Shipping date {v} is in the past, using today')
    #         return dt.date.today()

    @_p.field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').business_name
        return v

    @_p.model_validator(mode='after')
    def check_collection_info(self):
        if self.shipment_type == 'COLLECTION':
            assert isinstance(
                self.collection_info, CollectionInfo
            ), 'collection_info is required for collection shipments'
            assert self.print_own_label is not None, 'print_own_label is required for collection shipments'
        return self
