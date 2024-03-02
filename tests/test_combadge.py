import os

from combadge.support.zeep.backends.sync import ZeepBackend
from dotenv import load_dotenv

from shipr.el_combadge import PFCom, PFCom
from shipr.models.pf_msg_protocols import CreateShipmentService, FindService
from shipr.express.expresslink_pydantic import (
    PAF,
)
from shipr import AddressPF
from shipr.express.pf_msg import (
    CreateShipmentRequest,
    CreateShipmentResponse,
    FindRequest,
    FindResponse,
)

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)



def test_find_paf(zconfig):
    pfc = PFCom.from_config(zconfig)
    service = ZeepBackend(pfc.service)[FindService]
    paf = PAF(postcode='NW6 4TE')
    req = FindRequest(authentication=zconfig.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], AddressPF)


def test_get_shipment(min_shipment_r, service, pf_auth):
    cb = combadge_service(service, CreateShipmentService)
    req = CreateShipmentRequest(authentication=pf_auth, requested_shipment=min_shipment_r)
    resp: CreateShipmentResponse = cb.createshipment(request=req)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    assert isinstance(shipment_.shipment_number, str)


def test_pfc2(zconfig, pf_com):
    back = pf_com.backend(FindService)
    req = FindRequest(authentication=zconfig.auth, paf=PAF(postcode='NW6 4TE'))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], AddressPF)


def combadge_service(service, service_prot):
    return ZeepBackend(service)[service_prot]
