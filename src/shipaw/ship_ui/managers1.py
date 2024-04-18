from __future__ import annotations

import sqlmodel as sqm

import shipaw.shipaw_types
from pawdantic.pawui import states

class BaseManager(sqm.SQLModel):
    state: states.BaseUIState = sqm.Field(sa_column=sqm.Column(
        shipaw.types.GenericJSONType(states.BaseUIState)))


class BaseManagerDB(BaseManager):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)


class BaseManagerOut(BaseManagerDB, table=False):
    id: int
