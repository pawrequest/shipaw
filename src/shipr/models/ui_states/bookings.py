from __future__ import annotations

import pydantic as pyd
import sqlmodel as sqm

from pawsupport.sqlmodel_ps import sqlpr
from shipr.models.ui_states.abc import BaseUIState


class BaseBooking(sqm.SQLModel):
    state: BaseUIState = sqm.Field(
        sa_column=sqm.Column(sqlpr.GenericJSONType(BaseUIState))
    )


class BaseBookingDB(BaseBooking):
    """ subclass and set table = true"""
    id: int | None = sqm.Field(primary_key=True)


class BaseBookingOUT(BaseBookingDB, table=False):
    pass
