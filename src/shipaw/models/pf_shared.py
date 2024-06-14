# from __future__ import annotations
import datetime as dt
import enum
import typing as _t
from enum import Enum
from pathlib import Path

import sqlmodel as sqm
import pydantic as _p
from pydantic import BaseModel
from pydantic.alias_generators import to_pascal

from .. import ship_types


# class PFBaseModel(sqm.SQLModel):
class PFBaseModel(BaseModel):
    model_config = _p.ConfigDict(
        alias_generator=_p.AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,

    )


class ServiceCode(enum.StrEnum):
    EXPRESS24 = 'SND'
    EXPRESS9 = '09'
    EXPRESS10 = 'S10'
    EXPRESSAM = 'S12'
    EXPRESSPM = 'SPM'
    EXPRESS48 = 'SUP'


class ServiceCodeFull(enum.StrEnum):
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


class Authentication(PFBaseModel):
    user_name: _t.Annotated[str, _p.StringConstraints(max_length=80)]
    password: _t.Annotated[str, _p.StringConstraints(max_length=80)]


class Hours(PFBaseModel):
    open: str | None = None
    close: str | None = None
    close_lunch: str | None = None
    after_lunch_opening: str | None = None


class DayHours(PFBaseModel):
    hours: Hours | None = None


class OpeningHours(PFBaseModel):
    mon: DayHours | None = None
    tue: DayHours | None = None
    wed: DayHours | None = None
    thu: DayHours | None = None
    fri: DayHours | None = None
    sat: DayHours | None = None
    sun: DayHours | None = None
    bank_hol: DayHours | None = None


class HazardousGood(PFBaseModel):
    lqdgun_code: str | None = None
    lqdg_description: str | None = None
    lqdg_volume: float | None = None
    firearms: str | None = None


class Returns(PFBaseModel):
    returns_email: str | None = None
    email_message: str | None = None
    email_label: bool


class ContentDetail(PFBaseModel):
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


class DateTimeRange(PFBaseModel):
    from_: str = _p.Field(alias='From')
    to: str

    @classmethod
    def null_times_from_date(cls, null_date: dt.date):
        null_isodatetime = dt.datetime.combine(null_date, dt.time(0, 0)).isoformat(
            timespec='seconds'
        )
        return cls(from_=null_isodatetime, to=null_isodatetime)

    @classmethod
    def from_datetimes(cls, from_dt: dt.datetime, to_dt: dt.datetime):
        return cls(
            from_=from_dt.isoformat(timespec='seconds'),
            to=to_dt.isoformat(timespec='seconds')
        )


class ContentData(PFBaseModel):
    name: str
    data: str


class LabelItem(PFBaseModel):
    name: str
    data: str


class Barcode(PFBaseModel):
    name: str
    data: str


class Image(PFBaseModel):
    name: str
    data: str


class ManifestShipment(PFBaseModel):
    shipment_number: str
    service_code: str


class CompletedShipment(PFBaseModel):
    shipment_number: str | None = None
    out_bound_shipment_number: str | None = None
    in_bound_shipment_number: str | None = None
    partner_number: str | None = None


class CompletedCancelInfo(PFBaseModel):
    status: str | None = None
    shipment_number: str | None = None


class Position(PFBaseModel):
    longitude: float | None = None
    latitude: float | None = None


class Document(PFBaseModel):
    data: bytes

    def download(self, outpath: Path) -> Path:
        with open(outpath, 'wb') as f:
            f.write(self.data)
        return Path(outpath)


class Enhancement(PFBaseModel):
    enhanced_compensation: str | None = None
    saturday_delivery_required: bool | None = None


class Alert(PFBaseModel):
    code: int | None = None
    message: str
    type: ship_types.AlertType

    @classmethod
    def from_exception(cls, e: Exception):
        return cls(message=str(e), type='ERROR')


class NotificationType(str, Enum):
    EMAIL = 'EMAIL'
    EMAIL_DOD_INT = 'EMAILDODINT'
    EMAIL_ATTEMPT = 'EMAILATTEMPTDELIVERY'
    EMAIL_COLL_REC = 'EMAILCOLLRECEIVED'
    EMAIL_START_DEL = 'EMAILSTARTOFDELIVERY'
    DELIVERY = 'DELIVERYNOTIFICATION'
    SMS_DOD = 'SMSDAYOFDESPATCH'
    SMS_START_DEL = 'SMSSTARTOFDELIVERY'
    SMS_ATTEMPT_DEL = 'SMSATTEMPTDELIVERY'
    SMS_COLL_REC = 'SMSCOLLRECEIVED'


notification_label_map = {
    NotificationType.EMAIL: 'Email',
    NotificationType.EMAIL_DOD_INT: 'Email Day of Delivery Interactive',
    NotificationType.EMAIL_ATTEMPT: 'Email Attempted Delivery',
    NotificationType.EMAIL_COLL_REC: 'Email Collection Received',
    NotificationType.EMAIL_START_DEL: 'Email Start of Delivery',
    NotificationType.DELIVERY: 'Email Delivery',
    NotificationType.SMS_DOD: 'SMS Day of Despatch',
    NotificationType.SMS_START_DEL: 'SMS Start of Delivery',
    NotificationType.SMS_ATTEMPT_DEL: 'SMS Attempted Delivery',
    NotificationType.SMS_COLL_REC: 'SMS Collection Received',
}


#
# notification_label_map = {
#     'EMAIL': 'Email',
#     'EMAILDODINT': 'Email Day of Delivery Interactive',
#     'EMAIL_ATTEMPT': 'Email Attempted Delivery',
#     'EMAIL_COLL_REC': 'Email Collection Received',
#     'EMAIL_START_DEL': 'Email Start of Delivery',
#     'DELIVERY': 'Email Delivery',
#     'SMS_DOD': 'SMS Day of Despatch',
#     'SMS_START_DEL': 'SMS Start of Delivery',
#     'SMS_ATTEMPT_DEL': 'SMS Attempted Delivery',
#     'SMS_COLL_REC': 'SMS Collection Received',
# }


class CollectionNotificationType(str, Enum):
    EMAIL = 'EMAIL'
    EMAIL_RECIEVED = 'EMAILCOLLRECEIVED'
    SMS_RECIEVED = 'SMSCOLLRECEIVED'
