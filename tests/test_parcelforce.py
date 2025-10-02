import pytest
from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.address import AddressRecipient
from parcelforce_expresslink.config import pf_settings
from parcelforce_expresslink.request_response import ShipmentResponse

from shipaw.providers.parcelforce.provider_funcs import address_from_agnostic_fc, parcelforce_shipment_from_agnostic


@pytest.fixture
def sett():
    settings = pf_settings()
    assert 'test' in settings.pf_endpoint.lower(), 'Not using test endpoint!'
    yield settings


@pytest.fixture
def parcelforce_client(sett) -> ParcelforceClient:
    return ParcelforceClient(settings=sett)


@pytest.fixture
def address_r(sample_full_contact) -> AddressRecipient:
    return address_from_agnostic_fc(AddressRecipient, full_contact=sample_full_contact)


def test_client_gets_candidates(parcelforce_client, address_r):
    addresses = parcelforce_client.get_candidates(address_r.postcode)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], AddressRecipient)
    assert addresses[0].postcode == address_r.postcode


def check_label(el_client, resp, tmp_path):
    label_data = el_client.get_label_content(ship_num=resp.shipment_num)
    output = tmp_path / f'{resp.shipment_num}.pdf'
    output.write_bytes(label_data)
    assert output.exists()


def test_client_sends_outbound(sample_shipment, parcelforce_client:ParcelforceClient, tmp_path):
    # req = el_client.outbound_shipment_request(shipment)
    sample_shipment.direction = 'out'
    shipment = parcelforce_shipment_from_agnostic(shipment=sample_shipment)
    # req = shipment.authenticated(shipment)
    # assert isinstance(req, ShipmentRequest)
    resp = parcelforce_client.request_shipment(shipment)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(parcelforce_client, resp, tmp_path)


#
#
# def test_client_sends_inbound(sample_shipment, el_client, tmp_path):
#     sample_shipment.direction = 'out'
#     shipment = ParcelforceShippingProvider.provider_shipment_fn(shipment=sample_shipment, mode='pydantic')
#     resp = el_client.request_shipment(shipment)
#     assert isinstance(resp, ShipmentResponse)
#     assert not resp.alerts
#     check_label(el_client, resp, tmp_path)
#

