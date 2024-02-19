import os
from dataclasses import dataclass
from typing import Optional, Protocol, Annotated

import pytest
from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name
from dotenv import load_dotenv
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from combadge.support.zeep.backends.sync import ZeepBackend
from zeep import Client
from zeep.proxy import ServiceProxy


ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)

WSDL = os.environ.get('PF_WSDL')


class BasePFType(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
    )


class Authentication(BasePFType):
    user_name: str = Field(...)
    password: str = Field(...)


class PAF(BasePFType):
    postcode: Optional[str] = Field(None)


@dataclass
class ZeepConfig:
    auth: Authentication
    binding: str
    wsdl: str
    endpoint: str


def get_service(client, binding, endpoint) -> ServiceProxy:
    return client.create_service(
        binding_name=binding,
        address=endpoint
    )


@dataclass
class PFCom:
    config: ZeepConfig
    client: Client
    service: ServiceProxy = None

    @classmethod
    def from_config(cls, config: ZeepConfig):
        client = Client(wsdl=config.wsdl)
        service = get_service(
            client,
            config.binding,
            config.endpoint
        )
        return cls(
            config=config,
            client=client,
            service=service
        )

    def get_service(self) -> ServiceProxy:
        serv = self.client.create_service(
            binding_name=self.config.binding,
            address=self.config.endpoint
        )
        return serv


class FindRequest(BasePFType):
    authentication: Authentication = Field(None)
    paf: Optional[PAF] = Field(None, alias='PAF')


class FindResponse(BasePFType):
    paf: dict = Field(None, alias='PAF')


class FindService(SupportsService, Protocol):
    @operation_name("Find")
    def find(
            self,
            request: Annotated[FindRequest, Payload(by_alias=True)],
    ) -> FindResponse:
        ...


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')

    auth = Authentication(user_name=username, password=password)
    return auth


@pytest.fixture
def zconfig(pf_auth):
    wsdl = os.environ.get('PF_WSDL')
    binding = os.environ.get('PF_BINDING')
    ep = os.environ.get('PF_ENDPOINT_SAND')
    return ZeepConfig(
        binding=binding,
        wsdl=wsdl,
        auth=pf_auth,
        endpoint=ep
    )


def test_go(zconfig):
    pfc = PFCom.from_config(zconfig)
    service = ZeepBackend(pfc.service)[FindService]

    paf = PAF(postcode='NW6 4TE')
    req = FindRequest(authentication=zconfig.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
