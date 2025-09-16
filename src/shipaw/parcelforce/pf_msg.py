from __future__ import annotations

import pydantic as pyd
from loguru import logger
from pydantic import Field, field_validator

from shipaw.pf_config import pf_sett
from shipaw.parcelforce.pf_shared import PFBaseModel
from shipaw.parcelforce.pf_shipment import Shipment
from shipaw import ship_types
from shipaw.parcelforce import pf_lists, pf_models, pf_shared, pf_top
from shipaw.ship_types import AlertType, ExpressLinkError, ExpressLinkNotification, ExpressLinkWarning


class Alert(PFBaseModel):
    code: int | None = None
    message: str
    type: ship_types.AlertType = ship_types.AlertType.NOTIFICATION

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return NotImplemented
        return (self.code, self.message, self.type) == (other.code, other.message, other.type)

    def __hash__(self):
        return hash((self.code, self.message, self.type))

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type=AlertType.ERROR)


class Alerts(PFBaseModel):
    alert: list[Alert]

    def __bool__(self):
        return bool(self.alert)

    def __add__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        combined = set(self.alert) | set(other.alert)
        return Alerts(alert=list(combined))

    def __iadd__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        self.alert = list(set(self.alert) | set(other.alert))
        return self

    def __sub__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        diff = set(self.alert) - set(other.alert)
        return Alerts(alert=list(diff))

    def __contains__(self, alert: Alert):
        return alert in set(self.alert)

    @classmethod
    def empty(cls):
        return cls(alert=[])


class BaseRequest(pf_shared.PFBaseModel):
    authentication: pf_shared.Authentication | None = None

    def authenticated(self, auth):
        self.authentication = auth
        return self


class BaseResponse(pf_shared.PFBaseModel):
    alerts: Alerts | None = Field(default_factory=Alerts.empty)

    @field_validator('alerts', mode='after')
    def empty_alerts(cls, v):
        if v is None:
            return Alerts.empty()
        if isinstance(v, Alerts):
            return v
        raise TypeError(f'Expected Alerts instance, got {type(v)}')


class FindMessage(pf_shared.PFBaseModel):
    convenient_collect: pf_models.ConvenientCollect | None = None
    specified_post_office: pf_models.SpecifiedPostOffice | None = None
    paf: pf_top.PAF | None = pyd.Field(None, alias='PAF')
    safe_places: bool | None = None
    nominated_delivery_dates: pf_top.NominatedDeliveryDates | None = None
    postcode_exclusion: pf_top.PostcodeExclusion | None = None


class FindRequest(FindMessage, BaseRequest): ...


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: pf_lists.SafePlacelist | None = pyd.Field(default_factory=list)


# class FindMessenger(BaseMessenger):


#     name = 'Find'
#     request_type = type[FindRequest]
#     response_type = type[FindResponse]
#

################################################################


#
# class ShipmentRequest(BaseRequest):
#     shipment: pf_top.RequestedShipmentMinimum


#
# class CreateCollectionRequest(ShipmentRequest):
#     shipment: pf_top.CollectionMinimum


class ShipmentRequest(BaseRequest):
    requested_shipment: Shipment


class ShipmentResponse(BaseResponse):
    completed_shipment_info: pf_top.CompletedShipmentInfo | None = None

    @property
    def shipment_num(self):
        return (
            self.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
            if self.completed_shipment_info
            else None
        )

    @property
    def status(self):
        if self.completed_shipment_info:
            return self.completed_shipment_info.status
        return 'No Completed Shipment Info'

    @property
    def success(self):
        if self.completed_shipment_info:
            return self.completed_shipment_info.status.lower() == 'allocated'
        return False

    def tracking_link(self):
        tlink = pf_sett().tracking_url_stem + self.shipment_num
        # logger.info(f'Getting tracking link: {str(tlink)}')
        return tlink

    def tracking_link_rm(self):
        stem = pf_sett().tracking_url_stem_rm
        tlink = f'{stem}PB{self.shipment_num}001'
        return tlink

    def handle_errors(self):
        if hasattr(self, 'Error'): # Combadge adds this? or PF? not in WSDL but appears sometimes
            msg = self.Error.message if hasattr(self.Error, 'message') else str(self.Error)
            raise ExpressLinkError(msg)
        if hasattr(self, 'alerts') and hasattr(self.alerts, 'alert'):
            for _ in self.alerts.alert:
                match _.type:
                    case AlertType.ERROR:
                        logger.error('ExpressLinkl Error, booking failed?: ' + _.message)
                        raise ExpressLinkError(_.message)
                    case _:
                        logger.warning('Expresslink Warning: ' + _.message)


def log_booked_shipment(request: ShipmentRequest, response: ShipmentResponse):
    if hasattr(response, 'shipment_num') and response.shipment_num:
        logger.info(
            f'BOOKED {request.requested_shipment.direction.name.title()} shipment# {response.shipment_num} for {request.requested_shipment.remote_address.lines_str}'
        )


################################################################


class PrintLabelRequest(BaseRequest):
    shipment_number: str
    print_format: str | None = None
    barcode_format: str | None = None
    print_type: ship_types.PrintType = 'ALL_PARCELS'


class PrintLabelResponse(BaseResponse):
    label: pf_shared.Document | None = None
    label_data: pf_top.ShipmentLabelData | None = None
    partner_code: str | None


################################################################


class PrintDocumentRequest(BaseRequest):
    shipment_number: str | None = None
    document_type: int | None = None
    print_format: str | None = None


class PrintDocumentResponse(BaseResponse):
    label: pf_shared.Document | None = None
    label_data: pf_top.ShipmentLabelData | None = None
    document_type: pf_shared.Document | None = None


################################################################


class CreateManifestRequest(BaseRequest):
    department_id: int | None = None


class CreateManifestResponse(BaseResponse):
    completed_manifests: pf_top.CompletedManifests | None = None


################################################################


class PrintManifestRequest(BaseRequest):
    manifest_number: str
    print_format: str | None = None


class PrintManifestResponse(BaseResponse):
    manifest: pf_shared.Document | None = None


################################################################


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str
    collection_time: pf_shared.DateTimeRange | None = None


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: pf_models.CompletedReturnInfo | None = None


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str


class CCReserveResponse(BaseResponse):
    post_office: pf_models.PostOffice | None = None


################################################################


class CancelShipmentRequest(BaseRequest):
    shipment_number: str


class CancelShipmentResponse(BaseResponse):
    completed_cancel: pf_lists.CompletedCancel | None = pyd.Field(default_factory=list)


################################################################


class CreatePrintRequest(BaseRequest):
    requested_shipment: pf_top.RequestedShipmentMinimum


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: pf_top.CompletedShipmentInfoCreatePrint | None = None
    label: pf_shared.Document | None = None
    label_data: pf_top.ShipmentLabelData | None = None
    partner_code: str | None

################################################################
