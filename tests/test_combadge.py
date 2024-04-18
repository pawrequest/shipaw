from combadge.support.zeep.backends.sync import ZeepBackend
from dotenv import load_dotenv

from shipaw import ELClient, msgs
from shipaw.models import PAF, pf_ext

ENV_FILE = r'R:\paul_r\.internal\envs\sandbox.env'
load_dotenv(ENV_FILE)


def test_find_paf():
    el_client = ELClient.from_pyd()
    service = ZeepBackend(el_client.service)[msgs.FindService]
    paf = PAF(postcode='NW6 4TE')
    req = msgs.FindRequest(authentication=el_client.config.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, msgs.FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], pf_ext.AddressRecipient)


def test_get_shipment(min_shipment_r, service, pf_auth):
    cb = combadge_service(service, msgs.CreateShipmentService)
    req = msgs.CreateShipmentRequest(authentication=pf_auth, requested_shipment=min_shipment_r)
    resp: msgs.CreateShipmentResponse = cb.createshipment(request=req)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    assert isinstance(shipment_.shipment_number, str)


def combadge_service(service, service_prot):
    return ZeepBackend(service)[service_prot]
