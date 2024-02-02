from __future__ import annotations

from datetime import date, time
from typing import Literal, Sequence

from dotenv import load_dotenv

from shipr.apc.available_services.apc_abc import BaseRequest

load_dotenv()


class GoodsInfo(BaseRequest):
    goods_value: int
    goods_description: str
    premium_insurance: bool


class Item(BaseRequest):
    weight: int
    length: int
    width: int
    height: int
    value: int
    type: Literal['ALL'] = 'ALL'


class ShipmentDetails(BaseRequest):
    number_of_pieces: int
    items: Sequence[Item]


class Order(BaseRequest):
    collection_date: date
    ready_at: time
    closed_at: time
    collection: AddressRoughDC
    delivery: AddressRoughDC
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails


class AddressRoughDC(BaseRequest):
    postcode: str
    country_code: str
