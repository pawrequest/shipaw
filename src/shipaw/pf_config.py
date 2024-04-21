from __future__ import annotations

import functools
import os
from pathlib import Path

import pydantic as _p
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from shipaw.models import pf_ext, pf_shared, pf_top

SHIP_ENV = os.getenv("SHIP_ENV")


class PFSettings(BaseSettings):
    """Load Parcelforce ExpressLink configuration from environment variables.

    location of environment file is set by the environment variable SHIP_ENV.
    """

    pf_ac_num_1: str
    pf_contract_num_1: str
    pf_ac_num_2: str | None
    pf_contract_num_2: str | None

    ship_live: bool = False
    pf_expr_usr: str
    pf_expr_pwd: str

    pf_wsdl: str
    pf_binding: str = "{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding"
    pf_endpoint: str

    label_dir: Path

    home_address_line1: str
    home_address_line2: str | None = None
    home_address_line3: str | None = None
    home_town: str
    home_postcode: str
    home_country: str = "GB"

    home_contact_name: str
    home_email: str
    home_phone: str | None = None
    home_mobile_phone: str
    home_business_name: str

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=SHIP_ENV)

    @property
    def home_address(self):
        return pf_ext.AddressCollection(
            address_line1=self.home_address_line1,
            address_line2=self.home_address_line2,
            address_line3=self.home_address_line3,
            town=self.home_town,
            postcode=self.home_postcode,
            country=self.home_country,
        )

    @property
    def home_contact(self):
        return pf_top.Contact(
            contact_name=self.home_contact_name,
            email_address=self.home_email,
            mobile_phone=self.home_mobile_phone,
            business_name=self.home_business_name,
            telephone=self.home_phone,
        )

    @property
    def auth(self):
        return pf_shared.Authentication(user_name=self.pf_expr_usr, password=self.pf_expr_pwd)

    @_p.field_validator("ship_live", mode="after")
    def check_setting_scope(cls, v):
        if v:
            logger.warning("Creating Shipper with Live Creds")
        else:
            logger.info("Creating Shipper with Sandbox Creds")
        return v


class PFSandboxSettings(PFSettings):
    @_p.field_validator("ship_live", mode="after")
    def ship_live_validator(cls, v, values):
        if v:
            raise ValueError("ship_live must be False for sandbox")
        return v

    @_p.field_validator("pf_endpoint", mode="after")
    def pf_endpoint_validator(cls, v, values):
        if v != "https://expresslink-test.parcelforce.net/ws/":
            raise ValueError("pf_endpoint must be https://expresslink-test.parcelforce.net/ws/")
        return v


logger.info(f"SHIP_ENV is {SHIP_ENV}")
PF_SETTINGS = PFSettings()


@functools.lru_cache(maxsize=1)
def sandbox_settings():
    return PFSandboxSettings()
