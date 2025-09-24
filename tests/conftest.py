from pathlib import Path
from amherst.set_env import set_env_files

ENV_DIR = Path(r'C:\prdev\envs\sandbox')
set_env_files(ENV_DIR)
assert ENV_DIR.name == 'sandbox'

from shipaw.agnostic.providers import ShippingProvider
from shipaw.apc.provider import APCProvider
from shipaw.parcelforce.provider import ParcelforceProvider

from datetime import date, timedelta

import pytest

from shipaw.agnostic.shipment import Shipment
from shipaw.agnostic.address import Address, Contact, FullContact
from shipaw.agnostic.ship_types import ShipDirection, pydantic_export

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def sample_contact():
    yield Contact(
        contact_name='Test Contact name',
        mobile_phone='07666666666',
        email_address='dsvkndslvn@dzv.com',
    )


@pytest.fixture(scope='session')
def sample_address():
    yield Address(
        postcode='DA16 3HU',
        address_lines=['25 Bennet Close'],
        town='Welling',
        country='GB',
        business_name='Test Company',
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
    res = provider.shipment_type.from_generic(sample_shipment)
    res = pydantic_export(res, mode='python')
    return res, provider
