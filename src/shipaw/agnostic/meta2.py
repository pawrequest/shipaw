from typing import Protocol, runtime_checkable

from agnostic.shipment import Shipment


class ConvertableShipment(Protocol):
    @classmethod
    def from_generic(cls, shipment: Shipment) -> 'ConvertableShipment': ...
    def to_generic(self) -> Shipment: ...


ShipmentType = ConvertableShipment


@runtime_checkable
class ProviderInterface[ShipmentType](Protocol):
    name: str
    shipment_type: type[ShipmentType]

    def book_shipment(self, shipment: dict) -> str: ...
    def get_label_content(self, shipment_num: str) -> bytes: ...

    # def import_shipment(self, shipment: Shipment) -> ShipmentType: ...
    # def export_shipment(self, shipment: ShipmentType) -> Shipment: ...


def use_provider(provider: ProviderInterface) -> None:
    print(provider.name)
    provider.book_shipment({'key': 'value'})
    provider.get_label_content('12345')


class AProvider:
    name = 'INVALID'
    shipment_type = ShipmentType

    def book_shipment(self, shipment: dict) -> str:
        return 42

    def get_label_content(self, shipment_num: str) -> bytes:
        return b'label content'

    # def import_shipment(self, shipment: Shipment) -> ShipmentType:
    #     return shipment.to_generic()


use_provider(AProvider())


PROVIDER_REGISTER: dict[str, ProviderInterface] = {}


def register_provider(cls: type[ProviderInterface]) -> type[ProviderInterface]:
    inst = cls()
    if not isinstance(inst, ProviderInterface):
        raise TypeError('Class does not implement ProviderInterface')
    PROVIDER_REGISTER[cls.name] = inst
    return cls

