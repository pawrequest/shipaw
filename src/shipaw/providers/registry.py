from shipaw.providers.provider_abc import ShippingProvider

PROVIDER_TYPE_REGISTER: dict[str, type[ShippingProvider]] = {}
PROVIDER_REGISTER: dict[str, ShippingProvider] = {}


def register_provider_type(cls):
    PROVIDER_TYPE_REGISTER[cls.name] = cls
    return cls


def register_provider_instance(instance: ShippingProvider):
    PROVIDER_REGISTER[instance.name] = instance
    return instance
