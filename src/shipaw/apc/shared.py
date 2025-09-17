import os
from datetime import date, time
from enum import StrEnum

from pydantic import ConfigDict

from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.requests import Authentication, encode_b64_str



class APCBaseModel(ShipawBaseModel):
    model_config = ConfigDict(
        json_encoders={
            time: lambda v: v.strftime('%H:%M'),
            date: lambda v: v.strftime('%d/%m/%Y'),
        },
    )


# class Messages(APCBaseModel):
#     Code: str
#     Description: str


class EndPoints(StrEnum):
    BASE = r'https://apc-training.hypaship.com/api/3.0/'
    SERVICES = BASE + 'ServiceAvailability.json'
    ORDERS = BASE + 'Orders.json'


def get_remote_user(login, password) -> str:
    usr_str = f'{login}:{password}'
    return f'Basic {encode_b64_str(usr_str)}'


def get_headers() -> dict:
    usr = os.environ.get('EMAIL')
    pwd = os.environ.get('PASSWORD')
    return {'Content-Type': 'application/json', 'remote-user': get_remote_user(usr, pwd)}


class APCAuthentication(Authentication):
    def auth_str(self):
        return {
            'Content-Type': 'application/json',
            'remote-user': get_remote_user(self.user_name.get_secret_value(), self.password.get_secret_value()),
        }


#
def apc_date(d: date) -> str:
    return d.strftime('%d/%m/%Y')
