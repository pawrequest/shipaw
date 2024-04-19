from __future__ import annotations

import functools
import os
from pathlib import Path

import pydantic as _p
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from shipaw.models import pf_shared

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

    ship_live: bool = False
    pf_expr_usr: str
    pf_expr_pwd: str

    pf_wsdl: str
    pf_binding: str = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'
    pf_endpoint: str

    label_dir: Path

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=SHIP_ENV)

    @property
    def auth(self):
        return pf_shared.Authentication(user_name=self.pf_expr_usr, password=self.pf_expr_pwd)

    @_p.field_validator('ship_live', mode='after')
    def check_setting_scope(cls, v):
        if v:
            logger.warning('Creating Shipper with Live Creds')
        else:
            logger.info('Creating Shipper with Sandbox Creds')
        return v


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


logger.info(f'SHIP_ENV is {SHIP_ENV}')
PF_SETTINGS = PFSettings()


@functools.lru_cache(maxsize=1)
def sandbox_settings():
    return PFSandboxSettings()


@functools.lru_cache(maxsize=1)
def prod_settings():
    return PFSettings()
