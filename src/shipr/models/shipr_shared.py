from __future__ import annotations

import os
from datetime import date, timedelta
from enum import Enum
from typing import Literal, Annotated, Optional

import pydantic as pyd
import typing as _ty

from pydantic import BaseModel, ConfigDict, AliasGenerator, StringConstraints
from pydantic.alias_generators import to_pascal


def valid_ship_date_type() -> type[date]:
    tod = date.today()
    return pyd.condate(ge=tod, le=tod + timedelta(days=7))


ValidShipDate = valid_ship_date_type()
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

__all__ = [
    "ValidShipDate",
    "PrintType",
    "AlertType",
    "DeliveryKind",
    "DropOffInd",
    "DepartmentNum",
    "ServiceCode",
    "BasePFType",
    "Authentication",
    "Max80",
]


class OpeningHours(BasePFType):
    mon: Optional[Mon] = None
    tue: Optional[Tue] = None
    wed: Optional[Wed] = None
    thu: Optional[Thu] = None
    fri: Optional[Fri] = None
    sat: Optional[Sat] = None
    sun: Optional[Sun] = None
    bank_hol: Optional[BankHol] = None
