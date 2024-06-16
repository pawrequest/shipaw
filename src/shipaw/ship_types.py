from __future__ import annotations

import datetime
import datetime as dt
import re
import typing as _t
from datetime import date, timedelta
from enum import StrEnum, Enum

import pydantic
import pydantic as _p
import sqlalchemy as sqa
from loguru import logger

FormKind: _t.TypeAlias = _t.Literal['manual', 'select']  # fastui not support
ShipperScope = _t.Literal['SAND', 'LIVE']
# ShipDirection = _t.Literal['in', 'out', 'dropoff']

PrintType = _t.Literal['ALL_PARCELS', 'SINGLE_PARCEL']
# AlertType = _t.Literal['ERROR', 'WARNING', 'NOTIFICATION']
DeliveryKind = _t.Literal['DELIVERY', 'COLLECTION']
DropOffInd = _t.Literal['PO', 'DEPOT']
DepartmentNum = 1

class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'

class ShipDirection(StrEnum):
    IN = 'in'
    OUT = 'out'
    DROPOFF = 'dropoff'


class DropOffIndEnum(StrEnum):
    PO = 'PO'
    DEPOT = 'DEPOT'


class DeliveryKindEnum(str, Enum):
    DELIVERY = 'DELIVERY'
    COLLECTION = 'COLLECTION'


TOD = date.today()
COLLECTION_CUTOFF = datetime.time(23, 59, 59)
ADVANCE_BOOKING_DAYS = 28
WEEKDAYS_IN_RANGE = [
    TOD + timedelta(days=i) for i in range(ADVANCE_BOOKING_DAYS) if
    (TOD + timedelta(days=i)).weekday() < 5
]

COLLECTION_WEEKDAYS = [i for i in WEEKDAYS_IN_RANGE if not i == TOD]

COLLECTION_TIME_FROM = dt.time(0, 0)
COLLECTION_TIME_TO = dt.time(0, 0)

POSTCODE_PATTERN = r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})'
VALID_POSTCODE = _t.Annotated[
    str,
    _p.StringConstraints(pattern=POSTCODE_PATTERN),
    _p.BeforeValidator(lambda s: s.strip().upper()),
    _p.Field(description='A valid UK postcode'),
]


def is_valid_postcode(pc):
    return bool(re.match(POSTCODE_PATTERN, pc.strip().upper()))


def limit_daterange_no_weekends(v: date) -> date:
    if v:
        if isinstance(v, str):
            logger.debug(f'Validating date string: {v}')
            v = datetime.date.fromisoformat(v)

        if isinstance(v, date):
            if v < TOD or v.weekday() > 4:
                logger.info(f'Date {v} is a weekend or in the past - using next weekday')
                v = min(WEEKDAYS_IN_RANGE)

            if v > max(WEEKDAYS_IN_RANGE):
                logger.info(
                    f'Date {v} is too far in the future - using latest weekday (max 28 days in advance)'
                )
                v = max(WEEKDAYS_IN_RANGE)

            logger.debug(f'Validated date: {v}')
            return v


# SHIPPING_DATE = date




class ExpressLinkError(Exception):
    ...
