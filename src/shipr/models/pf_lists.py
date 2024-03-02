# from __future__ import annotations

# if _ty.TYPE_CHECKING:
#     pass

import sqlmodel as sqm
import pydantic as pyd

from shipr.models import (
    pf_ext,
    pf_shared,
    pf_simple,
)


class HazardousGoods(pf_shared.BasePFType):
    hazardous_good: list[pf_simple.HazardousGood]


class ContentDetails(pf_shared.BasePFType):
    content_detail: list[pf_simple.ContentDetail]


class ParcelContents(pf_shared.BasePFType):
    item: list[pf_simple.ContentData]


class LabelData(pf_shared.BasePFType):
    item: list[pf_simple.LabelItem]


class Barcodes(pf_shared.BasePFType):
    barcode: list[pf_simple.Barcode]


class Images(pf_shared.BasePFType):
    image: list[pf_simple.Image]


class ManifestShipments(pf_shared.BasePFType):
    manifest_shipment: list[pf_simple.ManifestShipment]


class CompletedShipments(pf_shared.BasePFType):
    completed_shipment: list[pf_simple.CompletedShipment] = sqm.Field(default_factory=list)


class CompletedCancel(pf_shared.BasePFType):
    completed_cancel_info: pf_simple.CompletedCancelInfo | None = None


class Alerts(pf_shared.BasePFType):
    alert: list[pf_simple.Alert]


class Notifications(pf_shared.BasePFType):
    notification_type: list[str] = pyd.Field(default_factory=list)


class NominatedDeliveryDatelist(pf_shared.BasePFType):
    nominated_delivery_date: list[str] = pyd.Field(default_factory=list)


class SafePlacelist(pf_shared.BasePFType):
    safe_place: list[str] = pyd.Field(default_factory=list)


class ServiceCodes(pf_shared.BasePFType):
    service_code: list[str] = pyd.Field(default_factory=list)


class SpecifiedNeighbour(pf_shared.BasePFType):
    address: list[pf_ext.AddressRecipient] = pyd.Field(default_factory=list)
