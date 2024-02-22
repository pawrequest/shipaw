import os
from dataclasses import dataclass

from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from pydantic import BaseModel
from zeep import Client
from zeep.proxy import ServiceProxy

from .models.express.expresslink_types import Authentication


class ZeepConfig(BaseModel):
    auth: Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def from_env(cls):
        return cls(
            auth=Authentication.from_env(),
            binding=os.environ.get('PF_BINDING'),
            wsdl=os.environ.get('PF_WSDL'),
            endpoint=os.environ.get('PF_ENDPOINT_SAND')
        )


def get_service(client, binding, endpoint) -> ServiceProxy:
    return client.create_service(
        binding_name=binding,
        address=endpoint
    )


@dataclass
class PFCom:
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

    @classmethod
    def from_env(cls):
        return cls.from_config(ZeepConfig.from_env())

    def new_service(self) -> ServiceProxy:
        client = Client(wsdl=self.config.wsdl)
        serv = client.create_service(
            binding_name=self.config.binding,
            address=self.config.endpoint
        )
        return serv

    def backend(self, service_prot: type[ServiceProtocolT]) -> ServiceProxy:
        return ZeepBackend(self.service)[service_prot]

    def get_response(
            self,
            *items,
            service_prot: type[ServiceProtocolT],
            request: BaseModel
    ) -> BaseModel:
        backend = self.backend(service_prot)
        return backend(*items, request=request)

