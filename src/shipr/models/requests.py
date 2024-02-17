from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from shipr.models.pf_types import (
    Authentication,
    DateTimeRange,
    ConvenientCollect,
    SpecifiedPostOffice, PAF, NominatedDeliveryDates, PostcodeExclusion, RequestedShipment,
)
from shipr.models.documents import PrintType


class BaseRequest(BaseModel):
    Authentication: Authentication


class PrintLabelRequest(BaseRequest):
    ShipmentNumber: str
    PrintFormat: Optional[str] = None
    BarcodeFormat: Optional[str] = None
    PrintType: Optional[PrintType] = None


class PrintDocumentRequest(BaseRequest):
    ShipmentNumber: str
    DocumentType: int
    PrintFormat: Optional[str] = None


class CreateManifestRequest(BaseRequest):
    DepartmentId: Optional[int] = None


class PrintManifestRequest(BaseRequest):
    ManifestNumber: str
    PrintFormat: Optional[str] = None


class ReturnShipmentRequest(BaseRequest):
    ShipmentNumber: str
    CollectionTime: DateTimeRange


class CCReserveRequest(BaseRequest):
    BookingReference: str


class CancelShipmentRequest(BaseRequest):
    ShipmentNumber: str


class CancelShipmentRequest1(BaseModel):
    CancelShipmentRequest: CancelShipmentRequest


class CCReserveRequest1(BaseModel):
    CCReserveRequest: CCReserveRequest


class CreateManifestRequest1(BaseModel):
    CreateManifestRequest: CreateManifestRequest


class PrintDocumentRequest1(BaseModel):
    PrintDocumentRequest: PrintDocumentRequest


class PrintLabelRequest1(BaseModel):
    PrintLabelRequest: PrintLabelRequest


class PrintManifestRequest1(BaseModel):
    PrintManifestRequest: PrintManifestRequest


class ReturnShipmentRequest1(BaseModel):
    ReturnShipmentRequest: ReturnShipmentRequest


class FindRequest(BaseRequest):
    ConvenientCollect: Optional[ConvenientCollect] = None
    SpecifiedPostOffice: Optional[SpecifiedPostOffice] = None
    PAF: Optional[PAF] = None
    SafePlaces: Optional[bool] = None
    NominatedDeliveryDates: Optional[NominatedDeliveryDates] = None
    PostcodeExclusion: Optional[PostcodeExclusion] = None


class FindRequest1(BaseModel):
    FindRequest: FindRequest


class CreateShipmentRequest(BaseRequest):
    RequestedShipment: RequestedShipment


class CreatePrintRequest(BaseRequest):
    RequestedShipment: RequestedShipment


class CreatePrintRequest1(BaseModel):
    CreatePrintRequest: CreatePrintRequest


class CreateShipmentRequest1(BaseModel):
    CreateShipmentRequest: CreateShipmentRequest
