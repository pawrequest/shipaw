from __future__ import annotations

from typing import Any, Generator

import pytest

from conftest import sample_address
from shipaw.apc.address import Address, apc_address
from shipaw.parcelforce.client import ELClient
from shipaw.parcelforce.models import AddressRecipient
from shipaw.parcelforce.msg import ShipmentRequest, ShipmentResponse
from shipaw.parcelforce.pf_config import PFSandboxSettings, pf_sandbox_sett
from shipaw.parcelforce.shipment import parcelforce_address


@pytest.fixture
def sett():
    settings = pf_sandbox_sett()
    PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett) -> Generator[ELClient, Any, None]:
    yield ELClient(settings=sett)


@pytest.fixture
def address_r(sample_address) -> Generator[AddressRecipient, Any, None]:
    yield parcelforce_address(sample_address)


def test_client_gets_candidates(el_client, address_r):
    addresses = el_client.get_candidates(address_r.postcode)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], AddressRecipient)
    assert addresses[0].postcode == address_r.postcode


def test_client_sends_outbound(shipment, el_client, tmp_path):
    # req = el_client.outbound_shipment_request(shipment)
    shipment.direction = 'out'
    # req = shipment.authenticated(shipment)
    # assert isinstance(req, ShipmentRequest)
    resp = el_client.request_shipment(shipment)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def test_client_sends_inbound(shipment, el_client, tmp_path):
    shipment.direction = 'in'
    req = el_client.shipment_request_authenticated(shipment)
    assert isinstance(req, ShipmentRequest)
    resp = el_client.send_shipment_request(req)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(el_client, resp, tmp_path)


def check_label(el_client, resp, tmp_path):
    label = el_client.get_label(ship_num=resp.shipment_num, dl_path=tmp_path / 'tmp.pdf')
    assert label.exists()
