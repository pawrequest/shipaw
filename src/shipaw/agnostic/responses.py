from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from shipaw.agnostic.base import ShipawBaseModel


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
    success: bool = False
    status: str | None = None


#
class ShipmentBookingResponseAgnost(BaseResponseAgnost):
    shipment_num: str | None = None

