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

from docs.source.resources.expresslink_pydantic_generated import AlertType
from .models.pf_combadge import (
    CancelShipmentService,
    CreateManifestService,
    CreateShipmentService,
    FindService,
    PrintLabelService,
)
from .models.pf_models import AddTypes, AddressChoice, AddressRecipient
from .models.pf_msg import (
    CancelShipmentRequest,
    CancelShipmentResponse,
    CreateManifestRequest,
    CreateManifestResponse,
    FindRequest,
    PrintLabelRequest,
    PrintLabelResponse,
    ShipmentRequest,
    ShipmentResponse,
)
from .models.pf_shipment import Shipment
from .models.pf_top import PAF
from .pf_config import PFSettings, pf_sett
from .ship_types import VALID_POSTCODE

SCORER = fuzz.token_sort_ratio


# @functools.lru_cache(maxsize=1)
class ELClient(pydantic.BaseModel):
    """Client for Parcelforce ExpressLink API.

    Attributes:
        settings: pf_config.PFSettings - settings for the client
        service: ServiceProxy | None - Zeep ServiceProxy (generated from settings)
    """

    settings: PFSettings = pf_sett()
    service: ServiceProxy | None = None
    strict: bool = True

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True, validate_default=True)

    @model_validator(mode='after')
    def get_service(self):
        if self.service is None:
            self.service = self.new_service()
        return self

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(
            wsdl=self.settings.pf_wsdl,
            settings=zeep.settings.Settings(strict=self.strict),
        )
        return client.create_service(binding_name=self.settings.pf_binding, address=self.settings.pf_endpoint)

    def backend(self, service_prot: type[ServiceProtocolT]) -> zeep.proxy.ServiceProxy:
        """Get a Combadge backend for a service_code protocol.

        Args:
            service_prot: type[ServiceProtocolT] - service_code protocol to get backend for

        Returns:
            ServiceProxy - Zeep Proxy

        """
        return ZeepBackend(self.service)[service_prot]

    def request_shipment(self, shipment: Shipment) -> ShipmentResponse:
        """Submit a ShipmentRequest to Parcelforce, booking carriage.

        Args:
            shipment: Shipment - ShipmenmtRequest to book

        Returns:
            .ShipmentResponse - response from Parcelforce

        """
        back = self.backend(CreateShipmentService)
        shipment_request = ShipmentRequest(requested_shipment=shipment)
        authorized_shipment = shipment_request.authenticated(self.settings.auth())
        resp: ShipmentResponse = back.createshipment(request=authorized_shipment.model_dump(by_alias=True))
        if hasattr(resp, 'shipment_num') and resp.shipment_num:
            logger.info(f'BOOKED shipment# {resp.shipment_num} to {shipment.recipient_address.lines_str}')
            logger.debug(f'Notifications: {shipment.notifications_str}')
        if hasattr(resp, 'Error'):
            msg = resp.Error.message if hasattr(resp.Error, 'message') else str(resp.Error)
            raise ValueError(f'ExpressLink Error: {msg}')
        if hasattr(resp, 'alerts') and hasattr(resp.alerts, 'alert'):
            for _ in resp.alerts.alert:
                match _.type:
                    case AlertType.ERROR:
                        logger.error("ExpressLinkl Error, booking failed: " + _.message)
                    case _:
                        logger.warning("Expresslink Warning: " + _.message)
        return resp

    def cancel_shipment(self, shipment_number):
        req = CancelShipmentRequest(shipment_number=shipment_number).authenticated(self.settings.auth())
        back = self.backend(CancelShipmentService)
        response: CancelShipmentResponse = back.cancelshipment(request=req.model_dump(by_alias=True))
        return response

    def get_candidates(self, postcode: str) -> list[AddressRecipient]:
        """Get candidate addresses at a postcode.

        Args:
            postcode: str - postcode to search for

        Returns:
            list[.models.AddressRecipient] - list of candidate addresses

        """
        postcode = clean_up_postcode(postcode)
        req = FindRequest(paf=PAF(postcode=postcode)).authenticated(self.settings.auth())
        back = self.backend(FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
            logger.info(f'No candidates found for {postcode}')
            return []
        return [neighbour.address[0] for neighbour in response.paf.specified_neighbour]

    def get_label(self, ship_num, dl_path: str, print_format: str | None = None, barcode_format:str | None = None ) -> Path:
        """Get the label for a shipment number.

        Args:
            ship_num: str - shipment number
            dl_path: str - path to download the label to, defaults to './temp_label.pdf'
            print_format: str | None (default = PDF)
            PDF - to return a PDF image of the Label.
            XML - to return a data stream in order to create own label.
            PDF-XML - to return the Parcelforce label as PDF and the Partner label as XML.
            XML-PDF – to return the Parcelforce label as XML and the Partner label as PDF

            barcode_format: Set to PNG to return image of Barcode in Base64 code

        Returns:
            Path - path to the downloaded label

        """
        back = self.backend(PrintLabelService)
        # req = PrintLabelRequest(authentication=self.settings.auth(), shipment_number=ship_num)
        req = PrintLabelRequest(authentication=self.settings.auth(), shipment_number=ship_num, print_format=print_format, barcode_format=barcode_format)
        response: PrintLabelResponse = back.printlabel(request=req)
        if response.alerts:
            for alt in response.alerts.alert:
                if alt.type == 'ERROR':
                    raise ValueError(f'ExpressLink Error: {alt.message}')
                logger.warning(f'ExpressLink Warning: {alt.message}')

        out_path = response.label.download(Path(dl_path))
        logger.info(f'Downloaded label to {out_path}')
        return out_path

    def get_manifest(self):
        back = self.backend(CreateManifestService)
        req = CreateManifestRequest(authentication=self.settings.auth())
        response: CreateManifestResponse = back.createmanifest(request=req)
        return response

    def choose_address[T: AddTypes](self, address: T) -> tuple[T, int]:
        """Takes a potentially invalid address, and returns the closest match from ExpressLink with fuzzy score."""
        candidates = self.get_candidates(address.postcode)
        candidate_strs = [c.lines_str for c in candidates]
        chosen, score = process.extractOne(address.lines_str, candidate_strs, scorer=SCORER)
        chosen_add = candidates[candidate_strs.index(chosen)]
        return chosen_add, score

    def address_choice[T: AddTypes](self, address: T) -> AddressChoice:
        logger.info(f'Choosing address for {address.lines_str} @ {address.postcode}')
        chosen, score = self.choose_address(address)
        return AddressChoice(address=chosen, score=score)

    def get_choices[T: AddTypes](self, postcode: VALID_POSTCODE, address: T | None = None) -> list[AddressChoice]:
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
        choices = [AddressChoice(address=candidate_dict[add], score=score) for add, score in scored]
        return sorted(
            choices,
            key=lambda x: x.score,
            reverse=True,
        )

    def candidates_json(self, postcode):
        return {add.lines_str: add.model_dump_json() for add in self.get_candidates(postcode)}


def clean_up_postcode(postcode: str):
    postcode = postcode.upper()
    return postcode
