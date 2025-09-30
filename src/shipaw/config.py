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
from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection


def load_env_index(envs_index: Path) -> None:
    load_dotenv(envs_index)


# def load_envs() -> Path:
#     shipaw_envs = Path(os.getenv('SHIPAW_ENVS'))
#     if not shipaw_envs or not shipaw_envs.exists():
#         raise ValueError('SHIPAW_ENVS not set')
#
#     apc = shipaw_envs / 'apc.env'
#     pf = shipaw_envs / 'parcelforce.env'
#     shipaw_env = shipaw_envs / 'shipaw.env'
#
#     for f in (apc, pf, shipaw_env):
#         if not f.exists():
#             raise ValueError(f'Env file {f} does not exist')
#
#     os.environ['APC_ENV'] = str(apc)
#     os.environ['PARCELFORCE_ENV'] = str(pf)
#     os.environ['SHIPAW_ENV'] = str(shipaw_env)
#     return shipaw_env


#
def load_env():
    ei = Path(os.environ.get('ENV_INDEX'))
    load_env_index(ei)
    shipaw_env = os.getenv('SHIPAW_ENV')
    shipaw_env = Path(shipaw_env) if shipaw_env else None
    if not shipaw_env or not shipaw_env.exists():
        raise ValueError('SHIPAW_ENV not set')
    logger.debug(f'Loading SHIPAW environment from {shipaw_env}')
    return shipaw_env


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


class ShipawSettings(BaseSettings):
    # toggles
    shipper_live: bool = False
    log_level: str = 'DEBUG'

    # dirs
    label_dir: Path
    log_dir: Path
    ui_dir: Path = files('shipaw').joinpath('ui')

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

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=load_env())

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


@functools.lru_cache
def shipaw_settings() -> ShipawSettings:
    return ShipawSettings.model_validate({})

