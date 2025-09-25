from datetime import date, time
from typing import Literal, Self, Sequence

from pydantic import model_validator, Field

from shipaw.agnostic.address import FullContact
from shipaw.agnostic.ship_types import ConvertMode, ShipDirection, pydantic_export
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.apc.address import Address, Contact
from shipaw.apc.services import APCServiceDict
from shipaw.apc.shared import APCBaseModel
from loguru import logger


class Item(APCBaseModel):
    type: Literal['ALL'] = 'ALL'
    weight: float | None = 5
    length: float | None = None
    width: float | None = None
    height: float | None = None
    reference: str | None = None


class Items(APCBaseModel):
    item: Sequence[Item] = Field(default_factory=list)


class ShipmentDetails(APCBaseModel):
    number_of_pieces: int
    items: Items | None = None

    @model_validator(mode='after')
    def check_items(self):
        if not self.items:
            self.items = Items(item=[Item() for _ in range(self.number_of_pieces)])
            logger.debug('Auto-filled items in ShipmentDetails')
        return self


class GoodsInfo(APCBaseModel):
    goods_value: str = '1000'
    goods_description: str = 'Radios'
    fragile: bool = False
    security: bool = False
    increased_liability: bool = False


class Order(APCBaseModel):
    collection_date: date
    ready_at: time = time(hour=9)
    closed_at: time = time(hour=17)
    product_code: str
    reference: str
    collection: Address | None = None
    delivery: Address
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails


class Orders(APCBaseModel):
    order: Order


class Shipment(APCBaseModel):
    orders: Orders

    def to_generic(self) -> ShipmentAgnost:
        order = self.orders.order
        contact = order.delivery.contact.to_generic()
        address = order.delivery.to_generic()

        return ShipmentAgnost(
            service=APCServiceDict[order.product_code],
            shipping_date=order.collection_date,
            reference=order.reference,
            recipient=FullContact(address=address, contact=contact),
            boxes=order.shipment_details.number_of_pieces,
            direction=ShipDirection.INBOUND if order.collection is not None else ShipDirection.OUTBOUND,
        )

    @classmethod
    def from_generic(cls, shipment: ShipmentAgnost) -> Self:
        # todo handle direction
        if shipment.direction not in [ShipDirection.INBOUND, ShipDirection.OUTBOUND]:
            raise NotImplementedError('APCProvider does not support DROPOFF shipments')

        service_code = APCServiceDict[shipment.service]
        ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

        order = Order(
            collection_date=shipment.shipping_date,
            product_code=service_code,
            reference=shipment.reference,
            delivery=Address.from_generic(shipment.recipient.address, shipment.recipient.contact),
            collection=Address.from_generic(shipment.sender.address, shipment.sender.contact)
            if shipment.sender
            else None,
            goods_info=GoodsInfo(),
            shipment_details=ship_deets,
        )
        return Shipment(orders=Orders(order=order))

