from __future__ import annotations

from base64 import b64encode
from pathlib import Path

from pydantic import ConfigDict, Field, model_validator

from shipaw.fapi.alerts import Alerts
from shipaw.models.base import ShipawBaseModel
from shipaw.models.label_file import get_label_stem, unused_path
from shipaw.models.shipment import Shipment
from shipaw.config import SHIPAW_SETTINGS


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
    shipment_num: str | None = None
    tracking_link: str | None = None
    label_data: bytes | None = None
    label_path: Path | None = None
    tracking_links: list[str] = Field(default_factory=list)
    shipment_numbers: list[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def track_links_from_tracking_link(self):
        if self.tracking_link and not self.tracking_links:
            self.tracking_links = [self.tracking_link]
        if self.shipment_num and not self.shipment_numbers:
            self.shipment_numbers = [self.shipment_num]
        return self

    model_config = ConfigDict(json_encoders={bytes: lambda v: b64encode(v).decode('utf-8') if v else None})

    @model_validator(mode='after')
    def get_label_path(self):
        if self.label_path is None:
            folder = SHIPAW_SETTINGS.label_dir / self.shipment.direction
            label_stem = get_label_stem(self.shipment)
            label_filepath = (folder / label_stem).with_suffix('.pdf')
            self.label_path = unused_path(label_filepath)
        return self

    # async def write_label_file(self):
    #     await array_write_label_content(self.label_data, self.label_path)


class ShipawTemplateResponse(BaseResponse):
    template: ShipawTemplate
