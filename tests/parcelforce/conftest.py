import sys

import pytest
from parcelforce_expresslink.expresslink_client import ParcelforceClient

from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider
from parcelforce_expresslink.config import ParcelforceSettings


@pytest.fixture
def sample_pf_settings():
    settings = ParcelforceSettings.from_env()
    assert 'test' in settings.pf_endpoint.lower(), 'Not using test endpoint!'
    return settings


@pytest.fixture
def sample_pf_client() -> ParcelforceClient:
    client = ParcelforceClient.from_env()
    return client

@pytest.fixture
def sample_parcelforce_provider(sample_pf_settings):
    return ParcelforceShippingProvider(settings=sample_pf_settings)

