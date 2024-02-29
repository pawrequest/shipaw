from __future__ import annotations

from typing import Optional

from loguru import logger
from pydantic import Field, field_validator

from . import extended, lists, shipr_shared as shared, simple_models as sm


class BaseRequest(shared.BasePFType):
    authentication: Optional[shared.Authentication] = Field(None)

    def req_dict(self):
        return self.model_dump(by_alias=True)

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: shared.Authentication):
        self.authentication = auth

    def auth_request_dict(self) -> dict:
        if not self.authorised:
            raise ValueError("Authentication is required")
        all_obs = [self.authentication, *self.objs]
        return self.alias_dict(all_obs)


class BaseResponse(shared.BasePFType):
    alerts: Optional[lists.Alerts] = Field(None)

    @field_validator("alerts")
    def check_alerts(cls, v):
        if v:
            for alt in v.alert:
                if alt.type == "WARNING":
                    logger.warning(f"ExpressLink Warning: {alt.message}")
                elif alt.type == "ERROR":
                    logger.error(f"ExpressLink Error: {alt.message}")
                else:
                    logger.info(f"ExpressLink {alt.type}: {alt.message}")
        return v


class FindMessage(shared.BasePFType):
    convenient_collect: Optional[extended.ConvenientCollect] = Field(None)
    specified_post_office: Optional[extended.SpecifiedPostOffice] = Field(None)
    paf: Optional[extended.PAF] = Field(None, alias="PAF")
    safe_places: Optional[bool] = Field(None)
    nominated_delivery_dates: Optional[extended.NominatedDeliveryDates] = Field(None)
    postcode_exclusion: Optional[extended.PostcodeExclusion] = Field(None)


class FindRequest(FindMessage, BaseRequest):
    ...


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: Optional[lists.SafePlacelist] = Field(None)
    ...


# class FindMessenger(BaseMessenger):
#     name = 'Find'
#     request_type = type[FindRequest]
#     response_type = type[FindResponse]
#

################################################################


class CreateShipmentRequest(BaseRequest):
    requested_shipment: extended.RequestedShipmentMinimum = Field(...)


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[extended.CompletedShipmentInfo] = Field(None)


################################################################


class PrintLabelRequest(BaseRequest):
    shipment_number: str = Field(...)
    print_format: Optional[str] = Field(None)
    barcode_format: Optional[str] = Field(None)
    print_type: Optional[shared.PrintType] = Field("ALL_PARCELS")


class PrintLabelResponse(BaseResponse):
    label: Optional[sm.Document] = Field(None)
    label_data: Optional[lists.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)


################################################################


class PrintDocumentRequest(BaseRequest):
    shipment_number: str = Field(...)
    document_type: int = Field(...)
    print_format: Optional[str] = Field(None)


class PrintDocumentResponse(BaseResponse):
    label: Optional[sm.Document] = Field(None)
    label_data: Optional[lists.ShipmentLabelData] = Field(None)
    document_type: Optional[sm.Document] = Field(None)


################################################################
class CreateManifestRequest(BaseRequest):
    department_id: Optional[int] = Field(None)


class CreateManifestResponse(BaseResponse):
    completed_manifests: Optional[lists.CompletedManifests] = Field(None)


################################################################
class PrintManifestRequest(BaseRequest):
    manifest_number: str = Field(...)
    print_format: Optional[str] = Field(None)


class PrintManifestResponse(BaseResponse):
    manifest: Optional[sm.Document] = Field(None)


################################################################


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)
    collection_time: sm.DateTimeRange = Field(...)


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[extended.CompletedReturnInfo] = Field(None)


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str = Field(...)


class CCReserveResponse(BaseResponse):
    post_office: Optional[extended.PostOffice] = Field(None)


################################################################


class CancelShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)


class CancelShipmentResponse(BaseResponse):
    completed_cancel: Optional[lists.CompletedCancel] = Field(None)


################################################################


class CreatePrintRequest(BaseRequest):
    requested_shipment: extended.RequestedShipmentMinimum = Field(...)


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: Optional[
        extended.CompletedShipmentInfoCreatePrint] = Field(None)
    label: Optional[sm.Document] = Field(None)
    label_data: Optional[lists.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)

################################################################
