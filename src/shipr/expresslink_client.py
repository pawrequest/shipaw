from __future__ import annotations

import os
from pathlib import Path

import pydantic
import zeep
from zeep.proxy import ServiceProxy
from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from thefuzz import fuzz, process

from . import models, msgs, ship_ui
from .models import types

SCORER = fuzz.token_sort_ratio


class ZeepConfig(pydantic.BaseModel):
    auth: models.Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def from_env(cls):
        return cls(
            auth=models.Authentication.from_env(),
            binding=os.environ.get("PF_BINDING"),
            wsdl=os.environ.get("PF_WSDL"),
            endpoint=os.environ.get("PF_ENDPOINT_SAND"),
        )


class ELClient(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    config: ZeepConfig
    service: zeep.proxy.ServiceProxy

    @classmethod
    def from_config(cls, config: ZeepConfig):
        client = zeep.Client(wsdl=config.wsdl)
        service = client.create_service(config.binding, config.endpoint)
        return cls(config=config, service=service)

    @classmethod
    # @lru_cache(maxsize=1)
    def from_env(cls):
        return cls.from_config(ZeepConfig.from_env())

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(wsdl=self.config.wsdl)
        serv = client.create_service(binding_name=self.config.binding, address=self.config.endpoint)
        return serv

    def backend(self, service_prot: type[ServiceProtocolT]) -> ServiceProxy:
        return ZeepBackend(self.service)[service_prot]

    def get_shipment_resp(self, req: msgs.CreateShipmentRequest) -> msgs.CreateShipmentResponse:
        back = self.backend(msgs.CreateShipmentService)
        resp = back.createshipment(request=req.model_dump(by_alias=True))
        return msgs.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[models.AddressRecipient]:
        req = msgs.FindRequest(authentication=self.config.auth, paf=models.PAF(postcode=postcode))
        back = self.backend(msgs.FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
            return []
        return [neighbour.address[0] for neighbour in response.paf.specified_neighbour]

    def get_label(self, ship_num) -> Path:
        """Get the label for a shipment number.

        args:
            pf_com2: PFCom - PFCom combadge client
            pf_auth: elt.Authentication - PFCom authentication
            ship_num: str - shipment number
        """
        back = self.backend(msgs.PrintLabelService)
        req = msgs.PrintLabelRequest(authentication=self.config.auth, shipment_number=ship_num)
        response: msgs.PrintLabelResponse = back.printlabel(request=req)
        out_path = response.label.download(Path('temp_label.pdf'))
        return out_path

    def choose_address(
            self,
            address: models.AddressRecipient
    ) -> models.AddressRecipient | None:
        if candidates := self.candidates_dict(address.postcode):
            chosen, score = process.extractOne(
                address.lines_str,
                list(candidates.keys()),
                scorer=SCORER
            )
            add = candidates[chosen]
            return add
        else:
            raise ValueError(f"No candidates found for {address.postcode}")

    def candidates_dict(self, postcode):
        return {add.lines_str: add
                for add in self.get_candidates(postcode)}

    def state_to_shipment_request(self, state: ship_ui.ShipState):
        ship_req = booking_state_to_shipment(state)
        req = msgs.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def state_to_response(self, state: ship_ui.ShipState) -> msgs.CreateShipmentResponse:
        req = self.state_to_shipment_request(state)
        return self.get_shipment_resp(req)


def booking_state_to_shipment(state: ship_ui.ShipState) -> models.RequestedShipmentMinimum:
    # add = elt.AddressRecipientPF.model_validate(state.address)
    return models.RequestedShipmentMinimum(
        department_id=types.DepartmentNum,
        shipment_type='DELIVERY',
        contract_number=os.environ["PF_CONT_NUM_1"],
        service_code=state.ship_service,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=state.address,
        total_number_of_parcels=state.boxes,
    )
