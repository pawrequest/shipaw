from __future__ import annotations

import os
from datetime import date
from typing import List, Optional

import pydantic
import sqlmodel as sqm
from pydantic import Field, constr

from shipr.models import lists, shipr_shared as shared, simple_models as sm
from pawsupport.pydantic.pyd_types import TruncatedSafeMaybeStr, TruncatedSafeStr
from shipr.models.lists import Notifications


class BaseAddress(shared.BasePFType):
    address_line1: TruncatedSafeStr(24)
    address_line2: TruncatedSafeMaybeStr(24)
    address_line3: TruncatedSafeMaybeStr(24)
    town: TruncatedSafeStr(24)
    postcode: str
    country: str = pydantic.Field("GB")

    @classmethod
    def from_lines_str_and_postcode(cls, addr_lines_str: str, postcode: str):
        return cls.AddressRecipientPF(
            **cls.address_string_to_dict(addr_lines_str),
            town="",
            postcode=postcode,
        )

    def address_lines_list(self):
        return [self.address_line1, self.address_line2, self.address_line3, self.town,
                self.postcode, self.country]

    def address_lines_str(self):
        return "\n".join(self.address_lines_list())

    def address_lines_dict(self):
        return {
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "address_line3": self.address_line3,
        }

    def address_string_to_dict(self, address_str: str) -> dict[str, str]:
        addr_lines = address_str.splitlines()
        if len(addr_lines) < 3:
            addr_lines.extend([""] * (3 - len(addr_lines)))
        elif len(addr_lines) > 3:
            addr_lines[2] = ",".join(addr_lines[2:])
        return {
            "address_line1": addr_lines[0],
            "address_line2": addr_lines[1],
            "address_line3": addr_lines[2],
        }


class AddressSender(BaseAddress):
    town: TruncatedSafeStr(24)
    postcode: str
    country: str = pydantic.Field("GB")


class AddressRecipient(BaseAddress):
    address_line1: TruncatedSafeStr(40)
    address_line2: TruncatedSafeMaybeStr(50)
    address_line3: TruncatedSafeMaybeStr(60)
    town: TruncatedSafeStr(30)


class Contact(shared.BasePFType):
    business_name: TruncatedSafeStr(40)
    email_address: TruncatedSafeStr(50)
    mobile_phone: str

    contact_name: TruncatedSafeMaybeStr(30)
    telephone: Optional[str] = None
    fax: Optional[str] = None

    senders_name: TruncatedSafeMaybeStr(25)
    notifications: Optional[Notifications] = None


class SpecifiedNeighbour(shared.BasePFType):
    address: Optional[List[AddressRecipient]] = pydantic.Field(None, description="")


class PAF(shared.BasePFType):
    postcode: Optional[str] = None
    count: Optional[int] = pydantic.Field(None)
    specified_neighbour: Optional[List[SpecifiedNeighbour]] = pydantic.Field(None, description="")


class CollectionInfo(shared.BasePFType):
    collection_contact: Contact
    collection_address: AddressRecipient
    collection_time: Optional[sm.DateTimeRange] = None


class PostOffice(shared.BasePFType):
    post_office_id: Optional[str] = None
    business: Optional[str] = None
    address: Optional[AddressRecipient] = None
    opening_hours: Optional[shared.OpeningHours] = None
    distance: Optional[float] = None
    availability: Optional[bool] = None
    position: Optional[sm.Position] = None
    booking_reference: Optional[str] = None


class AddressChoice(shared.BasePFType):
    address: AddressRecipient = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    score: int


class ConvenientCollect(shared.BasePFType):
    postcode: Optional[str] = None
    post_office: Optional[list[PostOffice]] = Field(None, description="")
    count: Optional[int] = None
    post_office_id: Optional[str] = None


class SpecifiedPostOffice(shared.BasePFType):
    postcode: Optional[str] = None
    post_office: Optional[list[PostOffice]] = Field(None, description="")
    count: Optional[int] = None
    post_office_id: Optional[str] = None


class CompletedReturnInfo(shared.BasePFType):
    status: str
    shipment_number: str
    collection_time: sm.DateTimeRange


class InBoundDetails(shared.BasePFType):
    contract_number: str
    service_code: str
    total_shipment_weight: Optional[str] = None
    enhancement: Optional[sm.Enhancement] = None
    reference_number1: Optional[str] = None
    reference_number2: Optional[str] = None
    reference_number3: Optional[str] = None
    reference_number4: Optional[str] = None
    reference_number5: Optional[str] = None
    special_instructions1: Optional[str] = None
    special_instructions2: Optional[str] = None
    special_instructions3: Optional[str] = None
    special_instructions4: Optional[str] = None


class Department(shared.BasePFType):
    department_id: Optional[list[int]] = pydantic.Field(None, description="")
    service_codes: Optional[list[lists.ServiceCodes]] = pydantic.Field(None, description="")
    nominated_delivery_date_list: Optional[lists.NominatedDeliveryDatelist] = None


