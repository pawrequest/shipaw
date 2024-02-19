# generated by datamodel-codegen:
#   filename:  ShipServiceDefinitions-OpenApi31Yaml.yaml
#   timestamp: 2024-02-17T19:09:14+00:00

from __future__ import annotations

from functools import partial
from typing import List, Optional, Sequence
from enum import Enum

from pydantic import Field

from shipr.models.express.address import Address, Contact
from shipr.models.express.enums import AlertType
from shipr.models.express.shared import BasePFType


class PAF(BasePFType):
    postcode: Optional[str] = Field(None)
    count: Optional[int] = Field(None)
    specified_neighbour: Optional[List[SpecifiedNeighbour]] = Field(
        None, description=''
    )


class SpecifiedNeighbour(BasePFType):
    address: Optional[List[Address]] = Field(None, description='')


class Notifications(BasePFType):
    notification_type: List[str] = Field(..., description='')


class Enhancement(BasePFType):
    enhanced_compensation: Optional[str] = Field(None)
    saturday_delivery_required: Optional[bool] = Field(
        None
    )


class HazardousGood(BasePFType):
    lqdgun_code: Optional[str] = Field(None)
    lqdg_description: Optional[str] = Field(None)
    lqdg_volume: Optional[float] = Field(None)
    firearms: Optional[str] = Field(None)


class Returns(BasePFType):
    returns_email: Optional[str] = Field(None)
    email_message: Optional[str] = Field(None)
    email_label: bool = Field(...)


class ContentDetail(BasePFType):
    country_of_manufacture: str = Field(...)
    country_of_origin: Optional[str] = Field(None)
    manufacturers_name: Optional[str] = Field(None)
    description: str = Field(...)
    unit_weight: float = Field(...)
    unit_quantity: int = Field(...)
    unit_value: float = Field(...)
    currency: str = Field(...)
    tariff_code: Optional[str] = Field(None)
    tariff_description: Optional[str] = Field(None)
    article_reference: Optional[str] = Field(None)


class DateTimeRange(BasePFType):
    from_: str = Field(...)
    to: str = Field(...)


class ContentData(BasePFType):
    name: str = Field(...)
    data: str = Field(...)


class LabelItem(BasePFType):
    name: str = Field(...)
    data: str = Field(...)


class Barcode(BasePFType):
    name: str = Field(...)
    data: str = Field(...)


class Image(BasePFType):
    name: str = Field(...)
    data: str = Field(...)


class PrintType(Enum):
    all_parcels = 'ALL_PARCELS'
    single_parcel = 'SINGLE_PARCEL'


class Document(BasePFType):
    data: str = Field(...)


class ManifestShipment(BasePFType):
    shipment_number: str = Field(...)
    service_code: str = Field(...)


class CompletedShipment(BasePFType):
    shipment_number: Optional[str] = Field(None)
    out_bound_shipment_number: Optional[str] = Field(
        None
    )
    in_bound_shipment_number: Optional[str] = Field(None)
    partner_number: Optional[str] = Field(None)


class CompletedReturnInfo(BasePFType):
    status: str = Field(...)
    shipment_number: str = Field(...)
    collection_time: DateTimeRange = Field(...)


class Authentication(BasePFType):
    user_name: str = Field(...)
    password: str = Field(...)


class CompletedCancelInfo(BasePFType):
    status: Optional[str] = Field(None)
    shipment_number: Optional[str] = Field(None)


class SafePlaceList(BasePFType):
    safe_place: Optional[List[str]] = Field(None, description='')


class NominatedDeliveryDateList(BasePFType):
    nominated_delivery_date: Optional[List[str]] = Field(
        None, description=''
    )


class ServiceCodes(BasePFType):
    service_code: Optional[List[str]] = Field(None, description='')


class Hours(BasePFType):
    open: Optional[str] = Field(None)
    close: Optional[str] = Field(None)
    close_lunch: Optional[str] = Field(None)
    after_lunch_opening: Optional[str] = Field(None)


