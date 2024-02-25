from __future__ import annotations

from typing import Optional

from pydantic import Field

from shipr.express import types as elp
from shipr.express.shipment import CompletedShipmentInfo, RequestedShipmentMinimum
from shipr.express.shared import BasePFType, BaseRequest, BaseResponse


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


# class FindMessenger(BaseMessenger):
#     name = 'Find'
#     request_type = type[FindRequest]
#     response_type = type[FindResponse]
#

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
