from __future__ import annotations

from datetime import date
from typing import Optional, Annotated

from pydantic import Field

from shipr.models.express.expresslink_pydantic import (
    CollectionInfo,
    CompletedShipments,
    ConvenientCollect,
    Enhancement,
    HazardousGoods,
    InBoundDetails,
    InternationalInfo,
    Returns,
    SpecifiedPostOffice, DeliveryTypeEnum, ServiceCode, DepartmentEnum,
)
from shipr.models.express.shared import BasePFType
from shipr.models.express.address import Address, Contact

class RequestedShipmentMinimum(BasePFType):
    department_id: DepartmentEnum = Field(None)
    shipment_type: DeliveryTypeEnum = Field(...)
    contract_number: str = Field(...)
    service_code: ServiceCode = Field(...)
    shipping_date: date = Field(None)
    recipient_contact: Contact = Field(...)
    recipient_address: Address = Field(...)
    total_number_of_parcels: int = Field(None)


class RequestedShipmentSimple(RequestedShipmentMinimum):
    job_reference: Optional[str] = Field(None)
    # todo validate both or none for sender
    sender_contact: Optional[Contact] = Field(None)
    sender_address: Optional[Address] = Field(None)
    total_shipment_weight: Optional[float] = Field(None)
    enhancement: Optional[Enhancement] = Field(None)
    delivery_options: Optional[DeliveryOptions] = Field(None)
    collection_info: Optional[CollectionInfo] = Field(None)


class RequestedShipmentComplex(RequestedShipmentSimple):
    hazardous_goods: Optional[HazardousGoods] = Field(None)
    consignment_handling: Optional[bool] = Field(None)
    drop_off_ind: Optional[str] = Field(None)
    exchange_instructions1: Optional[str] = Field(None)
    exchange_instructions2: Optional[str] = Field(None)
    exchange_instructions3: Optional[str] = Field(None)
    exporter_address: Optional[Address] = Field(None)
    exporter_contact: Optional[Contact] = Field(None)
    importer_address: Optional[Address] = Field(None)
    importer_contact: Optional[Contact] = Field(None)
    in_bound_address: Optional[Address] = Field(None)
    in_bound_contact: Optional[Contact] = Field(None)
    in_bound_details: Optional[InBoundDetails] = Field(None)
    international_info: Optional[InternationalInfo] = Field(None)
    pre_printed: Optional[bool] = Field(None)
    print_own_label: Optional[bool] = Field(None)
    reference_number1: Optional[str] = Field(None)
    reference_number2: Optional[str] = Field(None)
    reference_number3: Optional[str] = Field(None)
    reference_number4: Optional[str] = Field(None)
    reference_number5: Optional[str] = Field(None)
    request_id: Optional[int] = Field(None)
    returns: Optional[Returns] = Field(None)
    special_instructions1: Optional[str] = Field(None)
    special_instructions2: Optional[str] = Field(None)
    special_instructions3: Optional[str] = Field(None)
    special_instructions4: Optional[str] = Field(None)


class CompletedShipmentInfo(BasePFType):
    lead_shipment_number: Optional[str] = Field(None)
    delivery_date: Optional[date] = Field(None)
    status: str = Field(...)
    completed_shipments: CompletedShipments = Field(...)
    requested_shipment: RequestedShipmentMinimum = Field(...)


class DeliveryOptions(BasePFType):
    convenient_collect: Optional[ConvenientCollect] = Field(
        None
    )
    irts: Optional[bool] = Field(None)
    letterbox: Optional[bool] = Field(None)
    specified_post_office: Optional[SpecifiedPostOffice] = Field(
        None
    )
    specified_neighbour: Optional[str] = Field(None)
    safe_place: Optional[str] = Field(None)
    pin: Optional[int] = Field(None)
    named_recipient: Optional[bool] = Field(None)
    address_only: Optional[bool] = Field(None)
    nominated_delivery_date: Optional[str] = Field(None)
    personal_parcel: Optional[str] = Field(None)
