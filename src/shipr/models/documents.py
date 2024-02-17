from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from shipr.models.pf_types import ParcelContents, ManifestShipments


class ShipmentLabelData(BaseModel):
    ParcelLabelData: List[ParcelLabelData] = Field(..., description='')


class CompletedManifests(BaseModel):
    CompletedManifestInfo: List[CompletedManifestInfo] = Field(..., description='')


class LabelItem(BaseModel):
    Name: str
    Data: str


class Barcode(BaseModel):
    Name: str
    Data: str


class Image(BaseModel):
    Name: str
    Data: str


class PrintType(Enum):
    ALL_PARCELS = 'ALL_PARCELS'
    SINGLE_PARCEL = 'SINGLE_PARCEL'


class Document(BaseModel):
    Data: str


class LabelData(BaseModel):
    Item: List[LabelItem] = Field(..., description='')


class Barcodes(BaseModel):
    Barcode: List[Barcode] = Field(..., description='')


class Images(BaseModel):
    Image: List[Image] = Field(..., description='')


class ParcelLabelData(BaseModel):
    ParcelNumber: Optional[str] = None
    ShipmentNumber: Optional[str] = None
    JourneyLeg: Optional[str] = None
    LabelData: Optional[LabelData] = None
    Barcodes: Optional[Barcodes] = None
    Images: Optional[Images] = None
    ParcelContents: Optional[List[ParcelContents]] = Field(None, description='')


class CompletedManifestInfo(BaseModel):
    DepartmentId: int
    ManifestNumber: str
    ManifestType: str
    TotalShipmentCount: int
    ManifestShipments: ManifestShipments
