from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object

from .expresslink_specs import PFEndPointSpec
from .models.express.msg import PFFunc
from .models.bases import BaseResponse, BaseRequest, alias_dict


@dataclass
class PFConfig:
    wsdl: str
    auth: Authentication
    settings: Optional[Settings] = None
    transport: Optional[Transport] = None
    client: Optional[Client] = None

    def __post_init__(self):
        self.settings = self.settings or Settings()
        self.transport = self.transport or Transport(timeout=10)
        self.client = self.client or Client(
            wsdl=self.wsdl,
            settings=self.settings,
            transport=self.transport
        )


class PFExpressLink:
    def __init__(self, config: PFConfig):
        self.config = config
        self.service = self.get_service(PFEndPointSpec.sandbox())

    @property
    def auth(self):
        return self.config.auth

    @property
    def client(self):
        return self.config.client

    @lru_cache
    def get_service(self, endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.config.client.create_service(
            binding_name=endpoint.binding,
            address=endpoint.api_address
        )

    def get_response(self, request: BaseRequest, pf_func: PFFunc) -> BaseResponse:
        fnc = getattr(self.service, pf_func.name)
        if not request.authorised:
            request.authorise(self.auth)
        resp = fnc(**request.model_dump(by_alias=True, exclude_none=True))
        return resp

    def process_response(self, resp: BaseResponse, pf_func: PFFunc) -> BaseResponse:
        ser = serialize_object(resp)
        res = FindResponse(**ser)
        ret = pf_func.response_type.model_validate(res)
        ret2 = pf_func.response_type.model_validate(ser)

        return ret

