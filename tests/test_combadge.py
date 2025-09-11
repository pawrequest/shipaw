from __future__ import annotations

from shipaw import msgs
from shipaw.models import pf_ext


def test_client_gets_candidates(el_client, address_r):
    addresses = el_client.get_candidates(address_r.postal_code)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], pf_ext.AddressRecipient)
    assert addresses[0].postal_code == address_r.postal_code


def test_client_sends_outbound(shipment, el_client, tmp_path):
    # req = el_client.outbound_shipment_request(shipment)
    shipment.direction = 'out'
    req = shipment.authenticated(shipment)
    assert isinstance(req, msgs.CreateRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def test_client_sends_inbound(shipment, el_client, tmp_path):
    shipment.direction = 'in'
    req = el_client.shipment_request_authenticated(shipment)
    assert isinstance(req, msgs.CreateRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, msgs.CreateShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def check_label(el_client, resp, tmp_path):
    label = el_client.get_label(ship_num=resp.shipment_num, dl_path=tmp_path / 'tmp.pdf')
    assert label.exists()
