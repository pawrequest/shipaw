from __future__ import annotations

import sqlmodel as sqm

from fastui.states import BaseUIState
from pawsupport.sqlmodel_ps import sqlpr


class BaseManager(sqm.SQLModel):
    state: BaseUIState = sqm.Field(sa_column=sqm.Column(sqlpr.GenericJSONType(BaseUIState)))


class BaseManagerDB(BaseManager):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)


class BaseManagerOut(BaseManagerDB, table=False):
    id: int
