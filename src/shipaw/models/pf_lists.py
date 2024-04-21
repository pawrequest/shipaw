import pydantic as _p
import sqlmodel as sqm

from . import pf_ext, pf_shared


class HazardousGoods(pf_shared.BasePFType):
    hazardous_good: list[pf_shared.HazardousGood]


class ContentDetails(pf_shared.BasePFType):
    content_detail: list[pf_shared.ContentDetail]


class ParcelContents(pf_shared.BasePFType):
    item: list[pf_shared.ContentData]


class LabelData(pf_shared.BasePFType):
    item: list[pf_shared.LabelItem]


class Barcodes(pf_shared.BasePFType):
    barcode: list[pf_shared.Barcode]


class Images(pf_shared.BasePFType):
    image: list[pf_shared.Image]


class ManifestShipments(pf_shared.BasePFType):
    manifest_shipment: list[pf_shared.ManifestShipment]


class CompletedShipments(pf_shared.BasePFType):
    completed_shipment: list[pf_shared.CompletedShipment] = sqm.Field(default_factory=list)


class CompletedCancel(pf_shared.BasePFType):
    completed_cancel_info: pf_shared.CompletedCancelInfo | None = None


class Alerts(pf_shared.BasePFType):
    alert: list[pf_shared.Alert]


class CollectionNotifications(pf_shared.BasePFType):
    notification_type: list[pf_shared.CollectionNotificationType] = _p.Field(
        default_factory=list
    )

    @classmethod
    def standard_coll(cls):
        return cls(
            notification_type=[
                pf_shared.CollectionNotificationType.EMAIL,
                # pf_shared.CollectionNotificationType.SMS_RECIEVED,
                # pf_shared.CollectionNotificationType.EMAIL_RECIEVED,
            ]
        )


class RecipientNotifications(pf_shared.BasePFType):
    notification_type: list[pf_shared.NotificationType] = _p.Field(
        default_factory=list
    )

    @classmethod
    def standard_recip(cls):
        return cls(
            notification_type=[
                pf_shared.NotificationType.EMAIL,
                pf_shared.NotificationType.SMS_DOD,
                pf_shared.NotificationType.DELIVERY,
            ]
        )


class NominatedDeliveryDatelist(pf_shared.BasePFType):
    nominated_delivery_date: list[str] = _p.Field(default_factory=list)


class SafePlacelist(pf_shared.BasePFType):
    safe_place: list[str] = _p.Field(default_factory=list)


class ServiceCodes(pf_shared.BasePFType):
    service_code: list[str] = _p.Field(default_factory=list)


class SpecifiedNeighbour(pf_shared.BasePFType):
    address: list[pf_ext.AddTypes] = _p.Field(default_factory=list)
