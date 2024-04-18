from __future__ import annotations

import os

import pydantic as _p
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=os.getenv('SHIP_ENV'))


class PFSandboxSettings(PFSettings):
    ship_live: bool = False

    @_p.field_validator('ship_live', mode='after')
    def ship_live_validator(cls, v, values):
        return False

    @_p.field_validator('pf_endpoint', mode='after')
    def pf_endpoint_validator(cls, v, values):
        return 'https://expresslink-test.parcelforce.net/ws/'


PF_SETTINGS = PFSettings()
PF_SANDBOX_SETTINGS = PFSandboxSettings()
logger.info(f'SHIP_LIVE is {PF_SETTINGS.ship_live}')
logger.info(f'PF_ENDPOINT is {PF_SETTINGS.pf_endpoint}')
if 'test' not in PF_SETTINGS.pf_endpoint:
    logger.warning('USING PROD ENDPOINT')
