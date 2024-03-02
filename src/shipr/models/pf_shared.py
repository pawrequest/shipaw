from __future__ import annotations

import datetime
import os
from datetime import date, timedelta
from enum import Enum
from typing import Annotated, Literal, Optional
import typing as _ty

import pydantic as pyd
from loguru import logger
from pydantic import AliasGenerator, BaseModel, ConfigDict, StringConstraints
from pydantic.alias_generators import to_pascal

tod = date.today()
date_range = [tod + datetime.timedelta(days=x) for x in range(7)]
weekday_dates = [d for d in date_range if d.weekday() < 5]


def valid_ship_date_type() -> type[date]:
    tod = date.today()
    return pyd.condate(ge=tod, le=tod + timedelta(days=7))


ValidShipDateType = pyd.condate(ge=tod, le=tod + timedelta(days=7))


def is_valid_date(v) -> bool | Literal['HIGH', 'LOW', 'WKEND']:
    if v and isinstance(v, date):
        if v < tod:
            return "LOW"
        if v > tod + timedelta(days=7):
            return "HIGH"
        if v.weekday() > 5:
            return "WKEND"
        return True
    if isinstance(v, str):
        try:
            v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
            return is_valid_date(v)
        except ValueError:
            return False


def latest_weekday() -> date:
    return max(weekday_dates)


def fix_date(v: date) -> date:
    res = is_valid_date(v)
    latest_wkd = max(weekday_dates)
    match res:
        case True:
            return v
        case "LOW":
            logger.info(f"Date {v} is in the past - using today")
            return tod
        case "HIGH":
            logger.info(f"Date {v} is too far in the future - using {latest_wkd}")
            return latest_wkd
        case "WKEND":
            logger.info(f"Date {v} is a weekend - using {latest_wkd}")
            return latest_wkd
        case _:
            raise ValueError(f"unable to fix date: {v}")


# Valid_D = Annotated[date, pydantic.AfterValidator(lambda v: v >= date.today())]


ValidatedShipDate = Annotated[ValidShipDateType, pyd.BeforeValidator(fix_date)]

PrintType = _ty.Literal["ALL_PARCELS", "SINGLE_PARCEL"]
AlertType = Literal["ERROR", "WARNING", "NOTIFICATION"]
DeliveryKind = Literal['DELIVERY']
DropOffInd = Literal["PO", "DEPOT"]
DepartmentNum = 1


class ServiceCode(str, Enum):
    FLEX_DELIVERY_SERVICE_PRODUCT = "S09"
    EXPRESS9 = "09"
    EXPRESS9_SECURE = "SEN"
    EXPRESS9_COURIER_PACK = "SC9"
    EXPRESS10 = "S10"
    EXPRESS10_SECURE = "SEE"
    EXPRESS10_EXCHANGE = "SWN"
    EXPRESS10_SECURE_EXCHANGE = "SSN"
    EXPRESS10_COURIER_PACK = "SC0"
    EXPRESSAM = "S12"
    EXPRESSAM_LARGE = "SAML"
    EXPRESSAM_SECURE = "SET"
    EXPRESSAM_EXCHANGE = "SWT"
    EXPRESSAM_SECURE_EXCHANGE = "SST"
    EXPRESSAM_COURIER_PACK = "SC2"
    EXPRESSAM_SUNDAY_B2B = "SC2P"
    EXPRESSPM = "SPM"
    EXPRESSPM_SECURE = "SEM"
    EXPRESSPM_EXCHANGE = "SWP"
    EXPRESSPM_SECURE_EXCHANGE = "SSP"
    EXPRESS24 = "SND"
    EXPRESS24_LARGE = "S24L"
    EXPRESS24_SECURE = "SEF"
    EXPRESS24_EXCHANGE = "SWR"
    EXPRESS24_SECURE_EXCHANGE = "SSF"
    EXPRESS24_COURIER_PACK = "SCD"
    EXPRESS24_SUNDAY = "SCDP"
    EXPRESS48 = "SUP"
    EXPRESS48_LARGE = "SID"
    PARCELRIDER_PLUS_NI_ONLY = "SPR"
    EXPRESSCOLLECT = "SMS"
    GLOBALBULK_DIRECT = "GBD"
    GLOBALECONOMY = "IPE"
    GLOBALEXPRESS = "GEX"
    GLOBALEXPRESS_ENVELOPE_DELIVERY = "GXE"
    GLOBALEXPRESS_PACK_DELIVERY = "GXP"
    GLOBALPRIORITY = "GPR"
    GLOBALPRIORITY_H_M_FORCES = "GPR"
    GLOBALPRIORITY_RETURNS = "EPR"
    GLOBALVALUE = "GVA"
    EURO_ECONOMY = "EPH"
    EURO_PRIORITY = "EPB"
    EURO_PRIORITY_PACK = "EPK"
    EUROPRIORITY_HOME_PO_BOXES = "EPP"
    IRELANDEXPRESS = "I24"


class BasePFType(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
    )


class Authentication(BasePFType):
    user_name: Max80
    password: Max80

    @classmethod
    def from_env(cls):
        username = os.getenv("PF_EXPR_SAND_USR")
        password = os.getenv("PF_EXPR_SAND_PWD")
        return cls(user_name=username, password=password)


Max80 = Annotated[str, StringConstraints(max_length=80)]


class DayHours(BasePFType):
    hours: Hours | None = None


class OpeningHours(BasePFType):
    mon: DayHours | None = None
    tue: DayHours | None = None
    wed: DayHours | None = None
    thu: DayHours | None = None
    fri: DayHours | None = None
    sat: DayHours | None = None
    sun: DayHours | None = None
    bank_hol: DayHours | None = None


class Hours(BasePFType):
    open: Optional[str] = None
    close: Optional[str] = None
    close_lunch: Optional[str] = None
    after_lunch_opening: Optional[str] = None
