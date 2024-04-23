from __future__ import annotations

from combadge.support.zeep.backends.sync import ZeepBackend

from shipaw import msgs
from shipaw.models import PAF, pf_ext


def test_find_paf(el_client):
    service = ZeepBackend(el_client.service)[msgs.FindService]
    paf = PAF(postcode='NW6 4TE')
    req = msgs.FindRequest(authentication=el_client.settings.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, msgs.FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], pf_ext.AddressRecipient)


def test_client_gets_candidates(el_client, address_r):
    addresses = el_client.get_candidates(address_r.postcode)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], pf_ext.AddressRecipient)
    assert addresses[0].postcode == address_r.postcode


def test_client_sends_outbound(shipment, el_client, tmp_path):
    req = el_client.state_to_outbound_request(shipment)
    assert isinstance(req, msgs.CreateShipmentRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def test_client_sends_inbound(shipment, el_client, tmp_path):
    req = el_client.state_to_inbound_request(shipment)
    assert isinstance(req, msgs.CreateShipmentRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def check_label(el_client, resp, tmp_path):
    label = el_client.get_label(ship_num=resp.shipment_num, dl_path=tmp_path / 'tmp.pdf')
    assert label.exists()


