from __future__ import annotations

from pathlib import Path

import pydantic
import zeep
from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from loguru import logger
from thefuzz import fuzz, process
from zeep.proxy import ServiceProxy

from . import models, msgs, pf_config, ship_ui
from .models import pf_shared

SCORER = fuzz.token_sort_ratio


class ZeepConfig(pydantic.BaseModel):
    auth: models.Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def fetch(cls):
        sett = pf_config.PF_SETTINGS
        return cls(
            auth=models.Authentication(
                password=sett.pf_expr_pwd,
                user_name=sett.pf_expr_usr
            ),
            binding=sett.pf_binding,
            wsdl=sett.pf_wsdl,
            endpoint=str(sett.pf_endpoint)
        )


class ELClient(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    config: ZeepConfig
    service: ServiceProxy

    @classmethod
    def from_zeep_config(cls, config: ZeepConfig):
        client = zeep.Client(wsdl=config.wsdl)
        service = client.create_service(config.binding, config.endpoint)
        return cls(config=config, service=service)

    @classmethod
    def from_pyd(cls):
        settings = pf_config.PF_SETTINGS
        client = zeep.Client(wsdl=settings.pf_wsdl)
        service = client.create_service(settings.pf_binding, settings.pf_endpoint)
        return cls(
            config=ZeepConfig.fetch(),
            service=service,
        )

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(wsdl=self.config.wsdl)
        serv = client.create_service(binding_name=self.config.binding, address=self.config.endpoint)
        return serv

    def backend(self, service_prot: type[ServiceProtocolT]) -> zeep.proxy.ServiceProxy:
        """Get a Combadge backend for a service protocol.

        Args:
            service_prot: type[ServiceProtocolT] - service protocol to get backend for

        Returns:
            ServiceProxy - Zeep Proxy

        """
        return ZeepBackend(self.service)[service_prot]

    def shipment_req_to_resp(self, req: msgs.CreateShipmentRequest) -> msgs.CreateShipmentResponse:
        """Create a shipment.

        Args:
            req: .msgs.CreateShipmentRequest - ShipmenmtRequest to book

        Returns:
            .msgs.CreateShipmentResponse - response from Parcelforce

        """
        back = self.backend(msgs.CreateShipmentService)
        resp = back.createshipment(request=req.model_dump(by_alias=True))
        logger.warning(f'BOOKED {req.requested_shipment.recipient_address.lines_str}')

        return msgs.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[models.AddressRecipient]:
        """Get candidate addresses at a postcode.

        Args:
            postcode: str - postcode to search for

        Returns:
            list[.models.AddressRecipient] - list of candidate addresses

        """
        req = msgs.FindRequest(authentication=self.config.auth, paf=models.PAF(postcode=postcode))
        back = self.backend(msgs.FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
            return []
        return [neighbour.address[0] for neighbour in response.paf.specified_neighbour]

    def get_label(self, ship_num, dl_path=None) -> Path:
        """Get the label for a shipment number.

        Args:
            ship_num: str - shipment number
            dl_path: str - path to download the label to, defaults to './temp_label.pdf'

        Returns:
            Path - path to the downloaded label

        """
        dl_path = dl_path or 'temp_label.pdf'
        back = self.backend(msgs.PrintLabelService)
        req = msgs.PrintLabelRequest(authentication=self.config.auth, shipment_number=ship_num)
        response: msgs.PrintLabelResponse = back.printlabel(request=req)
        out_path = response.label.download(Path(dl_path))
        return out_path

    def choose_address(
            self,
            address: models.AddressRecipient
    ) -> models.AddressRecipient:
        if candidates := self.candidates_dict(address.postcode):
            chosen, score = process.extractOne(
                address.lines_str,
                list(candidates.keys()),
                scorer=SCORER
            )
            add = candidates[chosen]
            return add
        else:
            raise ValueError(f'No candidates found for {address.postcode}')

    def candidates_dict(self, postcode):
        return {add.lines_str: add
                for add in self.get_candidates(postcode)}

    def state_to_outbound_request(self, state: ship_ui.ShipState):
        ship_req = shipstate_to_outbound(state)
        req = msgs.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req


def shipstate_to_outbound(state: ship_ui.ShipState) -> models.RequestedShipmentMinimum:
    sett = pf_config.PF_SETTINGS
    return models.RequestedShipmentMinimum(
        contract_number=sett.pf_contract_num_1,
        service_code=pf_shared.ServiceCode.EXPRESS24,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=state.address,
        total_number_of_parcels=state.boxes,
        reference_number1=state.reference,
    )
