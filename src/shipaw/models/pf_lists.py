import pydantic as _p
import sqlmodel as sqm

from . import pf_models, pf_shared


class HazardousGoods(pf_shared.PFBaseModel):
    hazardous_good: list[pf_shared.HazardousGood]


class ContentDetails(pf_shared.PFBaseModel):
    content_detail: list[pf_shared.ContentDetail]


class ParcelContents(pf_shared.PFBaseModel):
    item: list[pf_shared.ContentData]


class LabelData(pf_shared.PFBaseModel):
    item: list[pf_shared.LabelItem]


class Barcodes(pf_shared.PFBaseModel):
    barcode: list[pf_shared.Barcode]


class Images(pf_shared.PFBaseModel):
    image: list[pf_shared.Image]


class ManifestShipments(pf_shared.PFBaseModel):
    manifest_shipment: list[pf_shared.ManifestShipment]


class CompletedShipments(pf_shared.PFBaseModel):
    completed_shipment: list[pf_shared.CompletedShipment] = sqm.Field(default_factory=list)


class CompletedCancel(pf_shared.PFBaseModel):
    completed_cancel_info: pf_shared.CompletedCancelInfo | None = None


class CollectionNotifications(pf_shared.PFBaseModel):
    notification_type: list[pf_shared.CollectionNotificationType] = _p.Field(default_factory=list)

    @classmethod
    def standard_coll(cls):
        return cls(
            notification_type=[
                pf_shared.CollectionNotificationType.EMAIL,
                # pf_shared.CollectionNotificationType.SMS_RECIEVED,
                # pf_shared.CollectionNotificationType.EMAIL_RECIEVED,
            ]
        )


class RecipientNotifications(pf_shared.PFBaseModel):
    notification_type: list[pf_shared.NotificationType] = _p.Field(default_factory=list)

    @classmethod
    def standard_recip(cls):
        return cls(
            notification_type=[
                pf_shared.NotificationType.EMAIL,
                pf_shared.NotificationType.SMS_DOD,
                pf_shared.NotificationType.DELIVERY,
            ]
        )


class NominatedDeliveryDatelist(pf_shared.PFBaseModel):
    nominated_delivery_date: list[str] = _p.Field(default_factory=list)


class SafePlacelist(pf_shared.PFBaseModel):
    safe_place: list[str] = _p.Field(default_factory=list)


class ServiceCodes(pf_shared.PFBaseModel):
    service_code: list[str] = _p.Field(default_factory=list)


class SpecifiedNeighbour(pf_shared.PFBaseModel):
    address: list[pf_models.AddressTemporary] = _p.Field(default_factory=list)

    @_p.field_validator('address', mode='after')
    def check_add_type(cls, v, values):
        outaddrs = []
        for add in v:
            try:
                addr = pf_models.AddressRecipient.model_validate(add.model_dump(by_alias=True))
            except _p.ValidationError:
                addr = pf_models.AddressCollection.model_validate(add.model_dump(by_alias=True))
            outaddrs.append(addr)
        return outaddrs


#
# class SpecifiedNeighbour(pf_shared.PFBaseModel):
#     address: list[pf_models.AddressRecipient] = _p.Field(default_factory=list)
#
#     @_p.field_validator('address', mode='after')
#     def check_add_type(cls, v, values):
#         outaddrs = []
#         for add in v:
#             try:
#                 addr = pf_models.AddressRecipient.model_validate(add.model_dump(by_alias=True))
#             except _p.ValidationError:
#                 addr = pf_models.AddressCollection.model_validate(add.model_dump(by_alias=True))
#             outaddrs.append(addr)
#         return outaddrs
