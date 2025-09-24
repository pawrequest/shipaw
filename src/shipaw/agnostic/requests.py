import base64
from typing import Annotated

from pydantic import StringConstraints

from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.ship_types import ProviderName
from shipaw.agnostic.shipment import Shipment


class Authentication(ShipawBaseModel):
    # todo SecretStr!!!!
    user_name: Annotated[str, StringConstraints(max_length=80)]
    password: Annotated[str, StringConstraints(max_length=80)]


class BaseRequest(ShipawBaseModel):
    authentication: Authentication


def encode_b64_str(s: str) -> str:
    return base64.b64encode(s.encode('utf8')).decode('utf8')


class ShipmentRequestAgnost(ShipawBaseModel):
    shipment: Shipment
    provider_name: ProviderName

    @property
    def provider(self) -> type[ShippingProvider]:
        match self.provider_name:
            case 'PARCELFORCE':
                from shipaw.parcelforce.provider import ParcelforceProvider

                return ParcelforceProvider
            case 'APC':
                from shipaw.apc.provider import APCProvider

                return APCProvider
            case _:
                raise ValueError(f'Unknown provider: {self.provider_name}')

