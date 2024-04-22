from combadge.support.zeep.backends.sync import ZeepBackend

from shipaw import ShipState, msgs
from shipaw.models import PAF, pf_ext, shipable


def test_find_paf(el_client):
    service = ZeepBackend(el_client.service)[msgs.FindService]
    paf = PAF(postcode='NW6 4TE')
    req = msgs.FindRequest(authentication=el_client.settings.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, msgs.FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], pf_ext.AddTypes)


def test_shipable_record(outbound_record):
    shipable.Shipable.model_validate(outbound_record)
    assert ShipState.model_validate(outbound_record.ship_state)


def test_client_sends_outbound(outbound_record, el_client, tmp_path):
    req = el_client.state_to_outbound_request(outbound_record.ship_state)
    assert isinstance(req, msgs.CreateShipmentRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def check_label(el_client, resp, tmp_path):
    label = el_client.get_label(ship_num=resp.shipment_num, dl_path=tmp_path / 'tmp.pdf')
    assert label.exists()


def test_client_sends_inbound(inbound_record, el_client, tmp_path):
    req = el_client.state_to_inbound_request(inbound_record.ship_state)
    assert isinstance(req, msgs.CreateShipmentRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)
