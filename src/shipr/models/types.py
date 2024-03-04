from __future__ import annotations

import datetime
import typing as _t
from datetime import date, timedelta

import pydantic as _p
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
