from __future__ import annotations

from enum import StrEnum
import datetime as dt

import phonenumbers
from loguru import logger


class ShipDirection(StrEnum):
    INBOUND = 'in'
    OUTBOUND = 'out'
    DROPOFF = 'dropoff'


TOD = dt.date.today()
COLLECTION_CUTOFF = dt.time(23, 59, 59)
ADVANCE_BOOKING_DAYS = 28
WEEKDAYS_IN_RANGE = [
    TOD + dt.timedelta(days=i) for i in range(ADVANCE_BOOKING_DAYS) if (TOD + dt.timedelta(days=i)).weekday() < 5
]

COLLECTION_WEEKDAYS = [i for i in WEEKDAYS_IN_RANGE if not i == TOD]

# COLLECTION_TIME_FROM = dt.time(0, 0)
# COLLECTION_TIME_TO = dt.time(0, 0)



def limit_daterange_no_weekends(v: dt.date) -> dt.date:
    logger.debug(f'Validating date: {v}')
    if v:
        if isinstance(v, str):
            logger.debug(f'parsing date string assuming isoformat: {v}')
            v = dt.date.fromisoformat(v)

        if isinstance(v, dt.date):
            if v < TOD or v.weekday() > 4:
                logger.debug(f'Date {v} is a weekend or in the past - using next weekday')
                v = min(WEEKDAYS_IN_RANGE)

            if v > max(WEEKDAYS_IN_RANGE):
                logger.debug(f'Date {v} is too far in the future - using latest weekday (max 28 days in advance)')
                v = max(WEEKDAYS_IN_RANGE)

    return v


def validate_phone(v: str, values) -> str:
    logger.warning(f'Validating phone: {v}')
    phone = v.replace(' ', '')
    nummy = phonenumbers.parse(phone, 'GB')
    assert phonenumbers.is_valid_number(nummy)
    return phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.E164)


# ConvertMode = Literal['pydantic', 'python', 'python-alias', 'json', 'json-alias']


# def pydantic_export(obj: BaseModel, mode: ConvertMode) -> dict | BaseModel | str:
#     match mode:
#         case 'pydantic':
#             return obj
#         case 'python':
#             return obj.model_dump(mode='json', by_alias=False)
#         case 'python-alias':
#             return obj.model_dump(mode='json', by_alias=True)
#         case 'json':
#             return obj.model_dump_json(by_alias=False)
#         case 'json-alias':
#             return obj.model_dump_json(by_alias=True)
#         case _:
#             raise ValueError(f'Invalid ConvertMode: {mode}')

