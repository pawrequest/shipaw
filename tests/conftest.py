import os
os.environ['ENV_INDEX'] = r'C:\prdev\envs\sandbox.env'

from shipaw.config import shipaw_settings  # FIRST!
from shipaw.providers.apc.provider import APCShippingProvider  # noqa
from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider  # noqa


from shipaw.models.provider import PROVIDER_REGISTER, ShippingProvider

from datetime import date, timedelta

import pytest

from shipaw.models.shipment import Shipment
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def settings():
    return shipaw_settings()


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


@pytest.fixture(params=[_ for _ in PROVIDER_REGISTER.values()], ids=[_ for _ in PROVIDER_REGISTER.keys()])
def provider_type(request) -> type[ShippingProvider]:
    return request.param


@pytest.fixture
def provider(provider_type) -> ShippingProvider:
    return provider_type()


@pytest.fixture
def sample_shipment_dicts(sample_shipment, request, provider):
    res = provider.provider_shipment(sample_shipment)
    res = res.model_dump()
    return res, provider
