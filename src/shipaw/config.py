from __future__ import annotations
from importlib.resources import files

import functools
import os
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import pydantic as _p
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.base import ShipawBaseModel
from shipaw.models.ship_types import ShipDirection


# def get_env2(env_name: str = 'SHIPAW_ENV') -> Path:
#     env = os.getenv(env_name)
#     if not env:
#         env_index = os.getenv('ENV_INDEX')
#         if env_index:
#             env_index_path = Path(env_index)
#             if env_index_path.exists():
#                 load_dotenv(env_index_path)
#                 env = os.getenv(env_name)
#                 if not env:
#                     raise ValueError(f'Environment variable {env_name} not set in {env_index_path}')
#             else:
#                 raise ValueError(f'ENV_INDEX ({env_index}) does not exist')
#         else:
#             raise ValueError(f'Environment variable {env_name} not set and ENV_INDEX not set')
#
#     env_path = Path(env)
#     if not env_path.exists():
#         raise ValueError(f'{env_path} not a valid path')
#     logger.debug(f'Loading environment from {env_path}')
#     return env_path

#
# def load_env_index(envs_index_key='SHIPAW_ENV_INDEX') -> None:
#     ei = os.environ.get(envs_index_key)
#     if not ei:
#         raise RuntimeError(f'Environment variable {envs_index_key} not set')
#     envs_index = Path(ei)
#     if not envs_index.exists():
#         raise FileNotFoundError(f'Environment index file {envs_index} does not exist')
#     logger.info(f'Loading env index from {envs_index}')
#     load_dotenv(envs_index)
#     for env in ('APC_ENV', 'PARCELFORCE_ENV', 'SHIPAW_ENV'):
#         if not os.getenv(env):
#             raise ValueError(f'Environment variable {env} not set in {envs_index}')
#         if not Path(os.getenv(env)).exists():
#             raise ValueError(f'Environment variable {env} points to non-existent file {os.getenv(env)}')
#

#
# def load_env() -> Path:
#     ei = Path(os.environ.get('SHIPAW_ENV_INDEX'))
#     logger.info(f'Loading env index from {ei}')
#     if not ei or not ei.exists():
#         raise ValueError(f'ENV_INDEX ({ei}) not set or does not exist')
#     load_env_index(ei)
#     shipaw_env = Path(os.getenv('SHIPAW_ENV'))
#     logger.debug(f'Loading SHIPAW environment from {shipaw_env}')
#     return shipaw_env


def get_shipaw_env(env_key:str = 'SHIPAW_ENV') -> Path:
    env = os.getenv(env_key)
    if not env:
        raise ValueError('SHIPAW_ENV not set')
    env_path = Path(env)
    if not env_path.exists():
        raise FileNotFoundError(f'SHIPAW_ENV file {env_path} does not exist')
    return env_path


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


def get_ui() -> Path:
    res = Path(files('shipaw'))
    res = res / 'ui'
    if not res.exists():
        raise FileNotFoundError(f'UI directory {res} does not exist')
    return res


class ProviderEnv(ShipawBaseModel):
    name: str
    env_file: Path


class ShipawSettings(BaseSettings):
    # toggles
    shipper_live: bool = False
    log_level: str = 'DEBUG'

    provider_dict: dict

    # dirs
    label_dir: Path
    log_dir: Path
    ui_dir: Path = Field(default_factory=get_ui)

    # auto dirs
    static_dir: Path | None = None
    template_dir: Path | None = None
    templates: Jinja2Templates | None = None

    # sender details
    address_line1: str
    address_line2: str | None = None
    address_line3: str | None = None
    town: str
    postcode: str
    country: str = 'GB'
    business_name: str
    contact_name: str
    email: str
    phone: str | None = None
    mobile_phone: str

    model_config = SettingsConfigDict()

    ## SET UI/TEMPLATE DIRS ##
    @model_validator(mode='after')
    def set_ui(self):
        self.static_dir = self.static_dir or self.ui_dir / 'static'
        self.template_dir = self.template_dir or self.ui_dir / 'templates'
        self.templates = self.templates or Jinja2Templates(directory=self.template_dir)
        self.templates.env.filters['jsonable'] = jsonable_encoder
        self.templates.env.filters['urlencode'] = lambda value: quote(str(value))
        self.templates.env.filters['sanitise_id'] = sanitise_id
        self.templates.env.filters['ordinal_dt'] = ordinal_dt
        return self

    ## SET LOGGING & LABELS ##
    @computed_field
    @property
    def log_file(self) -> Path:
        return self.log_dir / 'shipaw.log'

    @computed_field
    @property
    def ndjson_log_file(self) -> Path:
        return self.log_dir / 'shipaw.ndjson'

    @_p.model_validator(mode='after')
    def create_log_files(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        for v in (self.log_file, self.ndjson_log_file):
            v.touch()
        return self

    @_p.field_validator('label_dir', mode='after')
    def create_label_dirs(cls, v, values):
        directions = [_ for _ in ShipDirection]
        for subdir in directions:
            apath = v / subdir
            if not apath.exists():
                apath.mkdir(parents=True, exist_ok=True)
        return v

    ## SET ADDRESS/CONTACT OBJECTS FROM ENV VARS ##
    @property
    def contact(self):
        return Contact(
            contact_name=self.contact_name,
            email_address=self.email,
            mobile_phone=self.mobile_phone,
        )

    @property
    def address(self):
        return Address(
            address_lines=[_ for _ in [self.address_line1, self.address_line2, self.address_line3] if _],
            town=self.town,
            postcode=self.postcode,
            country=self.country,
            business_name=self.business_name,
        )

    @property
    def full_contact(self) -> FullContact:
        return FullContact(
            address=self.address,
            contact=self.contact,
        )

    @classmethod
    @functools.lru_cache
    def from_env(cls, env_key='SHIPAW_ENV') -> ShipawSettings:
        return cls(_env_file=get_shipaw_env(env_key))


# SHIPAW_SETTINGS = ShipawSettings(_env_file=get_shipaw_env())
@functools.lru_cache
def shipaw_settings() -> ShipawSettings:
    return ShipawSettings.from_env()

