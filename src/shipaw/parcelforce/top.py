import datetime as dt
import typing as _t

import pydantic
from pawdantic import paw_types
from pydantic import constr

# from shipaw.parcelforce.pf_shipment import Shipment as PFShipment
from shipaw.agnostic import ship_types
from shipaw.agnostic.ship_types import MyPhone
from shipaw.parcelforce.lists import (
    Barcodes,
    CollectionNotifications,
    CompletedShipments,
    ContentDetails,
    HazardousGoods,
    Images,
    LabelData,
    ManifestShipments,
    NominatedDeliveryDatelist,
    ParcelContents,
    RecipientNotifications,
    ServiceCodes,
    SpecifiedNeighbour,
)
from shipaw.parcelforce.models import AddTypes, AddressCollection, AddressRecipient, DeliveryOptions, InBoundDetails
from shipaw.parcelforce.shared import DateTimeRange, Enhancement, PFBaseModel, Returns, ServiceCode


class Contact(PFBaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    # business_name: constr(max_length=40)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: paw_types.truncated_printable_str_type(30)
    # contact_name: constr(max_length=30)
    notifications: RecipientNotifications | None = RecipientNotifications.standard_recip()

    @property
    def notifications_str(self) -> str:
        msg = f'Recip Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg


class ContactCollection(Contact):
    senders_name: paw_types.optional_truncated_printable_str_type(25)
    # senders_name: constr(max_length=25) | None = None
    telephone: MyPhone | None = None
    notifications: CollectionNotifications | None = CollectionNotifications.standard_coll()

    @property
    def notifications_str(self) -> str:
        msg = f'Collecton Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @pydantic.model_validator(mode='after')
    def tel_is_none(self):
        if not self.telephone:
            self.telephone = self.mobile_phone
        return self

    # @classmethod
    # def from_contact(cls, contact: Contact):
    #     return cls(
    #         **contact.model_dump(exclude={'notifications'}),
    #         senders_name=contact.contact_name,


class ContactSender(Contact):
    business_name: paw_types.optional_truncated_printable_str_type(25)
    # business_name: constr(max_length=25)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: paw_types.optional_truncated_printable_str_type(25)

    telephone: MyPhone | None = None
    senders_name: paw_types.optional_truncated_printable_str_type(25) | None = None
    notifications: None = None


class ContactTemporary(Contact):
    business_name: str = ''
    contact_name: str = ''
    mobile_phone: MyPhone | None = None
    email_address: str = ''
    telephone: MyPhone | None = None
    senders_name: str = ''

    @pydantic.model_validator(mode='after')
    def fake(self):
        for field, value in self.model_dump().items():
            if not value:
                value = '========='
                if field == 'email_address':
                    value = f'{value}@f======f.com'
                setattr(self, field, value)
        return self


class PAF(PFBaseModel):
    postcode: str | None = None
    count: int | None = pydantic.Field(None)
    specified_neighbour: list[SpecifiedNeighbour] = pydantic.Field(default_factory=list, description='')


class Department(PFBaseModel):
    department_id: list[int | None] = pydantic.Field(None, description='')
    service_codes: list[ServiceCodes | None] = pydantic.Field(None, description='')
    nominated_delivery_date_list: NominatedDeliveryDatelist | None = None


class Parcel(PFBaseModel):
    weight: float | None = None
    length: int | None = None
    height: int | None = None
    width: int | None = None
    purpose_of_shipment: str | None = None
    invoice_number: str | None = None
    export_license_number: str | None = None
    certificate_number: str | None = None
    content_details: ContentDetails | None = None
    shipping_cost: float | None = None


class ParcelLabelData(PFBaseModel):
    parcel_number: str | None = None
    shipment_number: str | None = None
    journey_leg: str | None = None
    label_data: LabelData | None = None
    barcodes: Barcodes | None = None
    images: Images | None = None
    parcel_contents: list[ParcelContents | None] = pydantic.Field(None, description='')


class CompletedManifestInfo(PFBaseModel):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: ManifestShipments


class CompletedShipmentInfoCreatePrint(PFBaseModel):
    lead_shipment_number: str | None = None
    shipment_number: str | None = None
    delivery_date: str | None = None
    status: str
    completed_shipments: CompletedShipments


class CompletedShipmentInfo(PFBaseModel):
    lead_shipment_number: str | None = None
    delivery_date: dt.date | None = None
    status: str | None = None
    completed_shipments: CompletedShipments | None = None


class CollectionInfo(PFBaseModel):
    collection_contact: ContactCollection
    collection_address: AddressCollection
    collection_time: DateTimeRange


class CollectionStateProtocol(_t.Protocol):
    contact: Contact
    address: AddressCollection
    ship_date: dt.date


# def collection_info_from_state(state: CollectionStateProtocol):
#     col_contact_ = ContactCollection(**state.contact.model_dump(exclude={'notifications'}))
#     col_contact = col_contact_.model_validate(col_contact_)
#     info = CollectionInfo(
#         collection_contact=col_contact,
#         collection_address=state.address,
#         collection_time=DateTimeRange.from_datetimes(
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_FROM),
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_TO)
#         )
#     )
#     return info.model_validate(info)


