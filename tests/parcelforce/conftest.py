import pytest
from parcelforce_expresslink.tests.conftest import (
    sample_client,
    sample_settings as sample_settings_pf,
)

from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider


@pytest.fixture
def sample_parcelforce_provider(sample_settings_pf):
    return ParcelforceShippingProvider(settings=sample_settings_pf)


__all__ = [
    'sample_client',
    'sample_settings_pf',
]