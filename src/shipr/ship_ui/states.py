from __future__ import annotations

import datetime as dt
import pathlib
import typing as _t

import pydantic as pyd
import sqlmodel as sqm

import shipr.models
import shipr.models.types
from fastuipr.states import BaseUIState
from pawsupport.sqlmodel_ps import sqlpr
from shipr.models import pf_ext, pf_shared, pf_top

from .. import msgs

BookingReqSQM = _t.Annotated[
    msgs.CreateShipmentRequest, sqm.Field(sa_column=sqm.Column(sqlpr.GenericJSONType(msgs.CreateShipmentRequest)))
]
BookingRespSQM = _t.Annotated[
    msgs.CreateShipmentResponse, sqm.Field(sa_column=sqm.Column(sqlpr.GenericJSONType(msgs.CreateShipmentResponse)))
]


class BookingState(BaseUIState):
    request: BookingReqSQM
    response: BookingRespSQM
    label_path: pathlib.Path | None = None
    printed: bool = False

    def shipment_num(self):
        return (
            self.response.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
            if self.booked
            else None
        )

    def alerts(self):
        return self.state.response.alerts.alert

    @property
    def booked(self):
        return self.response.completed_shipment_info is not None


class ShipStatePartial(BaseUIState):
    booking_state: BookingState | None = None
    boxes: int | None = None
    ship_date: dt.date | None = None
    ship_service: str | None = None
    contact: pf_top.Contact | None = None
    address: pf_ext.AddressRecipient | None = None


class ShipState(ShipStatePartial):
    booking_state: BookingState | None = None
    boxes: pyd.PositiveInt = 1
    ship_service: pf_shared.ServiceCode
    contact: pf_top.Contact
    address: pf_ext.AddressRecipient
    ship_date: shipr.models.types.ValidatedShipDate
