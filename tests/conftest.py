# from setup import load_sandbox_envs
# load_sandbox_envs()
import os

from amherst.set_env import set_amherstpr_env

os.environ['AMHERSTPR'] = r'C:\prdev\envs\sandbox'
set_amherstpr_env(sandbox=True)

from shipaw.agnostic.providers import ShippingProvider
from shipaw.apc.provider import APCProvider
from shipaw.parcelforce.provider import ParcelforceProvider

from datetime import date, timedelta

import pytest

from shipaw.agnostic.shipment import Shipment
from shipaw.agnostic.address import Address, Contact, FullContact
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
def sample_full_contact(sample_contact, sample_address):
    yield FullContact(
        contact=sample_contact,
        address=sample_address,
    )


@pytest.fixture(scope='session')
def sample_shipment(sample_full_contact):
    yield Shipment(
        recipient=sample_full_contact,
        boxes=2,
        shipping_date=TEST_DATE,
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference',
        service='NEXT_DAY',
    )


@pytest.fixture(params=[ParcelforceProvider(), APCProvider()], ids=['ParcelforceProvider', 'APCProvider'])
def sample_shipment_dicts(sample_shipment, request):
    provider: ShippingProvider = request.param
    return provider.provider_shipment(sample_shipment, mode='python'), provider