class Position(BasePFType):
    longitude: Optional[float] = Field(None)
    latitude: Optional[float] = Field(None)


class InBoundDetails(BasePFType):
    contract_number: str = Field(...)
    service_code: str = Field(...)
    total_shipment_weight: Optional[str] = Field(None)
    enhancement: Optional[Enhancement] = Field(None)
    reference_number1: Optional[str] = Field(None)
    reference_number2: Optional[str] = Field(None)
    reference_number3: Optional[str] = Field(None)
    reference_number4: Optional[str] = Field(None)
    reference_number5: Optional[str] = Field(None)
    special_instructions1: Optional[str] = Field(None)
    special_instructions2: Optional[str] = Field(None)
    special_instructions3: Optional[str] = Field(None)
    special_instructions4: Optional[str] = Field(None)


class HazardousGoods(BasePFType):
    hazardous_good: List[HazardousGood] = Field(
        ..., description=''
    )


class ContentDetails(BasePFType):
    content_detail: List[ContentDetail] = Field(
        ..., description=''
    )


class CollectionInfo(BasePFType):
    collection_contact: Contact = Field(...)
    collection_address: Address = Field(...)
    collection_time: Optional[DateTimeRange] = Field(None)


class ParcelContents(BasePFType):
    item: List[ContentData] = Field(..., description='')


class LabelData(BasePFType):
    item: List[LabelItem] = Field(..., description='')


class Barcodes(BasePFType):
    barcode: List[Barcode] = Field(..., description='')


class Images(BasePFType):
    image: List[Image] = Field(..., description='')


class ManifestShipments(BasePFType):
    manifest_shipment: List[ManifestShipment] = Field(
        ..., description=''
    )


class CompletedShipments(BasePFType):
    completed_shipment: List[CompletedShipment] = Field(
        ..., description=''
    )


class Alert(BasePFType):
    code: int = Field(...)
    message: str = Field(...)
    type: AlertType = Field(...)


class CompletedCancel(BasePFType):
    completed_cancel_info: Optional[CompletedCancelInfo] = Field(
        None
    )


class Department(BasePFType):
    department_id: Optional[List[int]] = Field(
        None, description=''
    )
    service_codes: Optional[List[ServiceCodes]] = Field(
        None, description=''
    )
    nominated_delivery_date_list: Optional[NominatedDeliveryDateList] = Field(
        None
    )


class Mon(BasePFType):
    hours: Optional[Hours] = Field(None)


class Tue(BasePFType):
    hours: Optional[Hours] = Field(None)


class Wed(BasePFType):
    hours: Optional[Hours] = Field(None)


class Thu(BasePFType):
    hours: Optional[Hours] = Field(None)


class Fri(BasePFType):
    hours: Optional[Hours] = Field(None)


class Sat(BasePFType):
    hours: Optional[Hours] = Field(None)


class Sun(BasePFType):
    hours: Optional[Hours] = Field(None)


class BankHol(BasePFType):
    hours: Optional[Hours] = Field(None)


class Parcel(BasePFType):
    weight: Optional[float] = Field(None)
    length: Optional[int] = Field(None)
    height: Optional[int] = Field(None)
    width: Optional[int] = Field(None)
    purpose_of_shipment: Optional[str] = Field(None)
    invoice_number: Optional[str] = Field(None)
    export_license_number: Optional[str] = Field(None)
    certificate_number: Optional[str] = Field(None)
    content_details: Optional[ContentDetails] = Field(None)
    shipping_cost: Optional[float] = Field(None)


class ParcelLabelData(BasePFType):
    parcel_number: Optional[str] = Field(None)
    shipment_number: Optional[str] = Field(None)
    journey_leg: Optional[str] = Field(None)
    label_data: Optional[LabelData] = Field(None)
    barcodes: Optional[Barcodes] = Field(None)
    images: Optional[Images] = Field(None)
    parcel_contents: Optional[List[ParcelContents]] = Field(
        None, description=''
    )


