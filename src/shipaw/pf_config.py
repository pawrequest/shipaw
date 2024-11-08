from __future__ import annotations

import functools
import os
from pathlib import Path

import pydantic as _p
from loguru import logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from shipaw.models import pf_lists, pf_models, pf_shared, pf_top
from shipaw.ship_types import MyPhone, ShipDirection

SHIP_ENV = os.getenv('SHIP_ENV')
if not Path(SHIP_ENV).exists():
    raise ValueError('SHIP_ENV not set')


class PFSettings(BaseSettings):
    """Load Parcelforce ExpressLink configuration from environment variables.

    location of environment file is set by the environment variable SHIP_ENV.
    """

    pf_ac_num_1: str
    pf_contract_num_1: str
    pf_ac_num_2: str | None
    pf_contract_num_2: str | None
    department_id: int = 1

    ship_live: bool = False
    pf_expr_usr: SecretStr
    pf_expr_pwd: SecretStr

    pf_wsdl: str = r'R:\paul_r\.internal\expresslink_api.wsdl'
    pf_binding: str = r'{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'
    tracking_url_stem: str = r'https://www.parcelforce.com/track-trace?trackNumber='
    pf_endpoint: str

    label_dir: Path

    home_address_line1: str
    home_address_line2: str | None = None
    home_address_line3: str | None = None
    home_town: str
    home_postcode: str
    home_country: str = 'GB'
    home_business_name: str
    home_contact_name: str
    home_email: str
    home_phone: MyPhone | None = None
    home_mobile_phone: MyPhone

    home_address: pf_models.AddressCollection | None = None
    home_contact: pf_top.Contact | None = None

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=SHIP_ENV)

    @_p.field_validator('label_dir', mode='after')
    def make_path(cls, v, values):
        dirs = [_ for _ in ShipDirection]
        for subdir in dirs:
            apath = v / subdir
            if not apath.exists():
                apath.mkdir(parents=True, exist_ok=True)
        return v

    #
    # @_p.field_validator('label_dir', mode='after')
    # def make_path(cls, v, values):
    #     for apath in [v / i for i in ['in', 'out', 'dropoff']]:
    #         if not apath.exists():
    #             v.mkdir(parents=True, exist_ok=True)
    #         return v

    # @_p.field_validator('pf_wsdl', mode='after')
    # def get_wsdl(cls, v, values):
    #     if v is None or not Path(v).is_file():
    #         try:
    #             v = r"R:\paul_r\.internal\expresslink_api.wsdl"
    #             assert Path(v).is_file()
    #             logger.info(f'WSDL path not provided - using hardcoded {v}')
    #         except (AssertionError, FileNotFoundError) as e:
    #             with resources.path(rsrc, 'expresslink_api.wsdl') as wsdl_path:
    #                 logger.info(f'WSDL path not provided - using {wsdl_path} from importlib.resources')
    #                 v = str(wsdl_path)
    #     return v

    def auth(self):
        return pf_shared.Authentication(
            user_name=self.pf_expr_usr.get_secret_value(), password=self.pf_expr_pwd.get_secret_value()
        )

    @_p.field_validator('ship_live', mode='after')
    def check_setting_scope(cls, v):
        if v:
            logger.warning('Creating Shipper with Live Creds')
        else:
            logger.warning('Creating Shipper with Sandbox Creds')
        return v

    @_p.model_validator(mode='after')
    def home_address_validator(self):
        if self.home_address is None:
            self.home_address = pf_models.AddressCollection(
                address_line1=self.home_address_line1,
                address_line2=self.home_address_line2,
                address_line3=self.home_address_line3,
                town=self.home_town,
                postcode=self.home_postcode,
                country=self.home_country,
            )
        return self

    @_p.model_validator(mode='after')
    def home_contact_validator(self):
        if self.home_contact is None:
            self.home_contact = pf_top.Contact(
                business_name=self.home_business_name,
                contact_name=self.home_contact_name,
                email_address=self.home_email,
                mobile_phone=self.home_mobile_phone,
                notifications=pf_lists.RecipientNotifications(
                    notification_type=[
                        pf_shared.NotificationType.DELIVERY,
                        pf_shared.NotificationType.EMAIL,
                    ]
                ),
            )
        return self


class PFSandboxSettings(PFSettings):
    @_p.field_validator('ship_live', mode='after')
    def ship_live_validator(cls, v, values):
        if v:
            raise ValueError('ship_live must be False for sandbox')
        return v

    @_p.field_validator('pf_endpoint', mode='after')
    def pf_endpoint_validator(cls, v, values):
        if v != 'https://expresslink-test.parcelforce.net/ws/':
            raise ValueError('pf_endpoint must be https://expresslink-test.parcelforce.net/ws/')
        return v


@functools.lru_cache(maxsize=1)
def pf_sandbox_sett():
    return PFSandboxSettings()


@functools.lru_cache
def pf_sett() -> PFSettings:
    logger.info(f'SHIP_ENV is {SHIP_ENV}')
    return PFSettings()
