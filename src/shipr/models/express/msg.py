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


class BaseResponse(elp.BasePFType, ABC):
    alerts: Optional[elp.Alerts] = Field(None)


class FindResponse(FindMessage, BaseResponse):
    ...


class PrintDocumentRequest(BaseRequest):
    shipment_number: str = Field(...)
    document_type: int = Field(...)
    print_format: Optional[str] = Field(None)


class CreateManifestRequest(BaseRequest):
    department_id: Optional[int] = Field(None)


class PrintManifestRequest(BaseRequest):
    manifest_number: str = Field(...)
    print_format: Optional[str] = Field(None)


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)
    collection_time: elp.DateTimeRange = Field(...)


class CCReserveRequest(BaseRequest):
    booking_reference: str = Field(...)


class CancelShipmentRequest(BaseRequest):
    shipment_number: str = Field(...)


class CancelShipmentRequest1(elp.BasePFType):
    cancel_shipment_request: CancelShipmentRequest = Field(
        ...
    )


class CCReserveRequest1(elp.BasePFType):
    cc_reserve_request: CCReserveRequest = Field(...)


class CreateManifestRequest1(elp.BasePFType):
    create_manifest_request: CreateManifestRequest = Field(
        ...
    )


class PrintDocumentRequest1(elp.BasePFType):
    print_document_request: PrintDocumentRequest = Field(
        ...
    )


class PrintLabelRequest1(elp.BasePFType):
    print_label_request: PrintLabelRequest = Field(...)


class PrintManifestRequest1(elp.BasePFType):
    print_manifest_request: PrintManifestRequest = Field(
        ...
    )


class ReturnShipmentRequest1(elp.BasePFType):
    return_shipment_request: ReturnShipmentRequest = Field(
        ...
    )


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: Optional[elp.CompletedShipmentInfoCreatePrint] = (
        Field(None)
    )
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)


class PrintLabelResponse(BaseResponse):
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    partner_code: Optional[str] = Field(None)


class PrintDocumentResponse(BaseResponse):
    label: Optional[elp.Document] = Field(None)
    label_data: Optional[elp.ShipmentLabelData] = Field(None)
    document_type: Optional[elp.Document] = Field(None)


class CreateManifestResponse(BaseResponse):
    completed_manifests: Optional[elp.CompletedManifests] = Field(
        None
    )


class PrintManifestResponse(BaseResponse):
    manifest: Optional[elp.Document] = Field(None)


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[elp.CompletedReturnInfo] = Field(
        None
    )


class CCReserveResponse(BaseResponse):
    post_office: Optional[elp.PostOffice] = Field(None)


class CancelShipmentResponse(BaseResponse):
    completed_cancel: Optional[elp.CompletedCancel] = Field(None)


class CancelShipmentResponse1(elp.BasePFType):
    cancel_shipment_reply: CancelShipmentResponse = Field(...)


class CCReserveResponse1(elp.BasePFType):
    cc_reserve_reply: CCReserveResponse = Field(...)


class CreateManifestResponse1(elp.BasePFType):
    create_manifest_reply: CreateManifestResponse = Field(...)


class CreatePrintResponse1(elp.BasePFType):
    create_print_reply: CreatePrintResponse = Field(...)


class PrintDocumentResponse1(elp.BasePFType):
    print_document_reply: PrintDocumentResponse = Field(...)


class PrintLabelResponse1(elp.BasePFType):
    print_label_reply: PrintLabelResponse = Field(...)


class PrintManifestResponse1(elp.BasePFType):
    print_manifest_reply: PrintManifestResponse = Field(...)


class ReturnShipmentResponse1(elp.BasePFType):
    return_shipment_reply: ReturnShipmentResponse = Field(...)


class FindResponse1(elp.BasePFType):
    find_reply: FindResponse = Field(...)


class FindRequest1(elp.BasePFType):
    find_request: FindRequest = Field(...)


class CreateShipmentRequest(BaseRequest):
    requested_shipment: elp.RequestedShipment = Field(...)


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: Optional[elp.CompletedShipmentInfo] = Field(
        None
    )


class CreatePrintRequest(BaseRequest):
    requested_shipment: elp.RequestedShipment = Field(...)


class CreatePrintRequest1(elp.BasePFType):
    create_print_request: CreatePrintRequest = Field(...)


class CreateShipmentResponse1(elp.BasePFType):
    create_shipment_reply: CreateShipmentResponse = Field(...)


class CreateShipmentRequest1(elp.BasePFType):
    create_shipment_request: CreateShipmentRequest = Field(
        ...
    )


class PrintLabelRequest(BaseRequest):
    shipment_number: str = Field(...)
    print_format: Optional[str] = Field(None)
    barcode_format: Optional[str] = Field(None)
    print_type: Optional[elp.PrintType] = Field(None)
