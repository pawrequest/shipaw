import datetime as dt
import typing as _t

import pydantic as _p
from pawdantic import paw_types
from pydantic import constr

from .. import ship_types
from . import pf_lists, pf_models, pf_shared
from ..ship_types import MyPhone


class Contact(pf_shared.PFBaseModel):
    business_name: constr(max_length=40)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: constr(max_length=30)
    notifications: pf_lists.RecipientNotifications | None = pf_lists.RecipientNotifications.standard_recip()


class ContactCollection(Contact):
    senders_name: constr(max_length=25) | None = None
    telephone: MyPhone | None = None
    notifications: pf_lists.CollectionNotifications | None = pf_lists.CollectionNotifications.standard_coll()

    @_p.field_validator('telephone', mode='after')
    def tel_is_none(cls, v, values):
        if not v:
            v = values.data.get('mobile_phone')
        return v

    # @classmethod
    # def from_contact(cls, contact: Contact):
    #     return cls(
    #         **contact.model_dump(exclude={'notifications'}),
    #         senders_name=contact.contact_name,


class ContactSender(Contact):
    business_name: constr(max_length=25)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: constr(max_length=25)

    telephone: MyPhone | None = None
    senders_name: constr(max_length=25) | None = None
    notifications: None = None


class ContactTemporary(Contact):
    business_name: str = ''
    contact_name: str = ''
    mobile_phone: MyPhone | None = None
    email_address: str = ''
    telephone: MyPhone | None = None
    senders_name: str = ''

    @_p.model_validator(mode='after')
    def fake(self):
        for field, value in self.model_dump().items():
            if not value:
                value = '========='
                if field == 'email_address':
                    value = f'{value}@f======f.com'
                setattr(self, field, value)
        return self


class PAF(pf_shared.PFBaseModel):
    postcode: str | None = None
    count: int | None = _p.Field(None)
    specified_neighbour: list[pf_lists.SpecifiedNeighbour] = _p.Field(default_factory=list, description='')


class Department(pf_shared.PFBaseModel):
    department_id: list[int | None] = _p.Field(None, description='')
    service_codes: list[pf_lists.ServiceCodes | None] = _p.Field(None, description='')
    nominated_delivery_date_list: pf_lists.NominatedDeliveryDatelist | None = None


class Parcel(pf_shared.PFBaseModel):
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


class ParcelLabelData(pf_shared.PFBaseModel):
    parcel_number: str | None = None
    shipment_number: str | None = None
    journey_leg: str | None = None
    label_data: pf_lists.LabelData | None = None
    barcodes: pf_lists.Barcodes | None = None
    images: pf_lists.Images | None = None
    parcel_contents: list[pf_lists.ParcelContents | None] = _p.Field(None, description='')


class CompletedManifestInfo(pf_shared.PFBaseModel):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: pf_lists.ManifestShipments


class CompletedShipmentInfoCreatePrint(pf_shared.PFBaseModel):
    lead_shipment_number: str | None = None
    shipment_number: str | None = None
    delivery_date: str | None = None
    status: str
    completed_shipments: pf_lists.CompletedShipments


class CompletedShipmentInfo(pf_shared.PFBaseModel):
    lead_shipment_number: str | None = None
    delivery_date: dt.date | None = None
    status: str | None = None
    completed_shipments: pf_lists.CompletedShipments | None = None


class CollectionInfo(pf_shared.PFBaseModel):
    collection_contact: ContactCollection
    collection_address: pf_models.AddressCollection
    collection_time: pf_shared.DateTimeRange


class CollectionStateProtocol(_t.Protocol):
    contact: Contact
    address: pf_models.AddressCollection
    ship_date: dt.date


