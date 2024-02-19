from __future__ import annotations

from abc import ABC
from typing import Optional

from pydantic import Field

from . import expresslink_pydantic as elp


class BaseRequest(elp.BasePFType, ABC):
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


class BaseResponse(elp.BasePFType, ABC):
    alerts: Optional[elp.Alerts] = Field(None)


class FindMessage(elp.BasePFType):
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
    ...


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
    requested_shipment: elp.RequestedShipment = Field(...)


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

class CreateShipmentRequest(BaseRequest):
    requested_shipment: elp.RequestedShipment = Field(...)


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[elp.CompletedShipmentInfo] = Field(
        None
    )
################################################################
