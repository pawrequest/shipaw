from __future__ import annotations

import functools
import os
from pathlib import Path

import pydantic as _p
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from shipaw.agnostic.address import Address, Contact, FullContact
from shipaw.agnostic.ship_types import MyPhone, ShipDirection


def load_env():
    shipaw_env = os.getenv('SHIPAW_ENV')
    shipaw_env = Path(shipaw_env) if shipaw_env else None
    if not shipaw_env or not shipaw_env.exists():
        raise ValueError('SHIPAW_ENV not set')
    logger.debug(f'Loading SHIPAW environment from {shipaw_env}')
    return shipaw_env


class ShipawSettings(BaseSettings):
    label_dir: Path

    address_line1: str
    address_line2: str | None = None
    address_line3: str | None = None
    town: str
    postcode: str
    country: str = 'GB'
    business_name: str
    contact_name: str
    email: str
    phone: MyPhone | None = None
    mobile_phone: MyPhone

    full_contact: FullContact | None = None

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=load_env())

    @_p.field_validator('label_dir', mode='after')
    def make_path(cls, v, values):
        dirs = [_ for _ in ShipDirection]
        for subdir in dirs:
            apath = v / subdir
            if not apath.exists():
                apath.mkdir(parents=True, exist_ok=True)
        return v

    @_p.model_validator(mode='after')
    def home_full_contact_validator(self):
        if self.full_contact is None:
            self.full_contact = FullContact(
                address=Address(
                    address_lines=[
                        _
                        for _ in [
                            self.address_line1,
                            self.address_line2,
                            self.address_line3,
                        ]
                        if _
                    ],
                    town=self.town,
                    postcode=self.postcode,
                    country=self.country,
                ),
                contact=Contact(
                    business_name=self.business_name,
                    contact_name=self.contact_name,
                    email_address=self.email,
                    mobile_phone=self.mobile_phone,
                ),
            )
        return self


@functools.lru_cache
def shipaw_settings() -> ShipawSettings:
    return ShipawSettings()
