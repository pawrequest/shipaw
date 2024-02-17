from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from shipr.models.simple import Parcels


# DOCS


class NominatedDeliveryDates(BaseModel):
    ServiceCode: Optional[str] = None
    Departments: Optional[Departments] = None


class PostcodeExclusion(BaseModel):
    DeliveryPostcode: Optional[str] = None
    CollectionPostcode: Optional[str] = None
    Departments: Optional[Departments] = None


class PostOffice(BaseModel):
    PostOfficeID: Optional[str] = None
    Business: Optional[str] = None
    Address: Optional[Address] = None
    OpeningHours: Optional[OpeningHours] = None
    Distance: Optional[float] = None
    Availability: Optional[bool] = None
    Position: Optional[Position] = None
    BookingReference: Optional[str] = None


class InternationalInfo(BaseModel):
    Parcels: Optional[Parcels] = None
    ExporterCustomsReference: Optional[str] = None
    RecipientImporterVatNo: Optional[str] = None
    OriginalExportShipmentNo: Optional[str] = None
    DocumentsOnly: Optional[bool] = None
    DocumentsDescription: Optional[str] = None
    ValueUnder200USDollars: Optional[bool] = None
    ShipmentDescription: Optional[str] = None
    Comments: Optional[str] = None
    InvoiceDate: Optional[str] = None
    TermsOfDelivery: Optional[str] = None
    PurchaseOrderRef: Optional[str] = None


class ConvenientCollect(BaseModel):
    Postcode: Optional[str] = None
    PostOffice: Optional[List[PostOffice]] = Field(None, description='')
    Count: Optional[int] = None
    PostOfficeID: Optional[str] = None


class SpecifiedPostOffice(BaseModel):
    Postcode: Optional[str] = None
    PostOffice: Optional[List[PostOffice]] = Field(None, description='')
    Count: Optional[int] = None
    PostOfficeID: Optional[str] = None


class DeliveryOptions(BaseModel):
    ConvenientCollect: Optional[ConvenientCollect] = None
    IRTS: Optional[bool] = None
    Letterbox: Optional[bool] = None
    SpecifiedPostOffice: Optional[SpecifiedPostOffice] = None
    SpecifiedNeighbour: Optional[str] = None
    SafePlace: Optional[str] = None
    PIN: Optional[int] = None
    NamedRecipient: Optional[bool] = None
    AddressOnly: Optional[bool] = None
    NominatedDeliveryDate: Optional[str] = None
    PersonalParcel: Optional[str] = None


class RequestedShipment(BaseModel):
    DepartmentId: Optional[int] = None
    ShipmentType: str
    ContractNumber: str
    RequestId: Optional[int] = None
    ServiceCode: str
    PrePrinted: Optional[bool] = None
    ShippingDate: Optional[str] = None
    JobReference: Optional[str] = None
    RecipientContact: Contact
    RecipientAddress: Address
    ImporterContact: Optional[Contact] = None
    ImporterAddress: Optional[Address] = None
    ExporterContact: Optional[Contact] = None
    ExporterAddress: Optional[Address] = None
    SenderContact: Optional[Contact] = None
    SenderAddress: Optional[Address] = None
    TotalNumberOfParcels: Optional[int] = None
    TotalShipmentWeight: Optional[float] = None
    Enhancement: Optional[Enhancement] = None
    DeliveryOptions: Optional[DeliveryOptions] = None
    HazardousGoods: Optional[HazardousGoods] = None
    Returns: Optional[Returns] = None
    DropOffInd: Optional[str] = None
    PrintOwnLabel: Optional[bool] = None
    CollectionInfo: Optional[CollectionInfo] = None
    InternationalInfo: Optional[InternationalInfo] = None
    ReferenceNumber1: Optional[str] = None
    ReferenceNumber2: Optional[str] = None
    ReferenceNumber3: Optional[str] = None
    ReferenceNumber4: Optional[str] = None
    ReferenceNumber5: Optional[str] = None
    SpecialInstructions1: Optional[str] = None
    SpecialInstructions2: Optional[str] = None
    SpecialInstructions3: Optional[str] = None
    SpecialInstructions4: Optional[str] = None
    InBoundContact: Optional[Contact] = None
    InBoundAddress: Optional[Address] = None
    InBoundDetails: Optional[InBoundDetails] = None
    ExchangeInstructions1: Optional[str] = None
    ExchangeInstructions2: Optional[str] = None
    ExchangeInstructions3: Optional[str] = None
    ConsignmentHandling: Optional[bool] = None


class CompletedShipmentInfo(BaseModel):
    LeadShipmentNumber: Optional[str] = None
    DeliveryDate: Optional[str] = None
    Status: str
    CompletedShipments: CompletedShipments
    RequestedShipment: RequestedShipment


class Notifications(BaseModel):
    NotificationType: List[str] = Field(..., description='')


class Address(BaseModel):
    AddressLine1: str
    AddressLine2: Optional[str] = None
    AddressLine3: Optional[str] = None
    Town: Optional[str] = None
    Postcode: Optional[str] = None
    Country: str


class Enhancement(BaseModel):
    EnhancedCompensation: Optional[str] = None
    SaturdayDeliveryRequired: Optional[bool] = None


class HazardousGood(BaseModel):
    LQDGUNCode: Optional[str] = None
    LQDGDescription: Optional[str] = None
    LQDGVolume: Optional[float] = None
    Firearms: Optional[str] = None


class Returns(BaseModel):
    ReturnsEmail: Optional[str] = None
    EmailMessage: Optional[str] = None
    EmailLabel: bool


