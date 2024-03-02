# from __future__ import annotations
import base64
import datetime as dt
import pathlib

import pydantic as pyd
import sqlmodel as sqm

from pawsupport.sqlmodel_ps import sqlpr
from shipr.models import pf_ext, pf_msg, pf_shared, pf_top
from shipr.models.ui_states.abc import BaseUIState


# if _ty.TYPE_CHECKING:
#     pass


class BookedState(BaseUIState):
    request: pf_msg.CreateShipmentRequest = sqm.Field(
        sa_column=sqm.Column(sqlpr.GenericJSONType(pf_msg.CreateShipmentRequest))
    )
    response: pf_msg.CreateShipmentResponse = sqm.Field(
        sa_column=sqm.Column(sqlpr.GenericJSONType(pf_msg.CreateShipmentResponse))
    )
    label_path: pathlib.Path | None = None
    printed: bool = False

    def shipment_num(self):
        return self.response.completed_shipment_info.completed_shipments.completed_shipment[
            0].shipment_number if self.booked else None

    def alerts(self):
        return self.state.response.alerts.alert

    @property
    def booked(self):
        return self.response.completed_shipment_info is not None


class ShipStatePartial(BaseUIState):
    book_state: BookedState | None = None
    boxes: int | None = None
    ship_date: dt.date = None
    ship_service: str | None = None
    contact: pf_top.Contact | None = None
    address: pf_ext.AddressRecipient | None = None


class ShipState(ShipStatePartial):
    book_state: BookedState | None = None
    boxes: pyd.PositiveInt = 1
    ship_service: pf_shared.ServiceCode
    contact: pf_top.Contact
    address: pf_ext.AddressRecipient
    ship_date: pf_shared.ValidatedShipDate


def update_get_partial64(partial_class, **kwargs) -> str:
    state = partial_class.model_validate(kwargs)
    state_j = state.model_dump_json(exclude_none=True)
    return base64.urlsafe_b64encode(state_j.encode()).decode()


