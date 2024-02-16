from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from typing import NamedTuple, Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy


class PFExpressApiEndpoint(StrEnum):
    TEST = 'https://expresslink-test.parcelforce.net/ws/'


class PFFunc(StrEnum):
    FIND = 'Find'


class PFDicts:
    @classmethod
    def _postcode_only(cls, postcode):
        return dict(Postcode=postcode)

    @classmethod
    def paf(cls, postcode):
        return dict(PAF=cls._postcode_only(postcode))


class PFBinding(StrEnum):
    SHIP = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'


class PFEndPointSpec(NamedTuple):
    function: PFFunc
    binding: PFBinding
    api_address: PFExpressApiEndpoint


class PFAuth(NamedTuple):
    user: str
    pwd: str

    def get_auth(self):
        return dict(
            UserName=self.user,
            Password=self.pwd
        )


FIND = PFEndPointSpec(
    function=PFFunc.FIND,
    binding=PFBinding.SHIP,
    api_address=PFExpressApiEndpoint.TEST
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
        self.client = Client(wsdl=config.wsdl, settings=config.settings, transport=config.transport)

    @lru_cache
    def get_service(self, endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.client.create_service(
            binding_name=endpoint.binding,
            address=endpoint.api_address
        )

    @lru_cache
    def find_service(self) -> ServiceProxy:
        spec = FIND
        return self.get_service(spec)

    def find2(self):
        find_serv = getattr(self.client.service, 'Find')
        return find_serv

    def go_find(self, postcode):
        find_serv = self.find_service()
        resp = getattr(find_serv, 'Find')(
            Authentication=self.config.auth.get_auth(),
            PAF={'Postcode': postcode}
        )
        return resp

    def get_response(self, service, spec: PFEndPointSpec, indict: dict):
        resp = getattr(service, spec.function)(Authentication=self.config.auth, **indict)

    def addresses_from_postcode(self, postcode):
        indict = {
            "Postcode": postcode
        }
        endpoint = FIND
        service = self.get_service(endpoint)
        response = self.get_response(service=service, binding_name='PAF', indict=indict)
        return response
