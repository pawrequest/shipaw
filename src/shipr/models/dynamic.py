from __future__ import annotations

import typing as _t
from abc import ABC
from datetime import date, timedelta
from enum import Enum, auto

import pydantic as _p
from fastui import class_name as _class_name
from fastui import components as c
from pydantic import BaseModel

from pawdantic.paw_strings import date_string
from pawdantic.pawui import styles
from shipr.models import pf_ext, pf_shared


def date_range_enum():
    return Enum(
        'DateRange',
        {str(d): date_string(d) for d in [date.today() + timedelta(days=i) for i in range(7)]}
    )


def make_address_enum(candidates: list[pf_ext.AddressRecipient]):
    return Enum(
        'AddressChoice',
        {f'address {i}': cand.address_line1 for i, cand in enumerate(candidates)}
    )


class BookingForm(BaseModel, ABC):
    boxes: BoxesEnum = _p.Field(description='Number of boxes')
    address: Enum
    ship_date: date_range_enum()
    ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: _t.Literal['in', 'out'] = 'out'


def make_booking_form_type(candidates: list[pf_ext.AddressRecipient]) -> type[BaseModel]:
    addr_enum = make_address_enum(candidates)

    class _Form(BookingForm):
        address: addr_enum

    return _Form


def address_first_lines(
        candidate: pf_ext.AddressRecipient,
        class_name: _class_name.ClassName = styles.ROW_STYLE,
):
    return c.Div(
        components=[
            c.Text(text=f'{candidate.address_line1} {candidate.address_line2}'),
        ],
        class_name=class_name
    )


class BoxesEnum(str, Enum):
    one = auto()
    two = auto()
    three = auto()
    four = auto()
    five = auto()
    six = auto()
    seven = auto()
    eight = auto()
    nine = auto()
    ten = auto()


class BoxesModelForm(_p.BaseModel):
    boxes: BoxesEnum
