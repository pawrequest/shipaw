import httpx
import pytest
from pawdantic.paw_types import pydantic_export

from conftest import TEST_DATE
from shipaw.fapi.responses import ShipmentBookingResponse
from apc_hypaship.address import Address as APCAddress, Contact, Contact as APCContact
from apc_hypaship.config import apc_date, apc_settings
from apc_hypaship.services import ServiceSpec
from apc_hypaship.shipment import Shipment as APCShipment
from shipaw.providers.apc_provider import (
    APCShippingProvider,
    address_from_agnostic_fc,
    apc_shipment_from_agnostic,
    contact_from_agnostic_fc,
)

TEST_DATE_STR = apc_date(TEST_DATE)
PROVIDER = APCShippingProvider()


@pytest.fixture(scope='session')
def sample_shipment_dict_apc(sample_shipment):
    res = PROVIDER.provider_shipment(shipment=sample_shipment)
    res = pydantic_export(res, mode='python-alias')
    yield res
    ...


@pytest.fixture(scope='session')
def booking_response(sample_shipment) -> ShipmentBookingResponse:
    return PROVIDER.book_shipment(shipment=sample_shipment)


def test_convert_contact(sample_full_contact):
    contact = contact_from_agnostic_fc(Contact, sample_full_contact)
    assert isinstance(contact, APCContact)
    assert contact.person_name == 'Test Contact name'


def test_convert_address(sample_full_contact):
    addr = address_from_agnostic_fc(APCAddress, sample_full_contact)
    assert isinstance(addr, APCAddress)
    assert addr.postal_code == 'DA16 3HU'
    assert addr.contact.person_name == 'Test Contact name'


def test_convert_shipment(sample_shipment):
    shipment: APCShipment = apc_shipment_from_agnostic(sample_shipment)
    assert isinstance(shipment, APCShipment)
    assert shipment.orders.order.delivery.postal_code == 'DA16 3HU'


def test_service_available(sample_shipment_dict_apc):
    settings = apc_settings()
    res = httpx.post(settings.services_endpoint, headers=settings.headers, json=sample_shipment_dict_apc, timeout=30)
    res.raise_for_status()
    res_json = res.json()
    avail = res_json['ServiceAvailability']['Services']['Service']
    services = [ServiceSpec(**_) for _ in avail]
    nd = [_ for _ in services if _.ProductCode == 'APCND16']
    assert nd


def test_shipment_export_dict(sample_shipment, sample_shipment_dict_apc):
    assert sample_shipment_dict_apc['Orders']['Order']['CollectionDate'] == apc_date(TEST_DATE)
    assert len(sample_shipment_dict_apc['Orders']['Order']['ShipmentDetails']['Items']['Item']) == sample_shipment.boxes


def test_make_shipment_request(booking_response):
    order_num = booking_response.shipment_num
    assert order_num


def test_download_label(booking_response, tmp_path):
    label_file = tmp_path / 'label.pdf'  # Create a file path inside the temp directory
    label_file.write_bytes(booking_response.label_data)
    assert label_file.exists()
    assert label_file.stat().st_size > 1000

