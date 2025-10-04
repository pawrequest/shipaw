from pprint import pprint

from shipaw.providers.apc.provider import APCShippingProvider
from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider
from shipaw.providers.registry import PROVIDER_TYPE_REGISTER


def test_settings(sample_settings):
    assert sample_settings.provider_dict
    pprint(sample_settings.provider_dict)


def test_provider_from_settings(sample_provider):
    assert sample_provider
    assert sample_provider.settings


def test_providers_registered():
    providers = PROVIDER_TYPE_REGISTER
    assert 'PARCELFORCE' in providers
    assert 'APC' in providers
    assert ParcelforceShippingProvider in providers.values()
    assert APCShippingProvider in providers.values()

