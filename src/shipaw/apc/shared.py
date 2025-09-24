import os
from datetime import date, time
from enum import StrEnum

from pydantic import ConfigDict

from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.requests import Authentication, encode_b64_str
from shipaw.apc.config import apc_settings


class APCBaseModel(ShipawBaseModel):
    model_config = ConfigDict(
        json_encoders={
            time: lambda v: v.strftime('%H:%M'),
            date: lambda v: v.strftime('%d/%m/%Y'),
        },
    )


class EndPoints(StrEnum):
    BASE = r'https://apc-training.hypaship.com/api/3.0/'
    SERVICES = BASE + 'ServiceAvailability.json'
    ORDERS = BASE + 'Orders.json'


def order_endpoint(order_num: str):
    return EndPoints.BASE + f'Orders/{order_num}.json'


def get_remote_user(login, password) -> str:
    usr_str = f'{login}:{password}'
    return f'Basic {encode_b64_str(usr_str)}'


def get_headers() -> dict:
    sett = apc_settings()
    usr = sett.apc_email.get_secret_value()
    pwd = sett.apc_password.get_secret_value()
    return {'Content-Type': 'application/json', 'remote-user': get_remote_user(usr, pwd)}


def apc_date(d: date) -> str:
    return d.strftime('%d/%m/%Y')
