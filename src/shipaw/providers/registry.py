from shipaw.providers.parcelforce.provider import ParcelforceShippingProvider
from shipaw.providers.providers import ShippingProvider
from shipaw.providers.apc.provider import APCShippingProvider

PROVIDER_TYPE_REGISTER: dict[str, type[ShippingProvider]] = {
    'APC': APCShippingProvider,
    'PARCELFORCE': ParcelforceShippingProvider,
}