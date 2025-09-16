import base64
import os
from datetime import date, time
from enum import StrEnum

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal

APC_ENV = r'C:\prdev\repos\amdev\shipaw\apc.env'


class APCBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
        json_encoders={
            time: lambda v: v.strftime('%H:%M'),
            date: lambda v: v.strftime('%d/%m/%Y'),
        },
    )


class Messages(APCBaseModel):
    Code: str
    Description: str


class EndPoints(StrEnum):
    BASE = r'https://apc-training.hypaship.com/api/3.0/'
    SERVICES = BASE + 'ServiceAvailability.json'
    ORDERS = BASE + 'Orders.json'

def encode_b64_str(s: str) -> str:
    return base64.b64encode(s.encode('utf8')).decode('utf8')
    # bytes_64 = s.encode('utf8')
    # return base64.b64encode(bytes_64).decode('utf8')


def get_remote_user(login, password) -> str:
    usr_str = f'{login}:{password}'
    return f'Basic {encode_b64_str(usr_str)}'


def get_headers() -> dict:
    usr = os.environ.get('EMAIL')
    pwd = os.environ.get('PASSWORD')
    return {'Content-Type': 'application/json', 'remote-user': get_remote_user(usr, pwd)}




#
def apc_date(d: date) -> str:
    return d.strftime('%d/%m/%Y')
