import datetime
from abc import ABC

import pydantic as _p

from shipaw import ship_types
from shipaw.models import pf_ext, pf_top
from shipaw.ship_ui.states import ShipStateExtra


class Shipable(_p.BaseModel, ABC):
    model_config = _p.ConfigDict(
        extra='ignore',
        populate_by_name=True,
    )
    name: str = _p.Field(..., alias='Name')
    ship_date: ship_types.SHIPPING_DATE = _p.Field(datetime.date.today(), alias='Send Out Date')
    boxes: int = _p.Field(1, alias='Boxes')
    address: pf_ext.AddTypes
    contact: pf_top.Contact

    @property
    def ship_state(self):
        return ShipStateExtra.model_validate(self, from_attributes=True)
