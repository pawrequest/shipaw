from __future__ import annotations

import os
from pathlib import Path

from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from pydantic import BaseModel, ConfigDict
from thefuzz import fuzz, process
from zeep import Client
from zeep.proxy import ServiceProxy

from shipr.models import pf_types as elt, pf_msg as msg, service_protocols as cp


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

    def get_shipment_resp(self, req: el.msg.CreateShipmentRequest) -> el.msg.CreateShipmentResponse:
        back = self.backend(cp.CreateShipmentService)
        resp = back.createshipment(request=req.model_dump(by_alias=True))
        return msg.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[elt.AddressPF]:
        req = msg.FindRequest(
            authentication=self.config.auth,
            paf=elt.PAF(postcode=postcode)
        )
        back = self.backend(cp.FindService)
        response = back.find(request=req.model_dump(by_alias=True))
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
            pf_auth: elt.Authentication - PFCom authentication
            ship_num: str - shipment number
        """
        back = self.backend(cp.PrintLabelService)
        req = msg.PrintLabelRequest(authentication=self.config.auth, shipment_number=ship_num)
        response: msg.PrintLabelResponse = back.printlabel(request=req)
        outpath = response.label.download()
        os.startfile(outpath)
        return outpath

    def choose_one_str(self, address_str: str, candidates: list) -> tuple[
        elt.AddressPF, int]:
        address, score = process.extractOne(address_str, candidates, scorer=fuzz.token_sort_ratio)
        return address, score

    def guess_address(self, address: elt.AddressPF) -> elt.AddressChoice:
        candidates_dict = {address_as_str(add): add for add in
                           self.get_candidates(address.postcode)}
        chosen, score = process.extractOne(
            address_as_str(address),
            list(candidates_dict.keys()),
            scorer=fuzz.token_sort_ratio
        )
        add = candidates_dict[chosen]
        return elt.AddressChoice(address=add, score=score)


def address_as_str(pf_address: elt.AddressPF) -> str:
    lines = [pf_address.address_line1, pf_address.address_line2, pf_address.address_line3]
    ls = ' '.join(line for line in lines if line)

    return ls
