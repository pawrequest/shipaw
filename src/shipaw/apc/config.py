import os
from functools import lru_cache
from pathlib import Path

import dotenv
from loguru import logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_env() -> Path:
    apc_env = Path(os.getenv('APC_ENV'))
    if not apc_env.exists():
        raise ValueError('APC_ENV not set correctly')
    logger.debug(f'Loading APC environment from {apc_env}')
    return apc_env


class APCSettings(BaseSettings):
    apc_email: SecretStr
    apc_password: SecretStr
    model_config = SettingsConfigDict(env_file=load_env())


@lru_cache
def apc_settings() -> APCSettings:
    return APCSettings()