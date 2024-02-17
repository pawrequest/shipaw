from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from shipr.models.pf_types import ContentDetails


class Parcels(BaseModel):
    Parcel: List[Parcel] = Field(..., description='')


class Parcel(BaseModel):
    Weight: Optional[float] = None
    Length: Optional[int] = None
    Height: Optional[int] = None
    Width: Optional[int] = None
    PurposeOfShipment: Optional[str] = None
    InvoiceNumber: Optional[str] = None
    ExportLicenseNumber: Optional[str] = None
    CertificateNumber: Optional[str] = None
    ContentDetails: Optional[ContentDetails] = None
    ShippingCost: Optional[float] = None
