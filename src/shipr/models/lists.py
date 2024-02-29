from __future__ import annotations

from typing import Optional

import pydantic
from pydantic import Field

from shipr.models import shipr_shared as shared, simple_models as sm


class HazardousGoods(shared.BasePFType):
    hazardous_good: list[sm.HazardousGood] = Field(..., description="")


class ContentDetails(shared.BasePFType):
    content_detail: list[sm.ContentDetail] = Field(..., description="")


class ParcelContents(shared.BasePFType):
    item: list[sm.ContentData] = Field(..., description="")


class LabelData(shared.BasePFType):
    item: list[sm.LabelItem] = Field(..., description="")


class Barcodes(shared.BasePFType):
    barcode: list[sm.Barcode] = Field(..., description="")


class Images(shared.BasePFType):
    image: list[sm.Image] = Field(..., description="")


class ManifestShipments(shared.BasePFType):
    manifest_shipment: list[sm.ManifestShipment] = Field(..., description="")


class CompletedShipments(shared.BasePFType):
    completed_shipment: list[sm.CompletedShipment] = Field(..., description="")


class CompletedCancel(shared.BasePFType):
    completed_cancel_info: Optional[sm.CompletedCancelInfo] = None


class Alerts(shared.BasePFType):
    alert: list[sm.Alert]


class Notifications(shared.BasePFType):
    notification_type: list[str] = pydantic.Field(default_factory=list)


class NominatedDeliveryDatelist(shared.BasePFType):
    nominated_delivery_date: Optional[list[str]] = Field(None, description="")


class Parcels(shared.BasePFType):
    parcel: list[Parcel] = Field(..., description="")


class ShipmentLabelData(shared.BasePFType):
    parcel_label_data: list[ParcelLabelData] = Field(..., description="")


class CompletedManifests(shared.BasePFType):
    completed_manifest_info: list[CompletedManifestInfo] = Field(..., description="")


class Departments(shared.BasePFType):
    department: Optional[list[Department]] = Field(None, description="")


class SafePlacelist(shared.BasePFType):
    safe_place: Optional[list[str]] = Field(None, description="")


class ServiceCodes(shared.BasePFType):
    service_code: Optional[list[str]] = Field(None, description="")
