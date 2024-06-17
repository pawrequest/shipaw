from __future__ import annotations

from pawdantic.pawsql import default_json_field, required_json_field
import pydantic as pyd
from loguru import logger

from shipaw.pf_config import pf_sett
from .pf_shared import PFBaseModel
from .. import ship_types
from ..models import pf_lists, pf_models, pf_shared, pf_top
from ..models.pf_shipment import ShipmentRequest


class Alert(PFBaseModel):
    code: int | None = None
    message: str
    type: ship_types.AlertType = ship_types.AlertType.NOTIFICATION

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type='ERROR')


class Alerts(PFBaseModel):
    alert: list[Alert] = default_json_field(Alert, list)

    @classmethod
    def empty(cls):
        return cls(alert=[])

    # alert: list[Alert] | None = optional_json_field(Alert)


# AlertList = optional_json_field(Alert)


class BaseRequest(pf_shared.PFBaseModel):
    authentication: pf_shared.Authentication

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: pf_shared.Authentication):
        self.authentication = auth


class BaseResponse(pf_shared.PFBaseModel):
    # alerts: list[Alert] | None = pyd.Field(default_factory=list, sa_column=sqm.Column(sqm.JSON))
    # alerts: Alerts | None = sqm.Field(
    #     None,
    #     sa_column=sqm.Column(PydanticJSONColumn(Alerts))
    # )
    alerts: Alerts | None = default_json_field(Alerts, Alerts.empty)
    # alerts: Alerts | None = optional_json_field(Alerts)
    # alerts: Alerts | None = pyd.Field(None, sa_column=sqlmodel.Column(PydanticJSONColumn(Alerts)))

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
        return (
            self.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
            if self.completed_shipment_info
            else None
        )

    @property
    def status(self):
        return self.completed_shipment_info.status

    def tracking_link(self):
        tlink = pf_sett().tracking_url_stem + self.shipment_num
        logger.info(f'Getting tracking link: {str(tlink)}')
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
