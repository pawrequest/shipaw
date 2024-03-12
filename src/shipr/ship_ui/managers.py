from __future__ import annotations

import datetime as dt

import sqlmodel as sqm
import sqlalchemy as sqa

from ..models import types, base_item
from . import states


# class BookingManager(sqm.SQLModel):
#     ...
#     # state: states.ShipState
#     # item: base_item.BaseItem
#     # booking_date: dt.date
#
#
# class BookingManagerDB(BookingManager):
#     """subclass and set table = true"""
#     ...
#     # state: states.ShipState = sqm.Field(
#     #     sa_column=sqm.Column(types.GenericJSONType(states.ShipState))
#     # )
#     # item: base_item.BaseItem = sqm.Field(sa_column=sqa.Column(types.GenericJSONType(
#     #     base_item.BaseItem)))
#     # booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
#     # id: int | None = sqm.Field(primary_key=True)
#
#
# class BookingManagerOut(BookingManager, table=False):
#     ...
#     # id: int
