from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple, Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object

from .expresslink_specs import PFEndPointSpec, PFFunc, PFFunc2
from .models.express.expresslink_pydantic import Authentication


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


class PFConnector:
    def __init__(self, config: PFConfig):
        self.config = config
        self.service = self.get_service(PFEndPointSpec.sandbox())

    @property
    def auth(self) -> Authentication:
        return self.config.auth.get_auth2()

    @property
    def client(self):
        return self.config.client

    @lru_cache
    def get_service(self, endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.config.client.create_service(
            binding_name=endpoint.binding,
            address=endpoint.api_address
        )


class PFExpressLink(PFConnector):
    def get_response(self, pf_func: PFFunc, data):
        data_dict = pf_func.get_pf_dict(data)
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(
            Authentication=self.auth,
            **data_dict
        )
        return resp

    def get_response2(self, pf_func: PFFunc2, data):
        data_dict = pf_func.get_pf_dict(data)
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(
            Authentication=self.auth,
            **data_dict
        )
        return resp

    def get_response3(self, pf_func: PFFunc, data) -> dict:
        request = pf_func.request_type(**data)
        data_dict = serialize_object(request, target_cls=dict)
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(
            Authentication=self.auth,
            **data_dict
        )
        return resp

    def process_request(self, request) -> dict:
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(**request)
        return resp
