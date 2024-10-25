# from __future__ import annotations

import re
import typing as _t
from enum import Enum, StrEnum
import datetime as dt

import phonenumbers
import pydantic as _p
from loguru import logger

DepartmentNum = 1


class PrintType(StrEnum):
    ALL_PARCELS = 'ALL_PARCELS'
    SINGLE_PARCEL = 'SINGLE_PARCEL'


class ShipmentType(StrEnum):
    DELIVERY = 'DELIVERY'
    COLLECTION = 'COLLECTION'


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class ShipDirection(StrEnum):
    INBOUND = 'in'
    OUTBOUND = 'out'
    DROPOFF = 'dropoff'


class DropOffInd(StrEnum):
    PO = 'PO'
    DEPOT = 'DEPOT'


class DeliveryKindEnum(str, Enum):
    DELIVERY = 'DELIVERY'
    COLLECTION = 'COLLECTION'


TOD = dt.date.today()
COLLECTION_CUTOFF = dt.time(23, 59, 59)
ADVANCE_BOOKING_DAYS = 28
WEEKDAYS_IN_RANGE = [
    TOD + dt.timedelta(days=i) for i in range(ADVANCE_BOOKING_DAYS) if (TOD + dt.timedelta(days=i)).weekday() < 5
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


def limit_daterange_no_weekends(v: dt.date) -> dt.date:
    logger.debug(f'Validating date: {v}')
    if v:
        if isinstance(v, str):
            logger.debug(f'Validating date string: {v}')
            v = dt.date.fromisoformat(v)

        if isinstance(v, dt.date):
            if v < TOD or v.weekday() > 4:
                logger.debug(f'Date {v} is a weekend or in the past - using next weekday')
                v = min(WEEKDAYS_IN_RANGE)

            if v > max(WEEKDAYS_IN_RANGE):
                logger.debug(f'Date {v} is too far in the future - using latest weekday (max 28 days in advance)')
                v = max(WEEKDAYS_IN_RANGE)

            return v


# SHIPPING_DATE = date


class ExpressLinkError(Exception):
    ...


class ExpressLinkWarning(Exception):
    ...


class ExpressLinkNotification(Exception):
    ...


def validate_phone(v: str, values) -> str:
    logger.warning(f'Validating phone: {v}')
    phone = v.replace(' ', '')
    nummy = phonenumbers.parse(phone, 'GB')
    assert phonenumbers.is_valid_number(nummy)
    return phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.E164)


def prep_phone(v: str) -> str:
    if isinstance(v, str):
        # logger.debug(f'Prepping phone: {v}')
        v = v.replace(' ', '')
        # try:
        #     nummy = phonenumbers.parse(v, 'GB')
        #     assert phonenumbers.is_valid_number(nummy)
        #     v = phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.NATIONAL).replace(' ', '')
        # except phonenumbers.phonenumberutil.NumberParseException:
        #     logger.warning(f'Unable to parse phone number: {v}')
        # except AssertionError:
        #     logger.warning(f'Invalid phone number: {v}')
    return v


MyPhone = _t.Annotated[str, _p.BeforeValidator(prep_phone)]
