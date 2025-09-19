import os

import dotenv

from shipaw.agnostic.providers import ShippingProvider

APC_ENV = r'C:\prdev\repos\amdev\shipaw\apc_sandbox.env'

os.environ['SHIP_ENV'] = r'C:\ProgramData\AmherstPR\pf_sandbox.env'
dotenv.load_dotenv(APC_ENV)

from shipaw.apc.provider import APCProvider
from shipaw.parcelforce.provider import ParcelforceProvider

from datetime import date, timedelta

import pytest

from shipaw.agnostic.shipment import Shipment
from shipaw.agnostic.address import Address, Contact
from shipaw.agnostic.services import ServiceType
from shipaw.agnostic.ship_types import ShipDirection


TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def sample_contact():
    yield Contact(
        contact_name='Test Contact name',
        mobile_phone='07666666666',
        email_address='dsvkndslvn@dzv.com',
        business_name='Test Company',
    )


@pytest.fixture(scope='session')
def sample_address():
    yield Address(
        postcode='DA16 3HU',
        address_lines=['25 Bennet Close'],
        town='Welling',
        country='GB',
    )


@pytest.fixture(scope='session')
def sample_shipment(sample_contact, sample_address):
    yield Shipment(
        recipient_contact=sample_contact,
        recipient_address=sample_address,
        boxes=2,
        shipping_date=TEST_DATE,
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference',
        service='NEXT_DAY',
    )


@pytest.fixture(params=[ParcelforceProvider(), APCProvider()], ids=['ParcelforceProvider', 'APCProvider'])
def sample_shipment_dicts(sample_shipment, request):
    provider: ShippingProvider = request.param
    return provider.make_shipment_dict(sample_shipment), provider
