from pprint import pprint

from shipaw.providers.apc.apc_provider import APCShippingProvider
from shipaw.providers.registry import PROVIDER_REGISTER, PROVIDER_TYPE_REGISTER


def test_settings(sample_settings):
    assert sample_settings.provider_env_dict
    pprint(sample_settings.provider_env_dict)


def test_provider_has_settings(sample_provider):
    assert sample_provider
    assert sample_provider.shipaw_settings


def test_provider_types_registered_by_code():
    provider_types = PROVIDER_TYPE_REGISTER
    assert 'APC' in provider_types
    assert APCShippingProvider in provider_types.values()


def test_providers_registered_by_settings(sample_settings):
    provs = PROVIDER_REGISTER
    assert len(provs) == 2
