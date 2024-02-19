from __future__ import annotations

import os
from datetime import date
from typing import Optional

from pydantic import Field

from shipr.models.express.expresslink_pydantic import (
    CollectionInfo,
    CompletedShipments,
    Enhancement,
    HazardousGoods,
    InBoundDetails,
    InternationalInfo,
    Returns,
)
from shipr.models.express.enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from shipr.models.express.options_enums import DeliveryOptions
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

    @classmethod
    def from_minimal(cls, ship_date: date, contact: Contact, address: Address, num_parcels: int = 1):
        contract_no = os.environ.get('PF_CONT_NUM_1')

        return cls(
            department_id=DepartmentEnum.MAIN,
            shipment_type=DeliveryTypeEnum.DELIVERY,
            contract_number=contract_no,
            service_code=ServiceCode.EXPRESS24,
            shipping_date=ship_date,
            recipient_contact=contact,
            recipient_address=address,
            total_number_of_parcels=num_parcels,
        )


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


