from shipaw.providers.apc_provider import APCShippingProvider
from shipaw.models.provider import PROVIDER_REGISTER, ShippingProvider
from shipaw.providers.parcelforce_provider import ParcelforceShippingProvider


def test_providers_registered():
    providers = PROVIDER_REGISTER
    assert 'PARCELFORCE' in providers
    assert 'APC' in providers
    assert ParcelforceShippingProvider in providers.values()
    assert APCShippingProvider in providers.values()


def test_providers(provider_type):
    assert issubclass(provider_type, ShippingProvider)


