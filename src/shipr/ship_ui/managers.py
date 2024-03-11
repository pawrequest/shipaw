from __future__ import annotations

import sqlmodel as sqm
import sqlalchemy as sqa
from ..models import types
from fastuipr.states import BaseUIState
import typing as _t
import datetime as dt
from . import states

T = _t.TypeVar('T')


class BaseManager(_t.Generic[T], sqm.SQLModel):
    item: T = sqm.Field(sa_column=sqa.Column(types.GenericJSONType(T)))
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(types.GenericJSONType(states.ShipState))
    )
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)


class BaseManagerDB(BaseManager):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)


class BaseManagerOut(BaseManagerDB, table=False):
    id: int
