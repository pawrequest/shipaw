from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from shipr.models.pf_types import (
    PostOffice,
    CompletedShipmentInfo,
    CompletedReturnInfo,
    CompletedCancel,
    Alerts,
    ConvenientCollect,
    SpecifiedPostOffice,
    PAF,
    SafePlaceList,
    NominatedDeliveryDates,
    PostcodeExclusion, CompletedShipmentInfoCreatePrint,
)
from shipr.models.documents import ShipmentLabelData, CompletedManifests, Document


class BaseReply(BaseModel):
    Alerts: Optional[Alerts] = None


class CreatePrintReply(BaseReply):
    CompletedShipmentInfoCreatePrint: Optional[CompletedShipmentInfoCreatePrint] = None
    Label: Optional[Document] = None
    LabelData: Optional[ShipmentLabelData] = None
    PartnerCode: Optional[str] = None


class PrintLabelReply(BaseReply):
    Label: Optional[Document] = None
    LabelData: Optional[ShipmentLabelData] = None
    PartnerCode: Optional[str] = None


class PrintDocumentReply(BaseReply):
    Label: Optional[Document] = None
    LabelData: Optional[ShipmentLabelData] = None
    DocumentType: Optional[Document] = None


class CreateManifestReply(BaseReply):
    CompletedManifests: Optional[CompletedManifests] = None


class PrintManifestReply(BaseReply):
    Manifest: Optional[Document] = None


class ReturnShipmentReply(BaseReply):
    CompletedShipmentInfo: Optional[CompletedReturnInfo] = None


class CCReserveReply(BaseReply):
    PostOffice: Optional[PostOffice] = None


class CancelShipmentReply(BaseReply):
    CompletedCancel: Optional[CompletedCancel] = None


class CancelShipmentReply1(BaseModel):
    CancelShipmentReply: CancelShipmentReply


class CCReserveReply1(BaseModel):
    CCReserveReply: CCReserveReply


class CreateManifestReply1(BaseModel):
    CreateManifestReply: CreateManifestReply


class CreatePrintReply1(BaseModel):
    CreatePrintReply: CreatePrintReply


class PrintDocumentReply1(BaseModel):
    PrintDocumentReply: PrintDocumentReply


class PrintLabelReply1(BaseModel):
    PrintLabelReply: PrintLabelReply


class PrintManifestReply1(BaseModel):
    PrintManifestReply: PrintManifestReply


class ReturnShipmentReply1(BaseModel):
    ReturnShipmentReply: ReturnShipmentReply


class CreateShipmentReply(BaseReply):
    CompletedShipmentInfo: Optional[CompletedShipmentInfo] = None


class CreateShipmentReply1(BaseModel):
    CreateShipmentReply: CreateShipmentReply


class FindReply(BaseReply):
    ConvenientCollect: Optional[ConvenientCollect] = None
    SpecifiedPostOffice: Optional[SpecifiedPostOffice] = None
    PAF: Optional[PAF] = None
    SafePlaceList: Optional[SafePlaceList] = None
    NominatedDeliveryDates: Optional[NominatedDeliveryDates] = None
    PostcodeExclusion: Optional[PostcodeExclusion] = None


class FindReply1(BaseModel):
    FindReply: FindReply
