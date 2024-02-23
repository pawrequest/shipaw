from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from pydantic import BaseModel, ConfigDict
from thefuzz import fuzz, process
from zeep import Client
from zeep.proxy import ServiceProxy

from shipr import types as elt
from shipr.models import combadge_protocols as cp
from shipr import msg


class ZeepConfig(BaseModel):
    auth: elt.Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def from_env(cls):
        return cls(
            auth=elt.Authentication.from_env(),
            binding=os.environ.get('PF_BINDING'),
            wsdl=os.environ.get('PF_WSDL'),
            endpoint=os.environ.get('PF_ENDPOINT_SAND')
        )


def get_service(client, binding, endpoint) -> ServiceProxy:
    return client.create_service(
        binding_name=binding,
        address=endpoint
    )


class PFCom(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
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

    # def get_candidates2(self, postcode: str) -> AddressCandidates:
    #     back = self.backend(cp.FindService)
    #     req = el.msg.FindRequest(
    #         authentication=self.config.auth,
    #         paf=el.types.PAF(postcode=postcode)
    #     )
    #     response = back.find(request=req)
    #     addresses = [neighbour.address[0] for neighbour in
    #                  response.paf.specified_neighbour] \
    #         if response.paf.specified_neighbour else []
    #     return AddressCandidates(candidates=addresses)

    def get_candidates(self, postcode: str):
        req = msg.FindRequest(
            authentication=self.config.auth,
            paf=elt.PAF(postcode=postcode)
        )
        back = self.backend(cp.FindService)
        response = back.find(request=req)
        if not response.paf.specified_neighbour:
            return []
        addresses = [
            neighbour.address[0]
            for neighbour in response.paf.specified_neighbour
        ]
        return addresses

    def get_label(self, ship_num) -> Path:
        """Get the label for a shipment number.

        args:
            pf_com2: PFCom - PFCom combadge client
            pf_auth: Authentication - PFCom authentication
            ship_num: str - shipment number
        """
        back = self.backend(cp.PrintLabelService)
        req = msg.PrintLabelRequest(authentication=self.config.auth, shipment_number=ship_num)
        response: msg.PrintLabelResponse = back.printlabel(request=req)
        outpath = response.label.download()
        os.startfile(outpath)
        return outpath

    def choose_one_str(self, address_str: str, candidates: list[str]) -> tuple[
        elt.AddressPF, int]:
        address, score = process.extractOne(address_str, candidates, scorer=fuzz.token_sort_ratio)
        return address, score
