from __future__ import annotations

import datetime
import typing as _t
from datetime import date, timedelta

import pydantic
import pydantic as _p
import sqlalchemy as sqa
from loguru import logger

FormKind: _t.TypeAlias = _t.Literal['manual', 'select']  # noqa: UP040 fastui not support
ShipperScope = _t.Literal['SAND', 'LIVE']
ShipDirection = _t.Literal['in', 'out']

PrintType = _t.Literal['ALL_PARCELS', 'SINGLE_PARCEL']
AlertType = _t.Literal['ERROR', 'WARNING', 'NOTIFICATION']
DeliveryKind = _t.Literal['DELIVERY', 'COLLECTION']
DropOffInd = _t.Literal['PO', 'DEPOT']
DepartmentNum = 1

TOD = date.today()
SHIPPING_CUTOFF = datetime.time(17, 0)
ADVANCE_BOOKING_DAYS = 28
AVAILABLE_DATES = []

for i in range(ADVANCE_BOOKING_DAYS):
    if (TOD + timedelta(days=i)).weekday() < 5:
        if i == 0 and datetime.datetime.now().time() > SHIPPING_CUTOFF:
            continue
        AVAILABLE_DATES.append(TOD + timedelta(days=i))

WEEKDAYS_IN_RANGE = AVAILABLE_DATES
# WEEKDAYS_IN_RANGE = [TOD + timedelta(days=i) for i in range(ADVANCE_BOOKING_DAYS) if
#                      (TOD + timedelta(days=i)).weekday() < 5]

POSTCODE_PATTERN = r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})'
VALID_PC = _t.Annotated[
    str,
    _p.StringConstraints(pattern=POSTCODE_PATTERN),
    _p.BeforeValidator(lambda s: s.strip().upper()),
    _p.Field(description='A valid UK postcode'),
]


def limit_daterange_no_weekends(v: date) -> date:
    if v:
        if isinstance(v, str):
            v = datetime.date.fromisoformat(v)

        if isinstance(v, date):
            if v < TOD:
                logger.info(f'Date {v} is in the past - using today')
                v = TOD

            if v == TOD and datetime.datetime.now().time() > SHIPPING_CUTOFF:
                logger.warning('Current time is past shipping cutoff - using next available date')
                v = v + timedelta(days=1)

            if v > max(WEEKDAYS_IN_RANGE):
                logger.info(f'Date {v} is too far in the future - using latest available)')
                v = max(WEEKDAYS_IN_RANGE)

            if v.weekday() > 4:
                logger.info(f'Date {v} is a weekend - adjusting to previous Friday')
                v = v - timedelta(days=6 - v.weekday())
                if v < TOD or datetime.datetime.now().time() > SHIPPING_CUTOFF:
                    logger.info(f'Date {v} is in the past - adding 3 days')
                    v = v + timedelta(days=3)

            return v


SHIPPING_DATE = _t.Annotated[date, _p.AfterValidator(limit_daterange_no_weekends)]


class GenericJSONType(sqa.TypeDecorator):
    impl = sqa.JSON

    def __init__(self, model_class: type[pydantic.BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class

    def process_bind_param(self, value, dialect):
        return value.model_dump_json(round_trip=True) if value is not None else None

    def process_result_value(self, value, dialect):
        return self.model_class.model_validate_json(value) if value else None


class ExpressLinkError(Exception):
    ...
