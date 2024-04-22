from __future__ import annotations

import pathlib
import typing as _t

import pydantic as pyd
import sqlmodel as sqm
from pawdantic.pawui import states as ui_states
from pydantic import ConfigDict, Field
<<<<<<< HEAD
from shipaw.models import pf_ext, pf_shared, pf_top
from shipaw.ship_types import ShipDirection

=======

from shipaw.models import pf_ext, pf_shared, pf_top
from shipaw.ship_types import ShipDirection
>>>>>>> recov
from .. import msgs, pf_config, ship_types

BookingReqSQM = _t.Annotated[
    msgs.CreateShipmentRequest, sqm.Field(sa_column=sqm.Column(ship_types.GenericJSONType(msgs.CreateShipmentRequest)))
]
BookingRespSQM = _t.Annotated[
    msgs.CreateShipmentResponse,
    sqm.Field(sa_column=sqm.Column(ship_types.GenericJSONType(msgs.CreateShipmentResponse))),
]


class BookingState(ui_states.BaseUIState):
    request: BookingReqSQM
    response: BookingRespSQM
    label_downloaded: bool = False
    label_dl_path: pathlib.Path | None = None

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
<<<<<<< HEAD
    address: pf_ext.AddressRecipient | None = None
    candidates: list[pf_ext.AddressRecipient] | None = None
=======
    address: pf_ext.AddTypes | None = None
    candidates: list[pf_ext.AddTypes] | None = None
>>>>>>> recov
    direction: ShipDirection | None = None
    reference: str | None = None
    special_instructions: str | None = None

    @property
    def pf_label_name(self):
<<<<<<< HEAD
        return f"Parcelforce Collection Label for {self.contact.business_name} on {self.ship_date}"
=======
        return f'Parcelforce Collection Label for {self.contact.business_name} on {self.ship_date}'
>>>>>>> recov

    @property
    def named_label_path(self):
        sett = pf_config.PF_SETTINGS
<<<<<<< HEAD
        return (sett.label_dir / self.pf_label_name).with_suffix(".pdf")
=======
        return (sett.label_dir / self.pf_label_name).with_suffix('.pdf')
>>>>>>> recov


class ShipState(ShipStatePartial):
    contact: pf_top.Contact
<<<<<<< HEAD
    address: pf_ext.AddressRecipient
    ship_date: ship_types.SHIPPING_DATE
    boxes: pyd.PositiveInt = 1
    service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: ship_types.ShipDirection = "out"
    candidates: list[pf_ext.AddressRecipient] | None = Field(None)
=======
    address: pf_ext.AddTypes
    ship_date: ship_types.SHIPPING_DATE
    boxes: pyd.PositiveInt = 1
    service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: ship_types.ShipDirection = 'out'
    candidates: list[pf_ext.AddTypes] | None = Field(None)
>>>>>>> recov
    reference: str | None = None
    special_instructions: str | None = None


class ShipStateExtra(ShipState):
<<<<<<< HEAD
    model_config = ConfigDict(
        extra="ignore",
    )
=======
    model_config = ConfigDict(extra='ignore')
>>>>>>> recov


def response_alert_dict(response):
    return {a.message: a.type for a in response.alerts.alert} if response.alerts else {}


def state_alert_dict(state: BookingState):
    return response_alert_dict(state.response)


class ShipStateBooked(ShipState):
    booking_state: BookingState
