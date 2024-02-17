from dataclasses import dataclass
from typing import NamedTuple, Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy

from .expresslink_specs2 import PFEndPointSpec, PFFunc


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
    pf_endpoint: PFEndPointSpec
    settings: Optional[Settings] = None
    transport: Optional[Transport] = None
    client: Optional[Client] = None
    service: Optional[ServiceProxy] = None

    def __post_init__(self):
        self.settings = self.settings or Settings()
        self.transport = self.transport or Transport(timeout=10)
        self.client = self.client or Client(
            wsdl=self.wsdl,
            settings=self.settings,
            transport=self.transport
        )
        # self.service = self.service or self.get_service(self.pf_endpoint)

    def get_service(self, pf_endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.client.create_service(
            binding_name=pf_endpoint.binding.value,
            address=pf_endpoint.url.value
        )


def get_pf_dict(pf_func: PFFunc, data):
    if pf_func == PFFunc.FIND:
        return dict(PAF={'Postcode': data})
    else:
        raise ValueError(f'Unknown function: {pf_func}')


class PFExpressLink:
    def __init__(self, config: PFConfig):
        self.config = config

    def _func(self, pf_func: PFFunc):
        soap_func = getattr(self.config.client.service, pf_func.value)
        return soap_func

    def get_response(self, pf_func: PFFunc, data):
        fnc = self._func(pf_func)
        indict = get_pf_dict(pf_func, data=data)
        resp = fnc(Authentication=self.config.auth.get_auth(), **indict)
        return resp

    def addresses_from_postcode(self, postcode):
        pf_func = PFFunc.FIND
        return self.get_response(pf_func, postcode)
