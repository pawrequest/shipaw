from __future__ import annotations

import os
import typing as _t

from . import types
from enum import Enum
from pathlib import Path

import pydantic as _p
from pydantic.alias_generators import to_pascal


# Valid_D = Annotated[date, pydantic.AfterValidator(lambda v: v >= date.today())]


class ServiceCode(str, Enum):
    FLEX_DELIVERY_SERVICE_PRODUCT = 'S09'
    EXPRESS9 = '09'
    EXPRESS9_SECURE = 'SEN'
    EXPRESS9_COURIER_PACK = 'SC9'
    EXPRESS10 = 'S10'
    EXPRESS10_SECURE = 'SEE'
    EXPRESS10_EXCHANGE = 'SWN'
    EXPRESS10_SECURE_EXCHANGE = 'SSN'
    EXPRESS10_COURIER_PACK = 'SC0'
    EXPRESSAM = 'S12'
    EXPRESSAM_LARGE = 'SAML'
    EXPRESSAM_SECURE = 'SET'
    EXPRESSAM_EXCHANGE = 'SWT'
    EXPRESSAM_SECURE_EXCHANGE = 'SST'
    EXPRESSAM_COURIER_PACK = 'SC2'
    EXPRESSAM_SUNDAY_B2B = 'SC2P'
    EXPRESSPM = 'SPM'
    EXPRESSPM_SECURE = 'SEM'
    EXPRESSPM_EXCHANGE = 'SWP'
    EXPRESSPM_SECURE_EXCHANGE = 'SSP'
    EXPRESS24 = 'SND'
    EXPRESS24_LARGE = 'S24L'
    EXPRESS24_SECURE = 'SEF'
    EXPRESS24_EXCHANGE = 'SWR'
    EXPRESS24_SECURE_EXCHANGE = 'SSF'
    EXPRESS24_COURIER_PACK = 'SCD'
    EXPRESS24_SUNDAY = 'SCDP'
    EXPRESS48 = 'SUP'
    EXPRESS48_LARGE = 'SID'
    PARCELRIDER_PLUS_NI_ONLY = 'SPR'
    EXPRESSCOLLECT = 'SMS'
    GLOBALBULK_DIRECT = 'GBD'
    GLOBALECONOMY = 'IPE'
    GLOBALEXPRESS = 'GEX'
    GLOBALEXPRESS_ENVELOPE_DELIVERY = 'GXE'
    GLOBALEXPRESS_PACK_DELIVERY = 'GXP'
    GLOBALPRIORITY = 'GPR'
    GLOBALPRIORITY_H_M_FORCES = 'GPR'
    GLOBALPRIORITY_RETURNS = 'EPR'
    GLOBALVALUE = 'GVA'
    EURO_ECONOMY = 'EPH'
    EURO_PRIORITY = 'EPB'
    EURO_PRIORITY_PACK = 'EPK'
    EUROPRIORITY_HOME_PO_BOXES = 'EPP'
    IRELANDEXPRESS = 'I24'


class BasePFType(_p.BaseModel):
    model_config = _p.ConfigDict(
        alias_generator=_p.AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
    )


class Authentication(BasePFType):
    user_name: _t.Annotated[str, _p.StringConstraints(max_length=80)]
    password: _t.Annotated[str, _p.StringConstraints(max_length=80)]

    @classmethod
    def from_env(cls, scope: types.ShipperScope = 'SAND'):
        username = os.getenv(f'PF_EXPR_{scope}_USR')
        password = os.getenv(f'PF_EXPR_{scope}_PWD')
        return cls(user_name=username, password=password)


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
    open: str | None = None
    close: str | None = None
    close_lunch: str | None = None
    after_lunch_opening: str | None = None


class HazardousGood(BasePFType):
    lqdgun_code: str | None = None
    lqdg_description: str | None = None
    lqdg_volume: float | None = None
    firearms: str | None = None


class Returns(BasePFType):
    returns_email: str | None = None
    email_message: str | None = None
    email_label: bool


class ContentDetail(BasePFType):
    country_of_manufacture: str
    country_of_origin: str | None = None
    manufacturers_name: str | None = None
    description: str
    unit_weight: float
    unit_quantity: int
    unit_value: float
    currency: str
    tariff_code: str | None = None
    tariff_description: str | None = None
    article_reference: str | None = None


class DateTimeRange(BasePFType):
    from_: str
    to: str


class ContentData(BasePFType):
    name: str
    data: str


class LabelItem(BasePFType):
    name: str
    data: str


class Barcode(BasePFType):
    name: str
    data: str


class Image(BasePFType):
    name: str
    data: str


class ManifestShipment(BasePFType):
    shipment_number: str
    service_code: str


class CompletedShipment(BasePFType):
    shipment_number: str | None = None
    out_bound_shipment_number: str | None = None
    in_bound_shipment_number: str | None = None
    partner_number: str | None = None


class CompletedCancelInfo(BasePFType):
    status: str | None = None
    shipment_number: str | None = None


class Position(BasePFType):
    longitude: float | None = None
    latitude: float | None = None


class Document(BasePFType):
    data: bytes

    def download(self, outpath: Path) -> Path:
        with open(outpath, 'wb') as f:
            f.write(self.data)
        return Path(outpath)


class Enhancement(BasePFType):
    enhanced_compensation: str | None = None
    saturday_delivery_required: bool | None = None


class Alert(BasePFType):
    code: int
    message: str
    type: types.AlertType
