from __future__ import annotations

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
    send_date: ship_types.SHIPPING_DATE = _p.Field(datetime.date.today(), alias='Send Out Date')
    boxes: int = 1
    address: pf_ext.AddressRecipient
    contact: pf_top.Contact

    @property
    def ship_state(self):
        return ShipStateExtra.model_validate(self, from_attributes=True)


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}
