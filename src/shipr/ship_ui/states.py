from __future__ import annotations

import datetime as dt
import pathlib
import typing as _t


import pydantic as pyd
import sqlmodel as sqm

import shipr.types
from pawdantic.pawui import states as ui_states
from shipr.models import pf_ext, pf_shared, pf_top
from .. import msgs, types
from shipr.types import ShipDirection

BookingReqSQM = _t.Annotated[
    msgs.CreateShipmentRequest, sqm.Field(
        sa_column=sqm.Column(
            shipr.types.GenericJSONType(msgs.CreateShipmentRequest)
        )
    )
]
BookingRespSQM = _t.Annotated[
    msgs.CreateShipmentResponse, sqm.Field(
        sa_column=sqm.Column(
            shipr.types.GenericJSONType(msgs.CreateShipmentResponse)
        )
    )
]


class BookingState(ui_states.BaseUIState):
    request: BookingReqSQM
    response: BookingRespSQM
    label_path: pathlib.Path | None = None
    printed: bool = False

    def shipment_num(self):
        return (
            self.response.completed_shipment_info.completed_shipments.completed_shipment[
                0].shipment_number
            if self.booked
            else None
        )

    # def state_alerts(self) -> list:
    #     return self.response.alerts.alert if self.response.alerts else []
    # 
    # def alert_dict(self) -> dict[str, shipr.types.AlertType]:
    #     return {a.message: a.type for a in self.state_alerts()}

    @property
    def booked(self):
        return self.response.completed_shipment_info is not None


class ShipStatePartial(ui_states.BaseUIState):
    booking_state: BookingState | None = None
    boxes: int | None = None
    ship_date: dt.date | None = None
    service: str | None = None
    contact: pf_top.Contact | None = None
    address: pf_ext.AddressRecipient | None = None
    candidates: list[pf_ext.AddressRecipient] | None = None
    direction: ShipDirection | None = None


class ShipState(ShipStatePartial):
    boxes: pyd.PositiveInt = 1
    service: pf_shared.ServiceCode
    contact: pf_top.Contact
    address: pf_ext.AddressRecipient
    ship_date: types.fixed_date_type(7)
    direction: types.ShipDirection = 'out'


def response_alert_dict(response):
    return {a.message: a.type for a in response.alerts.alert} if response.alerts else {}


def state_alert_dict(state: BookingState):
    return response_alert_dict(state.response)
