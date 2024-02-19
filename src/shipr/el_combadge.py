from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy

from .expresslink_specs import PFEndPointSpec
from .models.expresslink_pydantic import Authentication


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


@dataclass
class PFCom1:
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

    @lru_cache(maxsize=1)
    def get_service(self) -> ServiceProxy:
        serv = self.client.create_service(
            binding_name=self.config.binding,
            address=self.config.endpoint
        )
        return serv


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


class PFCom2:
    def __init__(self, config: PFConfig):
        self.config = config
        self.service = self.get_service(PFEndPointSpec.sandbox())

    @property
    def auth(self):
        return self.config.auth

    @property
    def client(self):
        return self.config.client

    @lru_cache(maxsize=1)
    def get_service(self, endpoint: PFEndPointSpec) -> ServiceProxy:
        return self.config.client.create_service(
            binding_name=endpoint.binding,
            address=endpoint.api_address
        )
