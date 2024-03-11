from __future__ import annotations

import datetime
import re
import typing as _t
from datetime import date, timedelta

import pydantic
import pydantic as _p
import sqlalchemy as sqa
from loguru import logger


def is_valid_date(v) -> _t.Literal['TRUE', 'HIGH', 'LOW', 'WK_END', 'ERROR']:
    if v and isinstance(v, date):
        if v < TOD:
            return 'LOW'
        if v > TOD + timedelta(days=7):
            return 'HIGH'
        if v.weekday() > 5:
            return 'WK_END'
        return 'TRUE'
    if isinstance(v, str):
        try:
            v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
            return is_valid_date(v)
        except ValueError:
            return 'ERROR'


def fix_date(v: date) -> date:
    date_range = [TOD + datetime.timedelta(days=x) for x in range(7)]
    weekday_dates = [d for d in date_range if d.weekday() < 5]
    latest_wkd = max(weekday_dates)
    res = is_valid_date(v)
    match res:
        case 'TRUE':
            return v
        case 'LOW':
            logger.info(f'Date {v} is in the past - using today')
            return TOD
        case 'HIGH':
            logger.info(f'Date {v} is too far in the future - using {latest_wkd}')
            return latest_wkd
        case 'WK_END':
            logger.info(f'Date {v} is a weekend - using {latest_wkd}')
            return latest_wkd
        case _:
            raise ValueError(f'unable to fix date: {v}')


TOD = date.today()
ValidShipDateType = _p.condate(ge=TOD, le=TOD + timedelta(days=7))
PrintType = _t.Literal['ALL_PARCELS', 'SINGLE_PARCEL']
AlertType = _t.Literal['ERROR', 'WARNING', 'NOTIFICATION']
DeliveryKind = _t.Literal['DELIVERY']
DropOffInd = _t.Literal['PO', 'DEPOT']
DepartmentNum = 1
ValidatedShipDate = _t.Annotated[ValidShipDateType, _p.BeforeValidator(fix_date)]


def validate_str(v):
    # return v
    if v:
        v = v.replace(r'/', '')
    return v or ''


SafeStr = _t.Annotated[str, _p.BeforeValidator(validate_str)]


def truncate_before(maxlength) -> _p.BeforeValidator:
    def _truncate(v):
        if v:
            if len(v) > maxlength:
                return v[:maxlength]
        return v

    return _p.BeforeValidator(_truncate)


def TruncatedSafeStr(max_length: int):
    return _t.Annotated[
        SafeStr, _p.StringConstraints(max_length=max_length), truncate_before(max_length)]


def TruncatedSafeMaybeStr(max_length: int):
    return _t.Annotated[
        SafeStr, _p.StringConstraints(max_length=max_length), truncate_before(max_length), _p.Field(
            ''
        )
    ]


excluded_chars = {'C', 'I', 'K', 'M', 'O', 'V'}


def validate_uk_postcode(v: str):
    pattern = re.compile(r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})')
    if not re.match(pattern, v) and not set(v[-2:]).intersection(excluded_chars):
        raise _p.ValidationError('Invalid UK postcode')
    return v


def is_valid_postcode(s):
    pattern = re.compile(r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})')
    return bool(re.match(pattern, s))


ValidPostcode = _t.Annotated[
    str, _p.BeforeValidator(validate_uk_postcode), _p.BeforeValidator(lambda v: v.upper())]


def default_gen(typ, **kwargs):
    return _t.Annotated[typ, _p.Field(**kwargs)]


class GenericJSONType(sqa.TypeDecorator):
    impl = sqa.JSON

    def __init__(self, model_class: type[pydantic.BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class

    def process_bind_param(self, value, dialect):
        return value.model_dump_json(round_trip=True) if value is not None else None

    def process_result_value(self, value, dialect):
        return self.model_class.model_validate_json(value) if value else None


ShipperScope = _t.Literal['SAND', 'LIVE']
