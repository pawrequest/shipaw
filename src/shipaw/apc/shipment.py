from datetime import date, datetime, time
from typing import Literal, Sequence

from shipaw.apc.address import Address, AddressDelivery
from shipaw.apc.shared import APCBaseModel


class Item(APCBaseModel):
    type: Literal['ALL'] = 'ALL'
    weight: float
    length: float
    width: float
    height: float
    reference: str


class ShipmentDetails(APCBaseModel):
    number_of_pieces: int
    items: Sequence[Item]


class GoodsInfo(APCBaseModel):
    goods_value: str = 1000
    goods_description: str = 'Radios'
    fragile: str = False
    security: str = False
    increased_liability: str = False


class Order(APCBaseModel):
    collection_date: date
    ready_at: time = time(hour=9)
    closed_at: time = time(hour=17)
    product_code: str = 'ND16'
    reference: str
    collection: Address | None = None
    delivery: Address
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails


class Orders(APCBaseModel):
    order: Order


class OrderCollection(APCBaseModel):
    orders: Orders
