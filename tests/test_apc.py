import os
from datetime import date, timedelta

import dotenv
import httpx
import pytest

from shipaw.ship_types import ShipDirection

from shipaw.agnostic.agnost import Address, Contact, Shipment
from shipaw.apc.address import Address as APCAddress, Contact as APCContact, apc_address, apc_contact
from shipaw.apc.services import APCService, ServiceSpec
from shipaw.apc.shared import APC_ENV, EndPoints, get_headers
from shipaw.apc.shipment import Order, apc_shipment

dotenv.load_dotenv(APC_ENV)

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())
TEST_DATE = TEST_DATE.strftime('%d/%m/%Y')


@pytest.fixture
def sample_contact():
    yield Contact(
        contact_name='Test Contact name',
        mobile_phone='07666666666',
        email_address='dsvkndslvn@dzv.com',
        business_name='Test Company',
    )


@pytest.fixture
def sample_address():
    yield Address(
        postcode='DA16 3HU',
        address_lines=['25 Bennet Close'],
        town='Welling',
        country='GB',
    )


@pytest.fixture
def sample_shipment(sample_contact, sample_address):
    yield Shipment(
        recipient_contact=sample_contact,
        recipient_address=sample_address,
        boxes=2,
        shipping_date=date.today() + timedelta(days=3),
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference',
        service=APCService.next_day_16(),
    )


def test_sample_fixtures(sample_contact, sample_address, sample_shipment):
    assert sample_contact.contact_name == 'Test Contact name'
    assert sample_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


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


@pytest.fixture
def service_request():
    yield {
        'Orders': {
            'Order': {
                'CollectionDate': TEST_DATE,
                'ReadyAt': '09:00',
                'ClosedAt': '18:00',
                'ProductCode': 'ND16',
                # 'Reference': 'Test',
                'Delivery': {'PostalCode': 'M17 1WA', 'CountryCode': 'GB'},
                # 'GoodsInfo': {'GoodsValue': '1', 'GoodsDescription': '.....'},
                'ShipmentDetails': {
                    'NumberofPieces': '1',
                    'Items': {'Item': {'Type': 'ALL', 'Weight': '1'}},
                },
            }
        }
    }


def test_service_available(sample_shipment_export_dict):
    res = httpx.post(EndPoints.SERVICES, headers=get_headers(), json=sample_shipment_export_dict, timeout=30)
    res.raise_for_status()
    res_json = res.json()
    avail = res_json['ServiceAvailability']['Services']['Service']
    services = [ServiceSpec(**_) for _ in avail]
    nd = [_ for _ in services if _.ProductCode == 'APCND16']
    assert nd


@pytest.fixture
def sample_shipment_export_dict(sample_shipment):
    shipment = apc_shipment(sample_shipment)
    yield shipment.export_dict()


def test_shipment_export_dict(sample_shipment, sample_shipment_export_dict):
    assert sample_shipment_export_dict['Orders']['Order']['CollectionDate'] == (
        date.today() + timedelta(days=3)
    ).strftime('%d/%m/%Y')
    assert (
        len(sample_shipment_export_dict['Orders']['Order']['ShipmentDetails']['Items']['Item']) == sample_shipment.boxes
    )


def test_make_shipment_request1(sample_shipment, sample_shipment_export_dict):
    res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=sample_shipment_export_dict)
    res.raise_for_status()
    res_json = res.json()
    assert res_json['Orders']['Order']['Collection']
    ...
