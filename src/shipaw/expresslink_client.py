from __future__ import annotations

import functools
from pathlib import Path

import pydantic
import zeep
from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from loguru import logger
from pydantic import model_validator
from thefuzz import fuzz, process
from zeep.proxy import ServiceProxy

from . import models, pf_config
from .models import AddressChoice, pf_models, pf_msg
from .models.pf_msg import CreateShipmentResponse
from .models.pf_services import CreateShipmentService, FindService, PrintLabelService
from .models.pf_shipment import ShipmentRequest

SCORER = fuzz.token_sort_ratio


@functools.lru_cache(maxsize=1)
class ELClient(pydantic.BaseModel):
    """Client for Parcelforce ExpressLink API.

    Attributes:
        settings: pf_config.PFSettings - settings for the client
        service: ServiceProxy | None - Zeep ServiceProxy (generated from settings)
    """

    settings: pf_config.PFSettings = pf_config.pf_sett()
    service: ServiceProxy | None = None

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True, validate_default=True)

    @model_validator(mode='after')
    def get_service(self):
        if self.service is None:
            self.service = self.new_service()
        return self

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(wsdl=self.settings.pf_wsdl)
        return client.create_service(
            binding_name=self.settings.pf_binding,
            address=self.settings.pf_endpoint
        )

    def backend(self, service_prot: type[ServiceProtocolT]) -> zeep.proxy.ServiceProxy:
        """Get a Combadge backend for a service protocol.

        Args:
            service_prot: type[ServiceProtocolT] - service protocol to get backend for

        Returns:
            ServiceProxy - Zeep Proxy

        """
        return ZeepBackend(self.service)[service_prot]

    def shipment_request_authenticated(self, shipment_request: ShipmentRequest):
        return pf_msg.CreateRequest(
            authentication=self.settings.auth,
            requested_shipment=shipment_request,
        )

    def send_shipment_request(
            self,
            requested_shipment: ShipmentRequest
    ) -> pf_msg.CreateShipmentResponse:
        """Submit a CreateRequest to Parcelforce, booking carriage.

        Args:
            requested_shipment: ShipmentRequest - ShipmenmtRequest to book

        Returns:
            .pf_msg.CreateShipmentResponse - response from Parcelforce

        """
        back = self.backend(CreateShipmentService)
        authorized_shipment = pf_msg.CreateRequest(
            authentication=self.settings.auth, requested_shipment=requested_shipment
        )
        resp: CreateShipmentResponse = back.createshipment(
            request=authorized_shipment.model_dump(by_alias=True)
        )
        # if resp.alerts:
        #     for alt in resp.alerts:
        #         if alt.type == 'ERROR':
        #             raise ValueError(
        #                 f'ExpressLink Error: {alt.message} for Shipment reference "{requested_shipment.reference_number1}" to {requested_shipment.recipient_address.lines_str}'
        #                 # f'ExpressLink Error: {alt.message} for {req.requested_shipment.recipient_address.lines_str}'
        #             )
        #         if alt.type == 'WARNING':
        #             logger.warning(
        #                 f'ExpressLink Warning: {alt.message} for Shipment reference "{requested_shipment.reference_number1}" to {requested_shipment.recipient_address.lines_str}'
        #                 # f'ExpressLink Warning: {alt.message} for shipment to {req.requested_shipment.recipient_address.lines_str}'
        #             )
        if resp.shipment_num:
            logger.info(
                f'BOOKED shipment# {resp.shipment_num} to {requested_shipment.recipient_address.lines_str}'
            )
        return resp
        # return pf_msg.CreateShipmentResponse.model_validate(resp)

    def get_candidates(self, postcode: str) -> list[models.AddressRecipient]:
        """Get candidate addresses at a postcode.

        Args:
            postcode: str - postcode to search for

        Returns:
            list[.models.AddressRecipient] - list of candidate addresses

        """
        req = pf_msg.FindRequest(
            authentication=self.settings.auth,
            paf=models.PAF(postcode=postcode)
        )
        back = self.backend(FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
            logger.info(f'No candidates found for {postcode}')
            return []
        return [neighbour.address[0] for neighbour in response.paf.specified_neighbour]

    def get_label(self, ship_num, dl_path: str) -> Path:
        """Get the label for a shipment number.

        Args:
            ship_num: str - shipment number
            dl_path: str - path to download the label to, defaults to './temp_label.pdf'

        Returns:
            Path - path to the downloaded label

        """
        back = self.backend(PrintLabelService)
        req = pf_msg.PrintLabelRequest(authentication=self.settings.auth, shipment_number=ship_num)
        response: pf_msg.PrintLabelResponse = back.printlabel(request=req)
        if response.alerts:
            for alt in response.alerts.alert:
                if alt.type == 'ERROR':
                    raise ValueError(f'ExpressLink Error: {alt.message}')
                logger.warning(f'ExpressLink Warning: {alt.message}')

        out_path = response.label.download(Path(dl_path))
        logger.info(f'Downloaded label to {out_path}')
        return out_path

    def choose_address[T: pf_models.AddTypes](self, address: T) -> T:
        # candidate_dict = self.candidates_dict(address.postcode)
        # chosen, score = process.extractOne(address.lines_str, list(candidate_dict.keys()), scorer=SCORER)
        candidates = self.get_candidates(address.postcode)
        chosen, score = process.extractOne(address.lines_str, candidates, scorer=SCORER)
        return chosen
        # return candidate_dict[chosen]

    def get_choices[T: pf_models.AddTypes](
            self, postcode: str, address: T | None = None
    ) -> list[AddressChoice]:
        candidates = self.get_candidates(postcode)
        if not address:
            return [AddressChoice(address=add, score=0) for add in candidates]

        candidate_dict = {add.lines_str: add for add in candidates}

        scored = process.extract(
            address.lines_str,
            candidate_dict.keys(),
            scorer=SCORER,
            limit=None,
        )
        return sorted(
            [AddressChoice(address=candidate_dict[add], score=score) for add, score in scored],
            key=lambda x: x.score,
            reverse=True
        )

    def candidates_json(self, postcode):
        return {add.lines_str: add.model_dump_json() for add in self.get_candidates(postcode)}