class RequestedShipmentZero(PFBaseModel):
    recipient_contact: Contact
    recipient_address: AddTypes
    total_number_of_parcels: int = pydantic.Field(..., description='Number of parcels in the shipment')
    shipping_date: dt.date


class RequestedShipmentMinimum(RequestedShipmentZero):
    recipient_contact: Contact

    contract_number: str
    department_id: int = ship_types.DepartmentNum

    shipment_type: ship_types.ShipmentType = 'DELIVERY'
    service_code: ServiceCode = ServiceCode.EXPRESS24
    reference_number1: paw_types.optional_truncated_printable_str_type(24)  # first 14 visible on label

    special_instructions1: pydantic.constr(max_length=25) | None = None
    special_instructions2: pydantic.constr(max_length=25) | None = None

    @pydantic.field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').delivery_contact_business
        return v


class CollectionMinimum(RequestedShipmentMinimum):
    shipment_type: ship_types.ShipmentType = 'COLLECTION'
    print_own_label: bool = True
    collection_info: CollectionInfo


class RequestedShipmentSimple(RequestedShipmentMinimum):
    enhancement: Enhancement | None = None
    delivery_options: DeliveryOptions | None = None


class Parcels(PFBaseModel):
    parcel: list[Parcel]


class ShipmentLabelData(PFBaseModel):
    parcel_label_data: list[ParcelLabelData]


class CompletedManifests(PFBaseModel):
    completed_manifest_info: list[CompletedManifestInfo]


class Departments(PFBaseModel):
    department: list[Department] = pydantic.Field(default_factory=list)


class NominatedDeliveryDates(PFBaseModel):
    service_code: str | None = None
    departments: Departments | None = None


class PostcodeExclusion(PFBaseModel):
    delivery_postcode: str | None = None
    collection_postcode: str | None = None
    departments: Departments | None = None


class InternationalInfo(PFBaseModel):
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
    hazardous_goods: HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: ship_types.DropOffInd | None = None
    exchange_instructions1: pydantic.constr(max_length=25) | None = None
    exchange_instructions2: pydantic.constr(max_length=25) | None = None
    exchange_instructions3: pydantic.constr(max_length=25) | None = None
    exporter_address: AddressRecipient | None = None
    exporter_contact: Contact | None = None
    importer_address: AddressRecipient | None = None
    importer_contact: Contact | None = None
    in_bound_address: AddressRecipient | None = None
    in_bound_contact: Contact | None = None
    in_bound_details: InBoundDetails | None = None
    international_info: InternationalInfo | None = None
    pre_printed: bool | None = None
    print_own_label: bool | None = None
    reference_number1: pydantic.constr(max_length=24) | None = None
    reference_number2: pydantic.constr(max_length=24) | None = None
    reference_number3: pydantic.constr(max_length=24) | None = None
    reference_number4: pydantic.constr(max_length=24) | None = None
    reference_number5: pydantic.constr(max_length=24) | None = None
    request_id: int | None = None
    returns: Returns | None = None
    special_instructions1: pydantic.constr(max_length=25) | None = None
    special_instructions2: pydantic.constr(max_length=25) | None = None
    special_instructions3: pydantic.constr(max_length=25) | None = None
    special_instructions4: pydantic.constr(max_length=25) | None = None

    # job_reference: str | None = None  # not required for domestic
    # sender_contact: Contact | None = None
    # sender_address: AddressSender | None = None
    # total_shipment_weight: float | None = None
    # enhancement: Enhancement | None = None
    # delivery_options: DeliveryOptions | None = None


