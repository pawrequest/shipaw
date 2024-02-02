import base64
import json
import os
import datetime
from typing import TypeVar
from aiohttp import ClientSession
from pawsupport.convert import snake_to_pascal
from pydantic import BaseModel, model_validator

class RequestMixin:
    @staticmethod
    async def request_from_dict(url, req_dict: dict, session=None) -> dict:
        session = session or ClientSession()
        req_json = json.dumps(req_dict)

        async with session:
            async with session.post(
                    url=url,
                    headers=get_headers(),
                    data=req_json
            ) as response:
                response_txt = await response.text()
                response_json = json.loads(response_txt)
                return response_json


class RequestDictMixin:
    def request_dict(self) -> dict:
        output_name = self.__class__.__name__
        output_dict = {
            output_name: {
                attr: getattr(self, attr)
                for attr in vars(self)
            }
        }

        return output_dict


T = TypeVar('T', bound='BaseRequest')


class BaseRequest(BaseModel):
    def get_dict(self) -> dict:
        return {
            self.__class__.__name__:
                {
                    snake_to_pascal(attr): getattr(self, attr)
                    for attr in vars(self)
                }

        }

    @classmethod
    def get_json_many(cls: type(T), instances: list[T]) -> str:
        return json.dumps(cls.get_dict_many(instances))

    @classmethod
    def get_dict_many(cls: type(T), instances: list[T]) -> dict:
        return {
            f'{cls.__name__}s': [instance.get_dict() for instance in instances]
        }

    @model_validator(mode='before')
    def date_is_str(cls, v):
        for k, value in v.items():
            if isinstance(value, datetime.date):
                v[k] = value.isoformat()
        return v


def get_headers() -> dict:
    usr = os.environ.get('APC_LOGIN')
    pwd = os.environ.get('APC_PASSWORD')
    res = {
        'Content-Type': 'application/json',
        'remote-user': get_remote_user(usr, pwd)
    }
    return res


def get_remote_user(login, password) -> str:
    usr_str = f'{login}:{password}'
    usr_str_encoded = encode_b64(usr_str)
    return f'Basic {usr_str_encoded}'


def encode_b64(s: str) -> str:
    asci_str = s.encode("ascii")
    base64_b = base64.b64encode(asci_str)
    base64_s = base64_b.decode("ascii")
    return base64_s