class CompletedManifestInfo(BasePFType):
    department_id: int = Field(...)
    manifest_number: str = Field(...)
    manifest_type: str = Field(...)
    total_shipment_count: int = Field(...)
    manifest_shipments: ManifestShipments = Field(...)


class CompletedShipmentInfoCreatePrint(BasePFType):
    lead_shipment_number: Optional[str] = Field(None)
    shipment_number: Optional[str] = Field(None)
    delivery_date: Optional[str] = Field(None)
    status: str = Field(...)
    completed_shipments: CompletedShipments = Field(...)


class Alerts(BasePFType):
    alert: List[Alert] = Field(..., description='')


class Departments(BasePFType):
    department: Optional[List[Department]] = Field(
        None, description=''
    )


class OpeningHours(BasePFType):
    mon: Optional[Mon] = Field(None)
    tue: Optional[Tue] = Field(None)
    wed: Optional[Wed] = Field(None)
    thu: Optional[Thu] = Field(None)
    fri: Optional[Fri] = Field(None)
    sat: Optional[Sat] = Field(None)
    sun: Optional[Sun] = Field(None)
    bank_hol: Optional[BankHol] = Field(None)


class Parcels(BasePFType):
    parcel: List[Parcel] = Field(..., description='')


class ShipmentLabelData(BasePFType):
    parcel_label_data: List[ParcelLabelData] = Field(
        ..., description=''
    )


class CompletedManifests(BasePFType):
    completed_manifest_info: List[CompletedManifestInfo] = Field(
        ..., description=''
    )


class NominatedDeliveryDates(BasePFType):
    service_code: Optional[str] = Field(None)
    departments: Optional[Departments] = Field(None)


class PostcodeExclusion(BasePFType):
    delivery_postcode: Optional[str] = Field(None)
    collection_postcode: Optional[str] = Field(None)
    departments: Optional[Departments] = Field(None)


class PostOffice(BasePFType):
    post_office_id: Optional[str] = Field(None)
    business: Optional[str] = Field(None)
    address: Optional[Address] = Field(None)
    opening_hours: Optional[OpeningHours] = Field(None)
    distance: Optional[float] = Field(None)
    availability: Optional[bool] = Field(None)
    position: Optional[Position] = Field(None)
    booking_reference: Optional[str] = Field(None)


class InternationalInfo(BasePFType):
    parcels: Optional[Parcels] = Field(None)
    exporter_customs_reference: Optional[str] = Field(
        None
    )
    recipient_importer_vat_no: Optional[str] = Field(
        None
    )
    original_export_shipment_no: Optional[str] = Field(
        None
    )
    documents_only: Optional[bool] = Field(None)
    documents_description: Optional[str] = Field(None)
    value_under200_us_dollars: Optional[bool] = Field(
        None
    )
    shipment_description: Optional[str] = Field(None)
    comments: Optional[str] = Field(None)
    invoice_date: Optional[str] = Field(None)
    terms_of_delivery: Optional[str] = Field(None)
    purchase_order_ref: Optional[str] = Field(None)


class ConvenientCollect(BasePFType):
    postcode: Optional[str] = Field(None)
    post_office: Optional[List[PostOffice]] = Field(
        None, description=''
    )
    count: Optional[int] = Field(None)
    post_office_id: Optional[str] = Field(None)


class SpecifiedPostOffice(BasePFType):
    postcode: Optional[str] = Field(None)
    post_office: Optional[List[PostOffice]] = Field(
        None, description=''
    )
    count: Optional[int] = Field(None)
    post_office_id: Optional[str] = Field(None)


def obj_dict(objs: BasePFType | Sequence[BasePFType], **kwargs) -> dict:
    if isinstance(objs, BasePFType):
        objs = [objs]
    return {obj.__class__.__name__: obj.model_dump(**kwargs) for obj in objs}


alias_dict = partial(obj_dict, by_alias=True, exclude_none=True)