class ContentDetail(BaseModel):
    CountryOfManufacture: str
    CountryOfOrigin: Optional[str] = None
    ManufacturersName: Optional[str] = None
    Description: str
    UnitWeight: float
    UnitQuantity: int
    UnitValue: float
    Currency: str
    TariffCode: Optional[str] = None
    TariffDescription: Optional[str] = None
    ArticleReference: Optional[str] = None


class DateTimeRange(BaseModel):
    From: str
    To: str


class ContentData(BaseModel):
    Name: str
    Data: str


class ManifestShipment(BaseModel):
    ShipmentNumber: str
    ServiceCode: str


class CompletedShipment(BaseModel):
    ShipmentNumber: Optional[str] = None
    OutBoundShipmentNumber: Optional[str] = None
    InBoundShipmentNumber: Optional[str] = None
    PartnerNumber: Optional[str] = None


class CompletedReturnInfo(BaseModel):
    Status: str
    ShipmentNumber: str
    CollectionTime: DateTimeRange


class Authentication(BaseModel):
    UserName: str
    Password: str


class CompletedCancelInfo(BaseModel):
    Status: Optional[str] = None
    ShipmentNumber: Optional[str] = None


class SpecifiedNeighbour(BaseModel):
    Address: Optional[List[Address]] = Field(None, description='')


class SafePlaceList(BaseModel):
    SafePlace: Optional[List[str]] = Field(None, description='')


class NominatedDeliveryDateList(BaseModel):
    NominatedDeliveryDate: Optional[List[str]] = Field(None, description='')


class ServiceCodes(BaseModel):
    ServiceCode: Optional[List[str]] = Field(None, description='')


class Hours(BaseModel):
    Open: Optional[str] = None
    Close: Optional[str] = None
    CloseLunch: Optional[str] = None
    AfterLunchOpening: Optional[str] = None


class Position(BaseModel):
    Longitude: Optional[float] = None
    Latitude: Optional[float] = None


class AlertType(Enum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Contact(BaseModel):
    BusinessName: str
    ContactName: Optional[str] = None
    EmailAddress: Optional[str] = None
    Telephone: Optional[str] = None
    Fax: Optional[str] = None
    MobilePhone: Optional[str] = None
    SendersName: Optional[str] = None
    Notifications: Optional[Notifications] = None


class InBoundDetails(BaseModel):
    ContractNumber: str
    ServiceCode: str
    TotalShipmentWeight: Optional[str] = None
    Enhancement: Optional[Enhancement] = None
    ReferenceNumber1: Optional[str] = None
    ReferenceNumber2: Optional[str] = None
    ReferenceNumber3: Optional[str] = None
    ReferenceNumber4: Optional[str] = None
    ReferenceNumber5: Optional[str] = None
    SpecialInstructions1: Optional[str] = None
    SpecialInstructions2: Optional[str] = None
    SpecialInstructions3: Optional[str] = None
    SpecialInstructions4: Optional[str] = None


class HazardousGoods(BaseModel):
    HazardousGood: List[HazardousGood] = Field(..., description='')


class ContentDetails(BaseModel):
    ContentDetail: List[ContentDetail] = Field(..., description='')


class CollectionInfo(BaseModel):
    CollectionContact: Contact
    CollectionAddress: Address
    CollectionTime: Optional[DateTimeRange] = None


class ParcelContents(BaseModel):
    Item: List[ContentData] = Field(..., description='')


class ManifestShipments(BaseModel):
    ManifestShipment: List[ManifestShipment] = Field(..., description='')


class CompletedShipments(BaseModel):
    CompletedShipment: List[CompletedShipment] = Field(..., description='')


class Alert(BaseModel):
    Code: int
    Message: str
    Type: AlertType


class CompletedCancel(BaseModel):
    CompletedCancelInfo: Optional[CompletedCancelInfo] = None


class PAF(BaseModel):
    Postcode: Optional[str] = None
    Count: Optional[int] = None
    SpecifiedNeighbour: Optional[List[SpecifiedNeighbour]] = Field(None, description='')


class Department(BaseModel):
    DepartmentID: Optional[List[int]] = Field(None, description='')
    ServiceCodes: Optional[List[ServiceCodes]] = Field(None, description='')
    NominatedDeliveryDateList: Optional[NominatedDeliveryDateList] = None


class Mon(BaseModel):
    Hours: Optional[Hours] = None


class Tue(BaseModel):
    Hours: Optional[Hours] = None


class Wed(BaseModel):
    Hours: Optional[Hours] = None


class Thu(BaseModel):
    Hours: Optional[Hours] = None


class Fri(BaseModel):
    Hours: Optional[Hours] = None


class Sat(BaseModel):
    Hours: Optional[Hours] = None


class Sun(BaseModel):
    Hours: Optional[Hours] = None


class BankHol(BaseModel):
    Hours: Optional[Hours] = None


class Alerts(BaseModel):
    Alert: List[Alert] = Field(..., description='')


class Departments(BaseModel):
    Department: Optional[List[Department]] = Field(None, description='')


class OpeningHours(BaseModel):
    Mon: Optional[Mon] = None
    Tue: Optional[Tue] = None
    Wed: Optional[Wed] = None
    Thu: Optional[Thu] = None
    Fri: Optional[Fri] = None
    Sat: Optional[Sat] = None
    Sun: Optional[Sun] = None
    BankHol: Optional[BankHol] = None


class CompletedShipmentInfoCreatePrint(BaseModel):
    LeadShipmentNumber: Optional[str] = None
    ShipmentNumber: Optional[str] = None
    DeliveryDate: Optional[str] = None
    Status: str
    CompletedShipments: CompletedShipments
