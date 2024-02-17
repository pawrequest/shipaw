from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple, Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy

from .expresslink_specs import PFFunc, PFEndPointSpec


class PFAuth(NamedTuple):
    user: str
    pwd: str

    def get_auth(self):
        return dict(
            UserName=self.user,
            Password=self.pwd
        )


@dataclass
class PFConfig:
    wsdl: str
    auth: PFAuth
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
        return self.config.auth.get_auth()

    @property
    def client(self):
        return self.config.client

    @lru_cache
    def get_service(self, endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.config.client.create_service(
            binding_name=endpoint.binding,
            address=endpoint.api_address
        )

    def get_response(self, pf_func: PFFunc, data):
        data_dict = pf_func.get_pf_dict(data)
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(
            Authentication=self.auth,
            **data_dict
        )
        return resp
