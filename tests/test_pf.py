from typing import Any, Generator

import pytest

from shipaw.parcelforce.client import ParcelforceClient
from shipaw.parcelforce.address import AddressRecipient
from shipaw.parcelforce.config import pf_settings
from shipaw.parcelforce.shipment import parcelforce_address


@pytest.fixture
def sett():
    settings = pf_settings()
    assert 'test' in settings.pf_endpoint.lower(), 'Not using test endpoint!'
    yield settings


@pytest.fixture
def el_client(sett) -> Generator[ParcelforceClient, Any, None]:
    yield ParcelforceClient(settings=sett)


@pytest.fixture
def address_r(sample_address) -> Generator[AddressRecipient, Any, None]:
    yield parcelforce_address(sample_address)


def test_client_gets_candidates(el_client, address_r):
    addresses = el_client.get_candidates(address_r.postcode)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], AddressRecipient)
    assert addresses[0].postcode == address_r.postcode


# def test_client_sends_outbound(sample_shipment, el_client, tmp_path):
#     # req = el_client.outbound_shipment_request(shipment)
#     sample_shipment.direction = 'out'
#     shipment = ParcelforceProvider.provider_shipment(shipment=sample_shipment, mode='pydantic')
#     # req = shipment.authenticated(shipment)
#     # assert isinstance(req, ShipmentRequest)
#     resp = el_client.request_shipment(shipment)
#     assert isinstance(resp, ShipmentResponse)
#     assert not resp.alerts
#     check_label(el_client, resp, tmp_path)
#
#
# def test_client_sends_inbound(sample_shipment, el_client, tmp_path):
#     sample_shipment.direction = 'out'
#     shipment = ParcelforceProvider.provider_shipment(shipment=sample_shipment, mode='pydantic')
#     resp = el_client.request_shipment(shipment)
#     assert isinstance(resp, ShipmentResponse)
#     assert not resp.alerts
#     check_label(el_client, resp, tmp_path)
#

# def check_label(el_client, resp, tmp_path):
#     label = el_client.get_label(ship_num=resp.shipment_num, dl_path=tmp_path / 'tmp.pdf')
#     assert label.exists()
