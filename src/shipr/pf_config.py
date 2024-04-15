import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class PFSettings(BaseSettings):
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


pf_settings = PFSettings()
