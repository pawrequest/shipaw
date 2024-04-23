from __future__ import annotations, annotations

import pathlib
import typing as _t

import pydantic as _p
import pydantic as pyd
import sqlmodel as sqm
from pawdantic.pawui import states as ui_states, pawui_types
from pydantic import ConfigDict, Field

from shipaw.models import pf_ext, pf_shared, pf_top
from shipaw.ship_types import ShipDirection
from .. import msgs, pf_config, ship_types

BookingReqSQM = _t.Annotated[
    msgs.CreateShipmentRequest, sqm.Field(sa_column=sqm.Column(ship_types.PawdanticJSON(msgs.CreateShipmentRequest)))
]
BookingRespSQM = _t.Annotated[
    msgs.CreateShipmentResponse,
    sqm.Field(sa_column=sqm.Column(ship_types.PawdanticJSON(msgs.CreateShipmentResponse))),
]


class BookingState(ui_states.BaseUIState):
    request: BookingReqSQM
    response: BookingRespSQM
    label_downloaded: bool = False
    label_dl_path: pathlib.Path | None = None

    @_p.model_validator(mode='after')
    def get_alerts(self):
        if self.response.alerts:
            self.alert_dict = pawui_types.AlertDict({a.message: a.type for a in self.response.alerts.alert})
        return self

    @property
    def response_alert_dict(self):
        return {a.message: a.type for a in self.response.alerts.alert} if self.response.alerts else {}

    def shipment_num(self):
        return (
            self.response.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
            if self.booked
            else None
        )

    # def state_alerts(self) -> list:
    #     return self.response.alerts.alert if self.response.alerts else []
    #
    # def alert_dict(self) -> dict[str, shipaw.types.AlertType]:
    #     return {a.message: a.type for a in self.state_alerts()}

    @property
    def booked(self):
        return self.response.completed_shipment_info is not None


class ShipStatePartial(ui_states.BaseUIState):
    booking_state: BookingState | None = None

    boxes: pyd.PositiveInt | None = None
    service: pf_shared.ServiceCode | None = None
    ship_date: ship_types.SHIPPING_DATE | None = None
    contact: pf_top.Contact | None = None
    address: pf_ext.AddressRecipient | None = None
    candidates: list[pf_ext.AddressRecipient] | None = None
    direction: ShipDirection | None = None
    reference: str | None = None
    special_instructions: str | None = None

    @property
    def pf_label_name(self):
        return f'Parcelforce Collection Label for {self.contact.business_name} on {self.ship_date}'

    @property
    def named_label_path(self):
        sett = pf_config.PF_SETTINGS
        return (sett.label_dir / self.pf_label_name).with_suffix('.pdf')


class ShipState(ShipStatePartial):
    contact: pf_top.Contact
    address: pf_ext.AddressRecipient
    ship_date: ship_types.SHIPPING_DATE
    boxes: pyd.PositiveInt = 1
    service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: ship_types.ShipDirection = 'out'
    candidates: list[pf_ext.AddressRecipient] | None = Field(None)
    reference: str | None = None
    special_instructions: str | None = None


class ShipStateExtra(ShipState):
    model_config = ConfigDict(extra='ignore')


def response_alert_dict(response):
    return {a.message: a.type for a in response.alerts.alert} if response.alerts else {}


def state_alert_dict(state: BookingState):
    return response_alert_dict(state.response)


class ShipStateBooked(ShipState):
    booking_state: BookingState