class Mon(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Tue(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Wed(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Thu(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Fri(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Sat(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Sun(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class BankHol(shared.BasePFType):
    hours: Optional[sm.Hours] = None


class Parcel(shared.BasePFType):
    weight: Optional[float] = None
    length: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    purpose_of_shipment: Optional[str] = None
    invoice_number: Optional[str] = None
    export_license_number: Optional[str] = None
    certificate_number: Optional[str] = None
    content_details: Optional[lists.ContentDetails] = None
    shipping_cost: Optional[float] = None


class ParcelLabelData(shared.BasePFType):
    parcel_number: Optional[str] = None
    shipment_number: Optional[str] = None
    journey_leg: Optional[str] = None
    label_data: Optional[lists.LabelData] = None
    barcodes: Optional[lists.Barcodes] = None
    images: Optional[lists.Images] = None
    parcel_contents: Optional[list[lists.ParcelContents]] = pydantic.Field(None, description="")


class CompletedManifestInfo(shared.BasePFType):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: lists.ManifestShipments


class CompletedShipmentInfoCreatePrint(shared.BasePFType):
    lead_shipment_number: Optional[str] = None
    shipment_number: Optional[str] = None
    delivery_date: Optional[str] = None
    status: str
    completed_shipments: lists.CompletedShipments


class NominatedDeliveryDates(shared.BasePFType):
    service_code: Optional[str] = None
    departments: Optional[lists.Departments] = None


class PostcodeExclusion(shared.BasePFType):
    delivery_postcode: Optional[str] = None
    collection_postcode: Optional[str] = None
    departments: Optional[lists.Departments] = None


class InternationalInfo(shared.BasePFType):
    parcels: Optional[lists.Parcels] = None
    exporter_customs_reference: Optional[str] = None
    recipient_importer_vat_no: Optional[str] = None
    original_export_shipment_no: Optional[str] = None
    documents_only: Optional[bool] = None
    documents_description: Optional[str] = None
    value_under200_us_dollars: Optional[bool] = None
    shipment_description: Optional[str] = None
    comments: Optional[str] = None
    invoice_date: Optional[str] = None
    terms_of_delivery: Optional[str] = None
    purchase_order_ref: Optional[str] = None


class DeliveryOptions(shared.BasePFType):
    convenient_collect: Optional[ConvenientCollect] = None
    irts: Optional[bool] = None
    letterbox: Optional[bool] = None
    specified_post_office: Optional[SpecifiedPostOffice] = None
    specified_neighbour: Optional[str] = None
    safe_place: Optional[str] = None
    pin: Optional[int] = None
    named_recipient: Optional[bool] = None
    address_only: Optional[bool] = None
    nominated_delivery_date: Optional[str] = None
    personal_parcel: Optional[str] = None


class RequestedShipmentMinimum(shared.BasePFType):
    recipient_contact: Contact
    recipient_address: AddressRecipient
    contract_number: str
    total_number_of_parcels: int = Field(1)
    shipping_date: date = Field(default_factory=date.today)
    service_code: shared.ServiceCode = Field(shared.ServiceCode.EXPRESS24)
    shipment_type: shared.DeliveryKind = 'DELIVERY'
    department_id: int = shared.DepartmentNum

    @classmethod
    def from_minimal(
            cls,
            ship_date: date,
            contact: Contact,
            address: AddressRecipient,
            num_parcels: int = 1,
    ):
        contract_no = os.environ.get("PF_CONT_NUM_1")

        return cls(
            department_id=shared.DepartmentNum.MAIN,
            shipment_type=shared.DeliveryKind.DELIVERY,
            contract_number=contract_no,
            service_code=shared.ServiceCode.EXPRESS24,
            shipping_date=ship_date,
            recipient_contact=contact,
            recipient_address=address,
            total_number_of_parcels=num_parcels,
        )


class RequestedShipmentSimple(RequestedShipmentMinimum):
    job_reference: Optional[str] = Field(None)
    # todo validate both or none for sender
    sender_contact: Optional[Contact] = Field(None)
    sender_address: Optional[AddressRecipient] = Field(None)
    total_shipment_weight: Optional[float] = Field(None)
    enhancement: Optional[sm.Enhancement] = Field(None)
    delivery_options: Optional[DeliveryOptions] = Field(None)
    collection_info: Optional[CollectionInfo] = Field(None)


class RequestedShipmentComplex(RequestedShipmentSimple):
    hazardous_goods: Optional[lists.HazardousGoods] = Field(None)
    consignment_handling: Optional[bool] = Field(None)
    drop_off_ind: Optional[shared.DropOffInd] = Field(None)
    exchange_instructions1: Optional[constr(max_length=25)] = Field(None)
    exchange_instructions2: Optional[constr(max_length=25)] = Field(None)
    exchange_instructions3: Optional[constr(max_length=25)] = Field(None)
    exporter_address: Optional[AddressRecipient] = Field(None)
    exporter_contact: Optional[Contact] = Field(None)
    importer_address: Optional[AddressRecipient] = Field(None)
    importer_contact: Optional[Contact] = Field(None)
    in_bound_address: Optional[AddressRecipient] = Field(None)
    in_bound_contact: Optional[Contact] = Field(None)
    in_bound_details: Optional[InBoundDetails] = Field(None)
    international_info: Optional[InternationalInfo] = Field(None)
    pre_printed: Optional[bool] = Field(None)
    print_own_label: Optional[bool] = Field(None)
    reference_number1: Optional[constr(max_length=24)] = Field(None)
    reference_number2: Optional[constr(max_length=24)] = Field(None)
    reference_number3: Optional[constr(max_length=24)] = Field(None)
    reference_number4: Optional[constr(max_length=24)] = Field(None)
    reference_number5: Optional[constr(max_length=24)] = Field(None)
    request_id: Optional[int] = Field(None)
    returns: Optional[sm.Returns] = Field(None)
    special_instructions1: Optional[constr(max_length=25)] = Field(None)
    special_instructions2: Optional[constr(max_length=25)] = Field(None)
    special_instructions3: Optional[constr(max_length=25)] = Field(None)
    special_instructions4: Optional[constr(max_length=25)] = Field(None)


class CompletedShipmentInfo(shared.BasePFType):
    lead_shipment_number: Optional[str] = Field(None)
    delivery_date: Optional[date] = Field(None)
    status: str = Field(...)
    completed_shipments: RequestedShipmentComplex = Field(...)
