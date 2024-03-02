from __future__ import annotations

from pathlib import Path
from typing import Optional

from pawsupport import convert_print_silent2
from shipr.models.pf_shared import AlertType, BasePFType


class Enhancement(BasePFType):
    enhanced_compensation: Optional[str] = None
    saturday_delivery_required: Optional[bool] = None


class HazardousGood(BasePFType):
    lqdgun_code: Optional[str] = None
    lqdg_description: Optional[str] = None
    lqdg_volume: Optional[float] = None
    firearms: Optional[str] = None


class Returns(BasePFType):
    returns_email: Optional[str] = None
    email_message: Optional[str] = None
    email_label: bool


class ContentDetail(BasePFType):
    country_of_manufacture: str
    country_of_origin: Optional[str] = None
    manufacturers_name: Optional[str] = None
    description: str
    unit_weight: float
    unit_quantity: int
    unit_value: float
    currency: str
    tariff_code: Optional[str] = None
    tariff_description: Optional[str] = None
    article_reference: Optional[str] = None


class DateTimeRange(BasePFType):
    from_: str
    to: str


class ContentData(BasePFType):
    name: str
    data: str


class LabelItem(BasePFType):
    name: str
    data: str


class Barcode(BasePFType):
    name: str
    data: str


class Image(BasePFType):
    name: str
    data: str


class ManifestShipment(BasePFType):
    shipment_number: str
    service_code: str


class CompletedShipment(BasePFType):
    shipment_number: Optional[str] = None
    out_bound_shipment_number: Optional[str] = None
    in_bound_shipment_number: Optional[str] = None
    partner_number: Optional[str] = None


class CompletedCancelInfo(BasePFType):
    status: Optional[str] = None
    shipment_number: Optional[str] = None


class Position(BasePFType):
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class Document(BasePFType):
    data: bytes

    def download(self, outpath: Path = Path("label_out.pdf")) -> Path:
        with open(outpath, "wb") as f:
            f.write(self.data)
        return Path(outpath)

    def print_doc_arrayed(self):
        output = self.download()
        convert_print_silent2(output)


class Alert(BasePFType):
    code: int
    message: str
    type: AlertType


__all__ = [
    "Enhancement",
    "HazardousGood",
    "Returns",
    "ContentDetail",
    "DateTimeRange",
    "ContentData",
    "LabelItem",
    "Barcode",
    "Image",
    "ManifestShipment",
    "CompletedShipment",
    "CompletedCancelInfo",
    "Position",
    "Document",
    "Alert",
]
