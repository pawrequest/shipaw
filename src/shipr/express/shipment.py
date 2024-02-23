from __future__ import annotations

import os
from datetime import date
from typing import Optional

from pydantic import Field
from . import types as el
from .enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from .shared import BasePFType


class RequestedShipmentMinimum(BasePFType):
    recipient_contact: el.ContactPF
    recipient_address: el.AddressPF
    contract_number: str
    total_number_of_parcels: int = Field(1)
    shipping_date: date = Field(default_factory=date.today)
    service_code: ServiceCode = Field(ServiceCode.EXPRESS24)
    shipment_type: DeliveryTypeEnum = Field(DeliveryTypeEnum.DELIVERY)
    department_id: DepartmentEnum = Field(DepartmentEnum.MAIN)

    @classmethod
    def from_minimal(cls, ship_date: date, contact: el.ContactPF, address: el.AddressPF, num_parcels: int = 1):
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
    sender_contact: Optional[el.ContactPF] = Field(None)
    sender_address: Optional[el.AddressPF] = Field(None)
    total_shipment_weight: Optional[float] = Field(None)
    enhancement: Optional[el.Enhancement] = Field(None)
    delivery_options: Optional[el.DeliveryOptions] = Field(None)
    collection_info: Optional[el.CollectionInfo] = Field(None)


class RequestedShipmentComplex(RequestedShipmentSimple):
    hazardous_goods: Optional[el.HazardousGoods] = Field(None)
    consignment_handling: Optional[bool] = Field(None)
    drop_off_ind: Optional[str] = Field(None)
    exchange_instructions1: Optional[str] = Field(None)
    exchange_instructions2: Optional[str] = Field(None)
    exchange_instructions3: Optional[str] = Field(None)
    exporter_address: Optional[el.AddressPF] = Field(None)
    exporter_contact: Optional[el.ContactPF] = Field(None)
    importer_address: Optional[el.AddressPF] = Field(None)
    importer_contact: Optional[el.ContactPF] = Field(None)
    in_bound_address: Optional[el.AddressPF] = Field(None)
    in_bound_contact: Optional[el.ContactPF] = Field(None)
    in_bound_details: Optional[el.InBoundDetails] = Field(None)
    international_info: Optional[el.InternationalInfo] = Field(None)
    pre_printed: Optional[bool] = Field(None)
    print_own_label: Optional[bool] = Field(None)
    reference_number1: Optional[str] = Field(None)
    reference_number2: Optional[str] = Field(None)
    reference_number3: Optional[str] = Field(None)
    reference_number4: Optional[str] = Field(None)
    reference_number5: Optional[str] = Field(None)
    request_id: Optional[int] = Field(None)
    returns: Optional[el.Returns] = Field(None)
    special_instructions1: Optional[str] = Field(None)
    special_instructions2: Optional[str] = Field(None)
    special_instructions3: Optional[str] = Field(None)
    special_instructions4: Optional[str] = Field(None)


class CompletedShipmentInfo(BasePFType):
    lead_shipment_number: Optional[str] = Field(None)
    delivery_date: Optional[date] = Field(None)
    status: str = Field(...)
    completed_shipments: el.CompletedShipments = Field(...)
    requested_shipment: RequestedShipmentComplex = Field(...)


