from __future__ import annotations

from base64 import b64encode
from pathlib import Path

from pydantic import ConfigDict, Field, computed_field

from shipaw.config import SHIPAW_SETTINGS
from shipaw.fapi.alerts import Alerts
from shipaw.models.base import ShipawBaseModel
from shipaw.utils.label_file import get_label_stem, unused_path
from shipaw.models.shipment import Shipment


class ShipawTemplate(ShipawBaseModel):
    template_path: str
    context: dict = Field(default_factory=dict)

    def render_template(self, request):
        if not self.template_path:
            raise ValueError('No template_path set')
        return request.app.shipaw_settings.templates.TemplateResponse(
            request=request, name=self.template_path, context=self.context
        )


class BaseResponse(ShipawBaseModel):
    alerts: Alerts = Alerts.empty()
    data: dict | None = None
    success: bool | None = None
    status: str | None = None
    template: ShipawTemplate | None = None


class ShipmentResponse(BaseResponse):
    shipment: Shipment
    label_data: bytes | None = None
    _label_path: Path | None = None
    shipment_num: str | None = None
    shipment_numbers: list[str] = Field(default_factory=list)
    tracking_links: list[str] = Field(default_factory=list)
    collection_id: str | None = None

    model_config = ConfigDict(json_encoders={bytes: lambda v: b64encode(v).decode('utf-8') if v else None})

    @computed_field
    @property
    def label_path(self) -> Path:
        if self._label_path is None:
            folder = SHIPAW_SETTINGS.label_dir / self.shipment.direction
            label_stem = get_label_stem(self.shipment)
            label_filepath = (folder / label_stem).with_suffix('.pdf')
            self._label_path = unused_path(label_filepath)
        return self._label_path


class CompletedShipmentResponse(ShipmentResponse):
    # model_config = ConfigDict(frozen=True)
    shipment: Shipment
    label_data: bytes
    shipment_num: str
    shipment_numbers: list[str]
    tracking_links: list[str]
    collection_id: str | None = None


class ShipawTemplateResponse(BaseResponse):
    template: ShipawTemplate
