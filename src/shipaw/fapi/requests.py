import base64
import uuid
from typing import Annotated

from pydantic import Field, StringConstraints

from shipaw.models.address import Address, Contact
from shipaw.models.base import ShipawBaseModel
from shipaw.models.shipment import Shipment
from shipaw.models.provider import PROVIDER_REGISTER, ShippingProvider


class Authentication(ShipawBaseModel):
    # todo SecretStr!!!!
    user_name: Annotated[str, StringConstraints(max_length=80)]
    password: Annotated[str, StringConstraints(max_length=80)]


def encode_b64_str(s: str) -> str:
    return base64.b64encode(s.encode('utf8')).decode('utf8')


class ShipmentRequest(ShipawBaseModel):
    id: uuid.UUID = uuid.uuid4()
    shipment: Shipment
    provider_name: str
    context: dict = Field(default_factory=dict)
    # handler: Callable | None = None

    @property
    def provider(self) -> ShippingProvider:
        if not self.provider_name:
            raise ValueError('Provider name is not set')
        if self.provider_name not in PROVIDER_REGISTER:
            raise ValueError(f'Unknown provider: {self.provider_name}')
        return PROVIDER_REGISTER[self.provider_name]()


class AddressRequest(ShipawBaseModel):
    postcode: str
    address: Address | None = None
    contact: Contact | None = None