# def collection_info_from_state(state: CollectionStateProtocol):
#     col_contact_ = ContactCollection(**state.contact.model_dump(exclude={'notifications'}))
#     col_contact = col_contact_.model_validate(col_contact_)
#     info = CollectionInfo(
#         collection_contact=col_contact,
#         collection_address=state.address,
#         collection_time=pf_shared.DateTimeRange.from_datetimes(
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_FROM),
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_TO)
#         )
#     )
#     return info.model_validate(info)


class RequestedShipmentZero(pf_shared.PFBaseModel):
    recipient_contact: Contact
    recipient_address: pf_models.AddTypes
    total_number_of_parcels: int = _p.Field(..., description='Number of parcels in the shipment')
    shipping_date: dt.date


class RequestedShipmentMinimum(RequestedShipmentZero):
    recipient_contact: Contact

    contract_number: str
    department_id: int = ship_types.DepartmentNum

    shipment_type: ship_types.ShipmentType = 'DELIVERY'
    service_code: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    reference_number1: paw_types.optional_truncated_printable_str_type(24)  # first 14 visible on label

    special_instructions1: _p.constr(max_length=25) | None = None
    special_instructions2: _p.constr(max_length=25) | None = None

    @_p.field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').business_name
        return v


class CollectionMinimum(RequestedShipmentMinimum):
    shipment_type: ship_types.ShipmentType = 'COLLECTION'
    print_own_label: bool = True
    collection_info: CollectionInfo


class RequestedShipmentSimple(RequestedShipmentMinimum):
    enhancement: pf_shared.Enhancement | None = None
    delivery_options: pf_models.DeliveryOptions | None = None


class Parcels(pf_shared.PFBaseModel):
    parcel: list[Parcel]


class ShipmentLabelData(pf_shared.PFBaseModel):
    parcel_label_data: list[ParcelLabelData]


class CompletedManifests(pf_shared.PFBaseModel):
    completed_manifest_info: list[CompletedManifestInfo]


class Departments(pf_shared.PFBaseModel):
    department: list[Department] = _p.Field(default_factory=list)


class NominatedDeliveryDates(pf_shared.PFBaseModel):
    service_code: str | None = None
    departments: Departments | None = None


class PostcodeExclusion(pf_shared.PFBaseModel):
    delivery_postcode: str | None = None
    collection_postcode: str | None = None
    departments: Departments | None = None


class InternationalInfo(pf_shared.PFBaseModel):
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
    drop_off_ind: ship_types.DropOffInd | None = None
    exchange_instructions1: _p.constr(max_length=25) | None = None
    exchange_instructions2: _p.constr(max_length=25) | None = None
    exchange_instructions3: _p.constr(max_length=25) | None = None
    exporter_address: pf_models.AddressRecipient | None = None
    exporter_contact: Contact | None = None
    importer_address: pf_models.AddressRecipient | None = None
    importer_contact: Contact | None = None
    in_bound_address: pf_models.AddressRecipient | None = None
    in_bound_contact: Contact | None = None
    in_bound_details: pf_models.InBoundDetails | None = None
    international_info: InternationalInfo | None = None
    pre_printed: bool | None = None
    print_own_label: bool | None = None
    reference_number1: _p.constr(max_length=24) | None = None
    reference_number2: _p.constr(max_length=24) | None = None
    reference_number3: _p.constr(max_length=24) | None = None
    reference_number4: _p.constr(max_length=24) | None = None
    reference_number5: _p.constr(max_length=24) | None = None
    request_id: int | None = None
    returns: pf_shared.Returns | None = None
    special_instructions1: _p.constr(max_length=25) | None = None
    special_instructions2: _p.constr(max_length=25) | None = None
    special_instructions3: _p.constr(max_length=25) | None = None
    special_instructions4: _p.constr(max_length=25) | None = None

    # job_reference: str | None = None  # not required for domestic
    # sender_contact: Contact | None = None
    # sender_address: pf_models.AddressSender | None = None
    # total_shipment_weight: float | None = None
    # enhancement: pf_shared.Enhancement | None = None
    # delivery_options: pf_models.DeliveryOptions | None = None
