import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_royal_mail_settings_env():
    rm_env = Path(os.getenv("ROYAL_MAIL_ENV"))
    if not rm_env or not rm_env.exists():
        raise ValueError(f"ROYAL_MAIL_ENV ({rm_env}) incorrectly set")
    print(f"Loading RoyalMail Settings from {rm_env}")
    return rm_env


class Settings(BaseSettings):
    api_key: str
    base_url: str = r"https://api.parcel.royalmail.com/api/v1"

    model_config = SettingsConfigDict(env_file=load_royal_mail_settings_env())


@lru_cache
def royal_mail_settings() -> Settings:
    return Settings()