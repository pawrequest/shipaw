import datetime as dt
import os

import pydantic as pyd

from . import pf_shared, pf_ext, types, pf_lists


class Contact(pf_shared.BasePFType):
    business_name: types.TruncatedSafeStr(40)
    email_address: types.TruncatedSafeStr(50)
    mobile_phone: str

    contact_name: types.TruncatedSafeMaybeStr(30)
    telephone: str | None = None
    fax: str | None = None

    senders_name: types.TruncatedSafeMaybeStr(25)
    notifications: pf_lists.Notifications | None = None


class PAF(pf_shared.BasePFType):
    postcode: str | None = None
    count: int | None = pyd.Field(None)
    specified_neighbour: list[pf_lists.SpecifiedNeighbour | None] = pyd.Field(None, description="")


class Department(pf_shared.BasePFType):
    department_id: list[int | None] = pyd.Field(None, description="")
    service_codes: list[pf_lists.ServiceCodes | None] = pyd.Field(None, description="")
    nominated_delivery_date_list: pf_lists.NominatedDeliveryDatelist | None = None


class Parcel(pf_shared.BasePFType):
    weight: float | None = None
    length: int | None = None
    height: int | None = None
    width: int | None = None
    purpose_of_shipment: str | None = None
    invoice_number: str | None = None
    export_license_number: str | None = None
    certificate_number: str | None = None
    content_details: pf_lists.ContentDetails | None = None
    shipping_cost: float | None = None


class ParcelLabelData(pf_shared.BasePFType):
    parcel_number: str | None = None
    shipment_number: str | None = None
    journey_leg: str | None = None
    label_data: pf_lists.LabelData | None = None
    barcodes: pf_lists.Barcodes | None = None
    images: pf_lists.Images | None = None
    parcel_contents: list[pf_lists.ParcelContents | None] = pyd.Field(None, description="")


class CompletedManifestInfo(pf_shared.BasePFType):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: pf_lists.ManifestShipments


class CompletedShipmentInfoCreatePrint(pf_shared.BasePFType):
    lead_shipment_number: str | None = None
    shipment_number: str | None = None
    delivery_date: str | None = None
    status: str
    completed_shipments: pf_lists.CompletedShipments


class CompletedShipmentInfo(pf_shared.BasePFType):
    lead_shipment_number: str | None = None
    delivery_date: dt.date | None = None
    status: str | None = None
    completed_shipments: pf_lists.CompletedShipments | None = None


class CollectionInfo(pf_shared.BasePFType):
    collection_contact: Contact
    collection_address: pf_ext.AddressRecipient
    collection_time: pf_shared.DateTimeRange | None = None


class RequestedShipmentMinimum(pf_shared.BasePFType):
    recipient_contact: Contact
    recipient_address: pf_ext.AddressRecipient
    contract_number: str
    total_number_of_parcels: int
    shipping_date: dt.date
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    shipment_type: types.DeliveryKind = 'DELIVERY'
    department_id: int = types.DepartmentNum

    @classmethod
    def from_minimal(
            cls,
            ship_date: dt.date,
            contact: Contact,
            address: pf_ext.AddressRecipient,
            num_parcels: int = 1,
    ):
        contract_no = os.environ.get("PF_CONT_NUM_1")

        return cls(
            department_id=types.DepartmentNum.MAIN,
            shipment_type=types.DeliveryKind.DELIVERY,
            contract_number=contract_no,
            service_code=pf_shared.ServiceCode.EXPRESS24,
            shipping_date=ship_date,
            recipient_contact=contact,
            recipient_address=address,
            total_number_of_parcels=num_parcels,
        )


class RequestedShipmentSimple(RequestedShipmentMinimum):
    job_reference: str | None = None
    # todo validate both or none for sender
    sender_contact: Contact | None = None
    sender_address: pf_ext.AddressRecipient | None = None
    total_shipment_weight: float | None = None
    enhancement: pf_shared.Enhancement | None = None
    delivery_options: pf_ext.DeliveryOptions | None = None
    collection_info: CollectionInfo | None = None


class Parcels(pf_shared.BasePFType):
    parcel: list[Parcel]


class ShipmentLabelData(pf_shared.BasePFType):
    parcel_label_data: list[ParcelLabelData]


class CompletedManifests(pf_shared.BasePFType):
    completed_manifest_info: list[CompletedManifestInfo]


class Departments(pf_shared.BasePFType):
    department: list[Department] = pyd.Field(default_factory=list)


class NominatedDeliveryDates(pf_shared.BasePFType):
    service_code: str | None = None
    departments: Departments | None = None


class PostcodeExclusion(pf_shared.BasePFType):
    delivery_postcode: str | None = None
    collection_postcode: str | None = None
    departments: Departments | None = None


class InternationalInfo(pf_shared.BasePFType):
    parcels: Parcels | None = None
    exporter_customs_reference: str | None = None
    recipient_importer_vat_no: str | None = None
    original_export_shipment_no: str | None = None
    documents_only: bool | None = None
    documents_description: str | None = None
    value_under200_us_dollars: bool | None = None
    shipment_description: str | None = None
    comments: str | None = None
    invoice_date: str | None = None
    terms_of_delivery: str | None = None
    purchase_order_ref: str | None = None


class RequestedShipmentComplex(RequestedShipmentSimple):
    hazardous_goods: pf_lists.HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: types.DropOffInd | None = None
    exchange_instructions1: pyd.constr(max_length=25) | None = None
    exchange_instructions2: pyd.constr(max_length=25) | None = None
    exchange_instructions3: pyd.constr(max_length=25) | None = None
    exporter_address: pf_ext.AddressRecipient | None = None
    exporter_contact: Contact | None = None
    importer_address: pf_ext.AddressRecipient | None = None
    importer_contact: Contact | None = None
    in_bound_address: pf_ext.AddressRecipient | None = None
    in_bound_contact: Contact | None = None
    in_bound_details: pf_ext.InBoundDetails | None = None
    international_info: InternationalInfo | None = None
    pre_printed: bool | None = None
    print_own_label: bool | None = None
    reference_number1: pyd.constr(max_length=24) | None = None
    reference_number2: pyd.constr(max_length=24) | None = None
    reference_number3: pyd.constr(max_length=24) | None = None
    reference_number4: pyd.constr(max_length=24) | None = None
    reference_number5: pyd.constr(max_length=24) | None = None
    request_id: int | None = None
    returns: pf_shared.Returns | None = None
    special_instructions1: pyd.constr(max_length=25) | None = None
    special_instructions2: pyd.constr(max_length=25) | None = None
    special_instructions3: pyd.constr(max_length=25) | None = None
    special_instructions4: pyd.constr(max_length=25) | None = None
