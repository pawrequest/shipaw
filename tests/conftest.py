from datetime import date, timedelta

import pytest

from shipaw.config import ShipawSettings  # FIRST!
from shipaw.models.services import AgnostServiceName
from shipaw.models.shipment import Shipment
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection
from shipaw.providers import RoyalMailProvider
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture
def sample_settings():
    return ShipawSettings(_env_file=r'C:\prdev\envs\amdev\sandbox\shipaw.env')


@pytest.fixture
def sample_settings_rm():
    return ShipawSettings(_env_file=r'C:\prdev\envs\amdev\with_rm.env')


@pytest.fixture(
    params=[
        ('APC', PROVIDER_TYPE_REGISTER['APC']),
        ('PARCELFORCE', PROVIDER_TYPE_REGISTER['PARCELFORCE']),
    ],
    ids=lambda val: val[0],
)
def sample_provider(sample_settings, request):
    name = request.param[0]
    type_ = request.param[1]
    env_file = sample_settings.provider_env_dict[name]
    provider = type_.from_env(env_file)
    assert provider.is_sandbox(), f'Must use sandbox environment for tests, {provider.settings=}'
    return provider


@pytest.fixture
def sample_provider_rm(sample_settings_rm):
    return RoyalMailProvider.from_shipaw_settings_env_dict(shipaw_settings=sample_settings_rm)


@pytest.fixture
def sample_remote_contact():
    yield Contact(
        contact_name='Test Remote Contact Name',
        mobile_phone='07666666666',
        email_address='remote@dzv.com',
    )


@pytest.fixture
def sample_remote_address():
    yield Address(
        postcode='DA16 3HU',
        address_lines=['25 Remote Street'],
        town='Welling',
        country='GB',
        business_name='Remote Company',
    )


@pytest.fixture
def sample_remote_fc(sample_remote_contact, sample_remote_address):
    yield FullContact(
        contact=sample_remote_contact,
        address=sample_remote_address,
    )


@pytest.fixture
def sample_home_contact():
    yield Contact(
        contact_name='Home Contact name',
        mobile_phone='07555555555',
        email_address='home@sdagfdasg.com',
    )


@pytest.fixture
def sample_home_address():
    yield Address(
        postcode='W1A 1AA',
        address_lines=['1 Home Street'],
        town='London',
        country='GB',
        business_name='Home Company',
    )


@pytest.fixture
def sample_full_home_contact(sample_home_contact, sample_home_address):
    yield FullContact(
        contact=sample_home_contact,
        address=sample_home_address,
    )


@pytest.fixture
def sample_shipment(sample_remote_fc):
    yield Shipment(
        recipient=sample_remote_fc,
        boxes=2,
        shipping_date=TEST_DATE,
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference outbound',
        service=AgnostServiceName.NEXT_DAY,
    )


@pytest.fixture
def sample_shipment_inbound(sample_remote_fc, sample_full_home_contact):
    return Shipment(
        sender=sample_remote_fc,
        recipient=sample_full_home_contact,
        boxes=1,
        shipping_date=TEST_DATE,
        direction=ShipDirection.INBOUND,
        reference='Test Inbound Reference',
        service=AgnostServiceName.NEXT_DAY,
        own_label=True,
    )


@pytest.fixture
def sample_shipment_dropoff(sample_shipment_inbound):
    dropoff = sample_shipment_inbound.model_copy()
    dropoff.direction = ShipDirection.DROPOFF
    dropoff.reference = 'Test Dropoff Reference'
    dropoff.own_label = None
    return dropoff


@pytest.fixture(params=['sample_shipment', 'sample_shipment_inbound', 'sample_shipment_dropoff'], ids=lambda val: val)
def all_sample_shipments(request):
    return request.getfixturevalue(request.param)
