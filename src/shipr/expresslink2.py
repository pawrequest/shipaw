from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from zeep import Client, Settings, Transport
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object
from .expresslink_specs import PFEndPointSpec, PFFunc2
from .models.messages import PFFunc3
from .models.remixed import Authentication, BasePFType, FindRequest, BaseResponse


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

    def get_response2(self, pf_func: PFFunc2, data):
        data_dict = pf_func.get_pf_dict(data)
        fnc = getattr(self.service, pf_func.name)
        resp = fnc(
            Authentication=self.auth,
            **data_dict
        )
        return resp

    # def process_request(self, pf_func: PFFunc2, data) -> dict:
    #     request = pf_func.request_type(**data)
    #     data_dict = serialize_object(request, target_cls=dict)
    #     fnc = getattr(self.service, pf_func.name)
    #     resp = fnc(
    #         Authentication=self.auth,
    #         **data_dict
    #     )
    #     return resp

    def process_request(self, request, pf_func:PFFunc3) -> BaseResponse:
        fnc = getattr(self.service, pf_func.name)
        data_dict = request.model_dump(by_alias=True)
        resp = fnc(**data_dict)
        ser = serialize_object(resp, target_cls=dict)
        return pf_func.response_type.model_validate(ser)

    def get_ath_request(self, pf_func: PFFunc3, *data: BasePFType):
        res = pf_func.get_auth_request(self.auth, *data)
        return res


