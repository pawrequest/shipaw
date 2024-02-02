from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Sequence
import pawsupport as ps
from dotenv import load_dotenv

from resources.shared import AddressRoughDC
from shipr.apc.available_services.v2 import RequestDictMixin, BaseRequest

load_dotenv()


@dataclass
class GoodsInfo:
    goods_value: int
    goods_description: str
    premium_insurance: bool


@dataclass
class Item:
    weight: int
    length: int
    width: int
    height: int
    value: int
    type: Literal['ALL'] = 'ALL'

    @property
    def available_services_dict(self) -> dict:
        return {
            "Type": self.type,
            "Weight": str(self.weight),
            "Length": str(self.length),
            "Width": str(self.width),
            "Height": str(self.height),
            "Value": str(self.value)
        }

    @property
    def item_dict(self) -> dict:
        return {
            "Item": self.available_services_dict
        }

    @staticmethod
    def items_dict_many(items: Sequence['Item']) -> dict:
        return {
            'Items':
                {
                    "Item": item.available_services_dict
                    for item in items
                }
        }


@dataclass
class ShipmentDetails:
    number_of_pieces: int
    items: Sequence[Item]


@dataclass
class ServiceRequest(RequestDictMixin, BaseRequest):
    collection_date: datetime.date
    ready_at: datetime.time
    closed_at: datetime.time
    collection: AddressRoughDC
    delivery: AddressRoughDC
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails

    # delivery_group: Optional[str] = None

    def make_avail_serv_dict(self: ServiceRequest) -> dict:
        return {
            "Orders": {
                "Order": {
                    "CollectionDate": self.collection_date.strftime('%d/%m/%Y'),
                    "ReadyAt": self.ready_at.strftime('%H:%M'),
                    "ClosedAt": self.closed_at.strftime('%H:%M'),
                    # "DeliveryGroup": order_req.delivery_group,
                    "Collection": {
                        "PostalCode": self.collection.postcode,
                        "CountryCode": self.collection.country_code
                    },
                    "Delivery": {
                        "PostalCode": self.delivery.postcode,
                        "CountryCode": self.delivery.country_code
                    },
                    "GoodsInfo": {
                        "GoodsValue": str(self.goods_info.goods_value),
                        "GoodsDescription": self.goods_info.goods_description,
                        "PremiumInsurance": str(self.goods_info.premium_insurance).title()
                    },
                    "ShipmentDetails": {
                        "NumberofPieces": str(self.shipment_details.number_of_pieces),
                        **Item.items_dict_many(self.shipment_details.items)

                    }
                }
            }
        }


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
        "Item": item.available_services_dict
        for item in items
    }
