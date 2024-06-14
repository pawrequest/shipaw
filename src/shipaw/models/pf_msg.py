# from __future__ import annotations
import json
from typing import Annotated

import sqlmodel
from pawdantic.pawsql import JSONColumn
from sqlalchemy.types import TEXT, TypeDecorator
import pydantic as pyd
from loguru import logger

from shipaw.pf_config import pf_sett
from .pf_lists import Alerts
from .. import ship_types
from ..models import pf_lists, pf_models, pf_shared, pf_top
from ..models.pf_shipment import ShipmentRequest


class BaseRequest(pf_shared.PFBaseModel):
    authentication: pf_shared.Authentication

    # def req_dict(self):
    #     return self.model_dump(by_alias=True)

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: pf_shared.Authentication):
        self.authentication = auth

    # def auth_request_dict(self) -> dict:
    #     if not self.authorised:
    #         raise ValueError('Authentication is required')
    #     all_obs = [self.authentication, *self.objs]
    #     return self.alias_dict(all_obs)


class JSONEncodedList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)


# AlertList = typing.Annotated[
#     list[pf_shared.Alert], pyd.Field(default_factory=list, sa_column=sqm.Column(JSONEncodedList))]

AlertList = Annotated[Alerts, pyd.Field(None, sa_column=sqlmodel.Column(JSONColumn(Alerts)))]


class BaseResponse(pf_shared.PFBaseModel):
    # alerts: list[Alert] | None = pyd.Field(default_factory=list, sa_column=sqm.Column(sqm.JSON))
    # alerts: Alerts | None = sqm.Field(
    #     None,
    #     sa_column=sqm.Column(JSONColumn(Alerts))
    # )
    # alerts: AlertList
    alerts: Alerts | None = pyd.Field(None, sa_column=sqlmodel.Column(JSONColumn(Alerts)))

    # @pyd.field_validator('alerts', mode='before')
    # def check_alerts(cls, v, values) -> list[Alert]:
    #     if not v:
    #         return set()
    #     if isinstance(v, dict):
    #         if 'Alert' in v:
    #             return [Alert(**alert) for alert in v['Alert']]
    #     elif isinstance(v, list):
    #         return [Alert(**alert) for alert in v]
    #     return v
    # @pyd.model_validator(mode='after')
    # def check_alerts(self):
    #     if isinstance(self.alerts, dict):
    #         if alt_ds := self.alerts.get('Alert'):
    #             alts = {Alert(**alt) for alt in alt_ds}
    #             self.alerts = self.alerts | alts
    #             for alt in alts:
    #                 if alt.type == 'WARNING':
    #                     logger.warning(f'ExpressLink Warning: {alt.message} in {self.__class__.__name__}')
    #                 elif alt.type == 'ERROR':
    #                     logger.error(
    #                         f'ExpressLink Error: {alt.message} in {self.__class__.__name__} - {"; ".join(f"{k}: {v}" for k, v in info.data)}'
    #                     )
    #                 else:
    #                     logger.info(f'ExpressLink {alt.type}: {alt.message} in {self.__class__.__name__}')
    #     return v


class FindMessage(pf_shared.PFBaseModel):
    convenient_collect: pf_models.ConvenientCollect | None = None
    specified_post_office: pf_models.SpecifiedPostOffice | None = None
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


#
# class CreateRequest(BaseRequest):
#     requested_shipment: pf_top.RequestedShipmentMinimum


#
# class CreateCollectionRequest(CreateRequest):
#     requested_shipment: pf_top.CollectionMinimum


class CreateRequest(BaseRequest):
    requested_shipment: ShipmentRequest


class CreateShipmentResponse(BaseResponse):
    completed_shipment_info: pf_top.CompletedShipmentInfo | None = None

    @property
    def shipment_num(self):
        return self.completed_shipment_info.completed_shipments.completed_shipment[
            0].shipment_number

    @property
    def status(self):
        return self.completed_shipment_info.status

    def tracking_link(self):
        tlink = pf_sett().tracking_url_stem + self.shipment_num
        logger.info(f'Creating tracking link: {tlink}')
        return tlink


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
