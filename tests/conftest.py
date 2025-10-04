from datetime import date, timedelta

import pytest

from shipaw.config import ShipawSettings  # FIRST!
from shipaw.providers.apc.provider import APCShippingProvider
from shipaw.providers.providers import PROVIDER_REGISTER, ShippingProvider
from shipaw.models.shipment import Shipment
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.ship_types import ShipDirection
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture
def sample_settings():
    return ShipawSettings(_env_file=r'C:\prdev\envs\amdev\sandbox\shipaw.env')


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
    env_file = sample_settings.provider_dict[name]
    return type_.from_env(env_file)


@pytest.fixture
def sample_contact():
    yield Contact(
        contact_name='Test Contact name',
        mobile_phone='07666666666',
        email_address='dsvkndslvn@dzv.com',
    )


@pytest.fixture
def sample_address():
    yield Address(
        postcode='DA16 3HU',
        address_lines=['25 Bennet Close'],
        town='Welling',
        country='GB',
        business_name='Test Company',
    )


@pytest.fixture
def sample_full_contact(sample_contact, sample_address):
    yield FullContact(
        contact=sample_contact,
        address=sample_address,
    )


@pytest.fixture
def sample_shipment(sample_full_contact):
    yield Shipment(
        recipient=sample_full_contact,
        boxes=2,
        shipping_date=TEST_DATE,
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference',
        service='NEXT_DAY',
    )


# @pytest.fixture(params=[_ for _ in PROVIDER_REGISTER.values()], ids=[_ for _ in PROVIDER_REGISTER.keys()])
# def provider_type(request) -> type[ShippingProvider]:
#     return request.param


# @pytest.fixture
# def provider(provider_type) -> ShippingProvider:
#     return provider_type()


# @pytest.fixture
# def sample_shipment_dicts(sample_shipment, request, provider):
#     res = provider.provider_shipment(sample_shipment)
#     res = res.model_dump()
#     return res, provider
