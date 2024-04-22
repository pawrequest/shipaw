from __future__ import annotations

from pathlib import Path

import pydantic
import zeep
from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from loguru import logger
from pydantic import model_validator
from thefuzz import fuzz, process
from zeep.proxy import ServiceProxy

from . import models, msgs, pf_config, ship_ui
<<<<<<< HEAD
from .models import pf_shared
=======
from .models import pf_ext, pf_top
>>>>>>> recov

SCORER = fuzz.token_sort_ratio


<<<<<<< HEAD
class ZeepConfig(pydantic.BaseModel):
    auth: models.Authentication
    binding: str
    wsdl: str
    endpoint: str

    @classmethod
    def fetch(cls, settings=pf_config.PF_SETTINGS):
        return cls(
            auth=models.Authentication(password=settings.pf_expr_pwd, user_name=settings.pf_expr_usr),
            binding=settings.pf_binding,
            wsdl=settings.pf_wsdl,
            endpoint=str(settings.pf_endpoint),
        )


=======
>>>>>>> recov
class ELClient(pydantic.BaseModel):
    """Client for Parcelforce ExpressLink API.

    Attributes:
        settings: pf_config.PFSettings - settings for the client
        service: ServiceProxy | None - Zeep ServiceProxy (generated from settings)
    """

    settings: pf_config.PFSettings = pf_config.PF_SETTINGS
    service: ServiceProxy | None = None

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True, validate_default=True)

<<<<<<< HEAD
    @model_validator(mode="after")
    def get_service(self):
        if self.service is None:
            self.service = self.new_service()
=======
    @model_validator(mode='after')
    def get_service(self):
        if self.service is None:
            self.service = self.new_service()
        return self
>>>>>>> recov

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(wsdl=self.settings.pf_wsdl)
        return client.create_service(binding_name=self.settings.pf_binding, address=self.settings.pf_endpoint)

    def backend(self, service_prot: type[ServiceProtocolT]) -> zeep.proxy.ServiceProxy:
        """Get a Combadge backend for a service protocol.

        Args:
            service_prot: type[ServiceProtocolT] - service protocol to get backend for

        Returns:
            ServiceProxy - Zeep Proxy

        """
        return ZeepBackend(self.service)[service_prot]

<<<<<<< HEAD
    def shipment_req_to_resp(self, req: msgs.CreateShipmentRequest) -> msgs.CreateShipmentResponse:
=======
    def send_shipment_request(self, req: msgs.CreateShipmentRequest) -> msgs.CreateShipmentResponse:
>>>>>>> recov
        """Submit a CreateShipmentRequest to Parcelforce, booking carriage.

        Args:
            req: .msgs.CreateShipmentRequest - ShipmenmtRequest to book

        Returns:
            .msgs.CreateShipmentResponse - response from Parcelforce

        """
        back = self.backend(msgs.CreateShipmentService)
        resp = back.createshipment(request=req.model_dump(by_alias=True))
<<<<<<< HEAD
        logger.warning(f"BOOKED {req.requested_shipment.recipient_address.lines_str}")
=======
        if resp.alerts:
            for alt in resp.alerts.alert:
                if alt.type == 'ERROR':
                    raise ValueError(f'ExpressLink Error: {alt.message} for {req.requested_shipment.recipient_address.lines_str}')
                if alt.type == 'WARNING':
                    logger.warning(f'ExpressLink Warning: {alt.message} for {req.requested_shipment.recipient_address.lines_str}')
        else:
            logger.warning(f'BOOKED {req.requested_shipment.recipient_address.lines_str}')
>>>>>>> recov

        return msgs.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[models.AddressRecipient]:
        """Get candidate addresses at a postcode.

        Args:
            postcode: str - postcode to search for

        Returns:
            list[.models.AddressRecipient] - list of candidate addresses

        """
        req = msgs.FindRequest(authentication=self.settings.auth, paf=models.PAF(postcode=postcode))
        back = self.backend(msgs.FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
<<<<<<< HEAD
=======
            logger.info(f'No candidates found for {postcode}')
>>>>>>> recov
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
        sett = pf_config.PF_SETTINGS
<<<<<<< HEAD
        dl_path = dl_path or sett.label_dir / "temp_label.pdf"
=======
        dl_path = dl_path or sett.label_dir / 'temp_label.pdf'
>>>>>>> recov
        back = self.backend(msgs.PrintLabelService)
        req = msgs.PrintLabelRequest(authentication=self.settings.auth, shipment_number=ship_num)
        response: msgs.PrintLabelResponse = back.printlabel(request=req)
        out_path = response.label.download(Path(dl_path))
<<<<<<< HEAD
        return out_path

    def choose_address(self, address: models.AddressRecipient) -> models.AddressRecipient:
        if candidates := self.candidates_dict(address.postcode):
            chosen, score = process.extractOne(address.lines_str, list(candidates.keys()), scorer=SCORER)
            add = candidates[chosen]
            return add
        else:
            raise ValueError(f"No candidates found for {address.postcode}")
=======
        logger.info(f'Downloaded label to {out_path}')
        return out_path

    def choose_address(
        self, address: pf_ext.AddressCollection
    ) -> tuple[models.AddressRecipient, list[models.AddressRecipient]]:
        candidate_dict = self.candidates_dict(address.postcode)
        chosen, score = process.extractOne(address.lines_str, list(candidate_dict.keys()), scorer=SCORER)
        return candidate_dict[chosen], list(candidate_dict.values())
>>>>>>> recov

    def candidates_dict(self, postcode):
        return {add.lines_str: add for add in self.get_candidates(postcode)}

    def state_to_outbound_request(self, state: ship_ui.ShipState):
<<<<<<< HEAD
        ship_req = shipstate_to_outbound(state)
        req = msgs.CreateShipmentRequest(authentication=self.settings.auth, requested_shipment=ship_req)
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
=======
        return msgs.CreateShipmentRequest(
            authentication=self.settings.auth,
            requested_shipment=models.RequestedShipmentMinimum(
                contract_number=self.settings.pf_contract_num_1,
                service_code=state.service,
                shipping_date=state.ship_date,
                recipient_contact=state.contact,
                recipient_address=state.address,
                total_number_of_parcels=state.boxes,
                reference_number1=state.reference,
            ),
        )

    def state_to_inbound_request(
        self,
        state: ship_ui.ShipState,
    ):
        return msgs.CreateShipmentRequest(
            authentication=self.settings.auth,
            requested_shipment=pf_top.CollectionSimple(
                contract_number=self.settings.pf_contract_num_1,
                service_code=state.service,
                shipping_date=state.ship_date,
                recipient_contact=self.settings.home_contact,
                recipient_address=self.settings.home_address,
                total_number_of_parcels=state.boxes,
                print_own_label=True,
                collection_info=pf_top.collection_info_from_state(state),
                reference_number1=state.reference,
                special_instructions1=state.special_instructions,
            ),
        )

    def state_to_request(self, state: ship_ui.ShipState):
        if state.direction == 'in':
            return self.state_to_inbound_request(state)
        if state.direction == 'out':
            return self.state_to_outbound_request(state)
        raise ValueError('Invalid direction')
>>>>>>> recov
