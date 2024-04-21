from __future__ import annotations

import typing as _t
from abc import ABC
from datetime import timedelta, date
from enum import Enum, auto

import pawdantic.paw_strings
import pydantic as _p
from fastui import class_name as _class_name, components as c, forms as fastui_forms
import pawdantic.paw_strings
from pawdantic.paw_strings import date_string
from pydantic import BaseModel
from pawdantic.pawui import styles

from shipaw.models import pf_ext, pf_shared

ADVANCE_BOOKING_RANGE = 28

DATE_RANGE_LIST = [
    date.today() + timedelta(days=i)
    for i in range(ADVANCE_BOOKING_RANGE)
    if (date.today() + timedelta(days=i)).weekday() < 5
]
DATE_RANGE_DICT = {d.isoformat(): date_string(d) for d in DATE_RANGE_LIST}


def date_select_options() -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=str(d.isoformat()),
            label=pawdantic.paw_strings.date_string(d),
        )
        for d in DATE_RANGE_LIST
    ]


def address_select_options(candidates: list[pf_ext.AddTypes]) -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=cand.model_dump_json(),
            label=cand.lines_str_oneline,
        )
        for cand in candidates
    ]


def address_enum(candidates: list[pf_ext.AddTypes]):
    return Enum('AddressChoice', {f'address {i}': cand.address_line1 for i, cand in enumerate(candidates)})


def date_range_enum():
    return Enum('DateRange', DATE_RANGE_DICT)


class BookingForm(BaseModel, ABC):
    boxes: BoxesEnum = _p.Field(description='Number of boxes')
    address: Enum
    ship_date: date_range_enum()
    service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: _t.Literal['in', 'out'] = 'out'


def booking_form_type(candidates: list[pf_ext.AddTypes]) -> type[BaseModel]:
    addr_enum = address_enum(candidates)

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
        class_name=class_name,
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
