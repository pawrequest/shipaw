from __future__ import annotations

from abc import ABC
from typing import Optional, TYPE_CHECKING

from loguru import logger
from pydantic import Field, field_validator

from shipr.express import types as elp
from shipr.express.shipment import RequestedShipmentMinimum, CompletedShipmentInfo
from shipr.express.shared import BasePFType


class BaseRequest(elp.BasePFType):
    authentication: Optional[elp.Authentication] = Field(None)

    def req_dict(self):
        return self.model_dump(by_alias=True, exclude_none=True)

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: elp.Authentication):
        self.authentication = auth

    def auth_request_dict(self) -> dict:
        if not self.authorised:
            raise ValueError('Authentication is required')
        all_obs = [self.authentication, *self.objs]
        return self.alias_dict(all_obs)


class BaseResponse(BasePFType, ABC):
    alerts: Optional[elp.Alerts] = Field(None)

    @field_validator('alerts')
    def check_alerts(cls, v):
        if v:
            for alt in v.alert:
                if alt.type == 'WARNING':
                    logger.warning(f'ExpressLink Warning: {alt.message}')
                elif alt.type == 'ERROR':
                    logger.error(f'ExpressLink Error: {alt.message}')
                else:
                    logger.info(f'ExpressLink {alt.type}: {alt.message}')
        return v


class FindMessage(BasePFType):
    convenient_collect: Optional[elp.ConvenientCollect] = Field(
        None
    )
    specified_post_office: Optional[elp.SpecifiedPostOffice] = Field(
        None
    )
    paf: Optional[elp.PAF] = Field(None, alias='PAF')
    safe_places: Optional[bool] = Field(None)
    nominated_delivery_dates: Optional[elp.NominatedDeliveryDates] = Field(
        None
    )
    postcode_exclusion: Optional[elp.PostcodeExclusion] = Field(
        None
    )


class FindRequest(FindMessage, BaseRequest):
    ...


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: Optional[elp.SafePlaceList] = Field(None)
    ...


################################################################

class CreateShipmentRequest(BaseRequest):
    requested_shipment: RequestedShipmentMinimum = Field(...)


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[CompletedShipmentInfo] = Field(
        None
    )


################################################################


class PrintDocumentRequest(BaseRequest):
    shipment_number: str = Field(...)
    document_type: int = Field(...)
    print_format: Optional[str] = Field(None)


class PrintDocumentResponse(BaseResponse):
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    document_type: Optional[elp.Document] = Field(None)


################################################################
class CreateManifestRequest(BaseRequest):
    department_id: Optional[int] = Field(None)


class CreateManifestResponse(BaseResponse):
    completed_manifests: Optional[elp.CompletedManifests] = Field(
        None
    )


################################################################
class PrintManifestRequest(BaseRequest):
    manifest_number: str = Field(...)
    print_format: Optional[str] = Field(None)


class PrintManifestResponse(BaseResponse):
    manifest: Optional[elp.Document] = Field(None)


################################################################


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)
    collection_time: elp.DateTimeRange = Field(...)


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[elp.CompletedReturnInfo] = Field(
        None
    )


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str = Field(...)


class CCReserveResponse(BaseResponse):
    post_office: Optional[elp.PostOffice] = Field(None)


################################################################

class CancelShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)


class CancelShipmentResponse(BaseResponse):
    completed_cancel: Optional[elp.CompletedCancel] = Field(None)


################################################################


class CreatePrintRequest(BaseRequest):
    requested_shipment: RequestedShipmentMinimum = Field(...)


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: Optional[elp.CompletedShipmentInfoCreatePrint] = (
        Field(None)
    )
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)


################################################################

class PrintLabelRequest(BaseRequest):
    shipment_number: str = Field(...)
    print_format: Optional[str] = Field(None)
    barcode_format: Optional[str] = Field(None)
    print_type: Optional[elp.PrintType] = Field(None)


class PrintLabelResponse(BaseResponse):
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)

################################################################
