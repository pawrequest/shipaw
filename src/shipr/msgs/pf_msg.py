# from __future__ import annotations

# if _ty.TYPE_CHECKING:
#     pass

import pydantic as pyd
from loguru import logger

from ..models import pf_ext, pf_lists, pf_shared, pf_top, types as shipr_types, types


class BaseRequest(pf_shared.BasePFType):
    authentication: pf_shared.Authentication

    def req_dict(self):
        return self.model_dump(by_alias=True)

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: pf_shared.Authentication):
        self.authentication = auth

    def auth_request_dict(self) -> dict:
        if not self.authorised:
            raise ValueError('Authentication is required')
        all_obs = [self.authentication, *self.objs]
        return self.alias_dict(all_obs)


class BaseResponse(pf_shared.BasePFType):
    alerts: pf_lists.Alerts | None = pyd.Field(default_factory=list)

    @pyd.field_validator('alerts')
    def check_alerts(cls, v, info):
        if v:
            for alt in v.alert:
                if alt.type == 'WARNING':
                    logger.warning(f'ExpressLink Warning: {alt.message} in {cls.__name__}')
                elif alt.type == 'ERROR':
                    logger.error(f'ExpressLink Error: {alt.message} in {cls.__name__}')
                    # raise types.ExpressLinkError(f'ExpressLink Error: {alt.message} for {cls.__name__}')
                else:
                    logger.info(f'ExpressLink {alt.type}: {alt.message} in {cls.__name__}')
        return v


class FindMessage(pf_shared.BasePFType):
    convenient_collect: pf_ext.ConvenientCollect | None = None
    specified_post_office: pf_ext.SpecifiedPostOffice | None = None
    paf: pf_top.PAF | None = pyd.Field(None, alias='PAF')
    safe_places: bool | None = None
    nominated_delivery_dates: pf_top.NominatedDeliveryDates | None = None
    postcode_exclusion: pf_top.PostcodeExclusion | None = None


class FindRequest(FindMessage, BaseRequest):
    ...


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: pf_lists.SafePlacelist | None = pyd.Field(default_factory=list)


# class FindMessenger(BaseMessenger):


#     name = 'Find'
#     request_type = type[FindRequest]
#     response_type = type[FindResponse]
#

################################################################


class CreateShipmentRequest(BaseRequest):
    requested_shipment: pf_top.RequestedShipmentMinimum


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: pf_top.CompletedShipmentInfo | None = None


################################################################


class PrintLabelRequest(BaseRequest):
    shipment_number: str
    print_format: str | None = None
    barcode_format: str | None = None
    print_type: shipr_types.PrintType = 'ALL_PARCELS'


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
    completed_shipment_info: pf_ext.CompletedReturnInfo | None = None


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str


class CCReserveResponse(BaseResponse):
    post_office: pf_ext.PostOffice | None = None


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
