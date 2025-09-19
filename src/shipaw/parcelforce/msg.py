from __future__ import annotations

import pydantic as pyd
from loguru import logger
from pydantic import Field
from pygments.lexer import default

from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.responses import AlertType, Alerts

from shipaw.parcelforce.lists import CompletedCancel, SafePlacelist
from shipaw.parcelforce.models import CompletedReturnInfo, ConvenientCollect, PostOffice, SpecifiedPostOffice
from shipaw.parcelforce.pf_config import pf_sett
from shipaw.parcelforce.shared import DateTimeRange, Document, PFBaseModel
from shipaw.agnostic.requests import Authentication
from shipaw.parcelforce.shipment import Shipment
from shipaw.agnostic import ship_types
from shipaw.agnostic.ship_types import ExpressLinkError
from shipaw.parcelforce.top import (
    CompletedManifests,
    CompletedShipmentInfo,
    CompletedShipmentInfoCreatePrint,
    NominatedDeliveryDates,
    PAF,
    PostcodeExclusion,
    RequestedShipmentMinimum,
    ShipmentLabelData,
)


class BaseRequest(PFBaseModel):
    authentication: Authentication | None = None

    def authenticated(self, auth):
        self.authentication = auth
        return self


class FindMessage(PFBaseModel):
    convenient_collect: ConvenientCollect | None = None
    specified_post_office: SpecifiedPostOffice | None = None
    paf: PAF | None = pyd.Field(None, alias='PAF')
    safe_places: bool | None = None
    nominated_delivery_dates: NominatedDeliveryDates | None = None
    postcode_exclusion: PostcodeExclusion | None = None


class FindRequest(FindMessage, BaseRequest): ...


class BaseResponse(ShipawBaseModel):
    alerts: Alerts | None = Field(default_factory=Alerts.empty)


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: SafePlacelist | None = pyd.Field(default_factory=list)


# class FindMessenger(BaseMessenger):


#     name = 'Find'
#     request_type = type[FindRequest]
#     response_type = type[FindResponse]
#

################################################################


#
# class ShipmentRequest(BaseRequest):
#     shipment: RequestedShipmentMinimum


#
# class CreateCollectionRequest(ShipmentRequest):
#     shipment: CollectionMinimum


class ShipmentRequest(BaseRequest):
    requested_shipment: Shipment


class ShipmentResponse(BaseResponse):
    completed_shipment_info: CompletedShipmentInfo | None = None

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
        if hasattr(self, 'Error'):  # Combadge adds this? or PF? not in WSDL but appears sometimes
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
    else:
        logger.warning('Something Wrong with booking, no shipment number returned?')


################################################################


class PrintLabelRequest(BaseRequest):
    shipment_number: str
    print_format: str | None = None
    barcode_format: str | None = None
    print_type: ship_types.PrintType = 'ALL_PARCELS'


class PrintLabelResponse(BaseResponse):
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    partner_code: str | None


################################################################


class PrintDocumentRequest(BaseRequest):
    shipment_number: str | None = None
    document_type: int | None = None
    print_format: str | None = None


class PrintDocumentResponse(BaseResponse):
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    document_type: Document | None = None


################################################################


class CreateManifestRequest(BaseRequest):
    department_id: int | None = None


class CreateManifestResponse(BaseResponse):
    completed_manifests: CompletedManifests | None = None


################################################################


class PrintManifestRequest(BaseRequest):
    manifest_number: str
    print_format: str | None = None


class PrintManifestResponse(BaseResponse):
    manifest: Document | None = None


################################################################


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str
    collection_time: DateTimeRange | None = None


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: CompletedReturnInfo | None = None


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str


class CCReserveResponse(BaseResponse):
    post_office: PostOffice | None = None


################################################################


class CancelShipmentRequest(BaseRequest):
    shipment_number: str


class CancelShipmentResponse(BaseResponse):
    completed_cancel: CompletedCancel | None = pyd.Field(default_factory=list)


################################################################


class CreatePrintRequest(BaseRequest):
    requested_shipment: RequestedShipmentMinimum


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: CompletedShipmentInfoCreatePrint | None = None
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    partner_code: str | None

################################################################
