from dataclasses import dataclass

from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from pydantic import BaseModel
from zeep import Client
from zeep.proxy import ServiceProxy

from .models.express.expresslink_pydantic import Authentication


class ZeepConfig(BaseModel):
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
    _service: ServiceProxy = None

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
            _service=service
        )

    @property
    def service(self) -> ServiceProxy:
        if self._service is None:
            self._service = self.new_service()
        return self._service

    def new_service(self) -> ServiceProxy:
        serv = self.client.create_service(
            binding_name=self.config.binding,
            address=self.config.endpoint
        )
        return serv


@dataclass
class PFCom2:
    config: ZeepConfig
    service: ServiceProxy

    @classmethod
    def from_config(cls, config: ZeepConfig):
        client = Client(wsdl=config.wsdl)
        service = client.create_service(config.binding, config.endpoint)
        return cls(
            config=config,
            service=service
        )

    def new_service(self) -> ServiceProxy:
        client = Client(wsdl=self.config.wsdl)
        serv = client.create_service(
            binding_name=self.config.binding,
            address=self.config.endpoint
        )
        return serv

    def backend(self, service_prot: type[ServiceProtocolT]) -> ServiceProxy:
        return ZeepBackend(self.service)[service_prot]
