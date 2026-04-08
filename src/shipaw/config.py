from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import BaseModel, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

from shipaw.fapi.ui_funcs import get_ui, ordinal_dt, sanitise_id
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER, register_provider_instance
from shipaw.utils.consts_enums import ShipDirection

SHIPAW_ENV_KEY = 'SHIPAW_ENV'


def path_from_env_key(env_key: str) -> Path:
    env = os.getenv(env_key)
    if not env:
        raise ValueError(f'{env_key} not set')
    env_path = Path(env)
    if not env_path.exists():
        raise FileNotFoundError(f'{env_key} file {env_path} does not exist')
    return env_path


@dataclass
class ProviderEnv:
    name: str
    env_path: Path


ProviderEnvs = list[ProviderEnv]


@functools.cache
def get_templates_cached(template_dir: Path):
    temps = Jinja2Templates(directory=str(template_dir))
    temps.env.filters['jsonable'] = jsonable_encoder
    temps.env.filters['urlencode'] = lambda value: quote(str(value))
    temps.env.filters['sanitise_id'] = sanitise_id
    temps.env.filters['ordinal_dt'] = ordinal_dt
    return temps


class ShipawSettings(BaseSettings):
    # toggles
    shipper_live: bool = True
    log_level: str = 'DEBUG'

    # dirs
    data_dir: Path = Path.home() / 'shipaw'
    label_dir: Path = Path.home() / 'shipaw' / 'labels'
    log_db_path: str | None = None
    ui_dir: Path = Field(default_factory=get_ui)

    # Provider env file dict (json string in .env)
    provider_env_dict: dict[str, Path]
    default_provider_name: str | None = None

    # auto dirs
    # templates: Jinja2Templates | None = None

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

    model_config = SettingsConfigDict(frozen=True)

    @classmethod
    @functools.cache
    def from_env(cls) -> ShipawSettings:
        logger.info(f'Loading ShipawSettings from env key: {SHIPAW_ENV_KEY}')
        env_path = path_from_env_key(SHIPAW_ENV_KEY)
        return cls(_env_file=env_path)  # pycharm_pydantic false positive

    #
    # @model_validator(mode='after')
    # def populate_provider_registry(self):
    #     logger.debug('Populating provider registry with providers from env')
    #     for name, env_path in self.provider_env_dict.items():
    #         logger.debug(f'Loading provider {name} from env file {env_path}')
    #         if provider_type := PROVIDER_TYPE_REGISTER.get(name):
    #             logger.debug(f'Found provider type {provider_type} for name {name}')
    #             provider_settings = provider_type.settings_type(_env_file=env_path)
    #             provider = provider_type(shipaw_settings=provider_settings)
    #             register_provider_instance(provider)
    #     return self

    @property
    def log_dir(self):
        return self.data_dir / 'logs'

    @property
    def template_dir(self):
        return self.ui_dir / 'templates'

    @property
    def static_dir(self):
        return self.ui_dir / 'static'

    @property
    def templates(self):
        return get_templates_cached(self.template_dir)

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
        # todo bad path crashes progqram - try/except + fallback label path?
        directions = [_ for _ in ShipDirection]
        try:
            make_label_dirs(directions, v)
        except FileNotFoundError:
            v = Path.home() / 'Shipping Labels'
            make_label_dirs(directions, v)
        return v

    # SET ADDRESS/CONTACT OBJECTS #
    @property
    def contact(self):
        return Contact(
            name=self.contact_name,
            email=self.email,
            phone=self.mobile_phone,
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


def make_label_dirs(directions, v):
    for direction in directions:
        apath = v / direction
        if not apath.exists():
            apath.mkdir(parents=True, exist_ok=True)


SHIPAW_SETTINGS = ShipawSettings.from_env()


def populate_providers(settings: ShipawSettings):
    settings = settings
    for name, env_path in settings.provider_env_dict.items():
        if provider_type := PROVIDER_TYPE_REGISTER.get(name):
            provider_settings = provider_type.settings_type(_env_file=env_path)
            register_provider_instance(provider_type(settings=provider_settings))


class FapiConfig(BaseModel):
    port: int = 8000
    post_body: dict = {}
    url_for_: str = ''
    context: dict = Field(default_factory=dict)
