from __future__ import annotations

from base64 import b64decode, b64encode
from enum import StrEnum
from pathlib import Path

from loguru import logger
from pawdf.array_pdf.array_p import on_a4
from pydantic import ConfigDict, Field, computed_field, field_validator, model_validator

from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.label_file import get_label_folder, get_label_stem, unused_path
from shipaw.agnostic.shipment import Shipment


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Alert(ShipawBaseModel):
    code: int | None = None
    message: str
    type: AlertType = AlertType.NOTIFICATION

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return NotImplemented
        return (self.code, self.message, self.type) == (other.code, other.message, other.type)

    def __hash__(self):
        return hash((self.code, self.message, self.type))

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type=AlertType.ERROR)


class Alerts(ShipawBaseModel):
    alert: list[Alert] = Field(default_factory=list[Alert])

    def __bool__(self):
        return bool(self.alert)

    def __add__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        combined = set(self.alert) | set(other.alert)
        return Alerts(alert=list(combined))

    def __iadd__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        self.alert = list(set(self.alert) | set(other.alert))
        return self

    def __sub__(self, other: Alerts | Alert):
        if not isinstance(other, Alerts) and not isinstance(other, Alert):
            raise TypeError(f'Expected Alerts or Alert instance, got {type(other)}')
        if isinstance(other, Alert):
            other = Alerts(alert=[other])
        diff = set(self.alert) - set(other.alert)
        return Alerts(alert=list(diff))

    def __contains__(self, alert: Alert):
        return alert in set(self.alert)

    @classmethod
    def empty(cls):
        return cls(alert=[])


class BaseResponseAgnost(ShipawBaseModel):
    alerts: Alerts = Field(default_factory=Alerts.empty)
    data: dict | None = None
    raw: str | None = None
    success: bool | None = None
    status: str | None = None


class ShipmentBookingResponseAgnost(BaseResponseAgnost):
    shipment: Shipment
    shipment_num: str | None = None
    tracking_link: str | None = None
    label_data: bytes | None = None
    label_path: Path | None = None

    model_config = ConfigDict(json_encoders={bytes: lambda v: b64encode(v).decode('utf-8') if v else None})

    @field_validator('label_data', mode='before')
    def decode_label_data(cls, value):
        if isinstance(value, str):
            return b64decode(value)
        return value

    @model_validator(mode='after')
    def get_label_path(self):
        if self.label_path is None and self.label_data:
            folder = get_label_folder(self.shipment.direction)
            label_stem = get_label_stem(self.shipment)
            label_filepath = (folder / label_stem).with_suffix('.pdf')
            self.label_path = unused_path(label_filepath)
        return self

    async def write_label_file(self):
        try:
            label_content = self.label_data
        except Exception as e:
            logger.error(f'Error getting label content: {e}')
            raise
        label_path = self.label_path
        unsize = label_path.parent / 'original_size' / label_path.name
        unsize.parent.mkdir(parents=True, exist_ok=True)
        unsize.write_bytes(label_content)
        on_a4(input_file=unsize, output_file=label_path)
        logger.info(f'Wrote label to {label_path}')