from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence, Literal

from dotenv import load_dotenv

from resources.shared import AddressRoughDC

load_dotenv()


@dataclass
class GoodsInfo:
    goods_value: int
    goods_description: str
    premium_insurance: bool


@dataclass
class Item:
    type: Literal['ALL']
    weight: int
    length: int
    width: int
    height: int
    value: int

    def available_services_dict(self) -> dict:
        return {
            "Type": self.type,
            "Weight": str(self.weight),
            "Length": str(self.length),
            "Width": str(self.width),
            "Height": str(self.height),
            "Value": str(self.value)
        }


@dataclass
class ShipmentDetails:
    number_of_pieces: int
    items: Sequence[Item]


@dataclass
class ServiceRequest:
    collection_date: datetime.date
    ready_at: datetime.time
    closed_at: datetime.time
    collection: AddressRoughDC
    delivery: AddressRoughDC
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails
    delivery_group: Optional[str] = None


def get_item(item_obj: Item) -> dict:
    return {
        "Type": item_obj.type,
        "Weight": str(item_obj.weight),
        "Length": str(item_obj.length),
        "Width": str(item_obj.width),
        "Height": str(item_obj.height),
        "Value": str(item_obj.value)
    }


def get_items_dict(items: Sequence[Item]) -> dict:
    return {
        "Item": _.available_services_dict()
        for _ in items
    }
