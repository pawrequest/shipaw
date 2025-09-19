import base64
from typing import Annotated

from pydantic import SecretStr, StringConstraints

from shipaw.agnostic.base import ShipawBaseModel


class Authentication(ShipawBaseModel):
    # todo SecretStr!!!!
    user_name: Annotated[str, StringConstraints(max_length=80)]
    password: Annotated[str, StringConstraints(max_length=80)]


class BaseRequest(ShipawBaseModel):
    authentication: Authentication


def encode_b64_str(s: str) -> str:
    return base64.b64encode(s.encode('utf8')).decode('utf8')
    # bytes_64 = s.encode('utf8')
    # return base64.b64encode(bytes_64).decode('utf8')
