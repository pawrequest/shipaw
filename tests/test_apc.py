import time

import httpx
import pytest

from conftest import TEST_DATE
from shipaw.apc.requests import dl_label, make_shipment_request

from shipaw.apc.address import Address as APCAddress, Contact as APCContact, apc_address, apc_contact
from shipaw.apc.services import ServiceSpec
from shipaw.apc.shared import EndPoints, apc_date, get_headers
from shipaw.apc.shipment import Order
from shipaw.apc.provider import apc_shipment, apc_shipment_dict

TEST_DATE_STR = apc_date(TEST_DATE)


@pytest.fixture(scope='session')
def sample_shipment_export_dict_apc(sample_shipment):
    yield apc_shipment_dict(sample_shipment)


@pytest.fixture(scope='session')
def booking_response(sample_shipment_export_dict_apc):
    yield make_shipment_request(sample_shipment_export_dict_apc)


def test_convert_contact(sample_contact):
    contact = apc_contact(sample_contact)
    assert isinstance(contact, APCContact)
    assert contact.person_name == 'Test Contact name'


def test_convert_address(sample_address, sample_contact):
    addr = apc_address(sample_address, sample_contact)
    assert isinstance(addr, APCAddress)
    assert addr.postal_code == 'DA16 3HU'
    assert addr.contact.person_name == 'Test Contact name'


def test_convert_shipment(sample_shipment):
    shipment: Order = apc_shipment(sample_shipment)
    assert isinstance(shipment, Order)
    assert shipment.delivery.postal_code == 'DA16 3HU'


def test_service_available(sample_shipment_export_dict_apc):
    res = httpx.post(EndPoints.SERVICES, headers=get_headers(), json=sample_shipment_export_dict_apc, timeout=30)
    res.raise_for_status()
    res_json = res.json()
    avail = res_json['ServiceAvailability']['Services']['Service']
    services = [ServiceSpec(**_) for _ in avail]
    nd = [_ for _ in services if _.ProductCode == 'APCND16']
    assert nd


def test_shipment_export_dict(sample_shipment, sample_shipment_export_dict_apc):
    assert sample_shipment_export_dict_apc['Orders']['Order']['CollectionDate'] == apc_date(TEST_DATE)
    assert (
        len(sample_shipment_export_dict_apc['Orders']['Order']['ShipmentDetails']['Items']['Item'])
        == sample_shipment.boxes
    )


def test_make_shipment_request(booking_response):
    order_num = booking_response.shipment_num
    assert order_num


def test_download_label(booking_response, tmp_path):
    order_num = booking_response.shipment_num
    time.sleep(4)  # Ensure the label is ready
    dld_label = dl_label(order_num, tmp_path / f'{order_num}.pdf')
    assert dld_label.exists()

