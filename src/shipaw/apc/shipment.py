from datetime import date, time
from typing import Literal, Sequence

from pydantic import model_validator

from shipaw.apc.address import Address
from shipaw.apc.shared import APCBaseModel


class Item(APCBaseModel):
    type: Literal['ALL'] = 'ALL'
    weight: float | None = 1
    length: float | None = None
    width: float | None = None
    height: float | None = None
    reference: str | None = None


class Items(APCBaseModel):
    item: Sequence[Item]


class ShipmentDetails(APCBaseModel):
    number_of_pieces: int
    items: Items | None = None

    @model_validator(mode='after')
    def check_items(self):
        if self.items is None:
            self.items = Items(item=[Item() for _ in range(self.number_of_pieces)])
        return self


class GoodsInfo(APCBaseModel):
    goods_value: str = 1000
    goods_description: str = 'Radios'
    fragile: str = False
    security: str = False
    increased_liability: str = False


# def boxes_to_details_dict(boxes: int):
#     items = Items.basic(boxes)
#     res = ShipmentDetails(number_of_pieces=boxes, items=items)
#     return res


class Order(APCBaseModel):
    # model_config = ConfigDict(
    # json_encoders=
    # )
    collection_date: date
    ready_at: time = time(hour=9)
    closed_at: time = time(hour=17)
    product_code: str
    reference: str
    collection: Address | None = None
    delivery: Address
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails
    #
    # def export_dict(self) -> dict:
    #     return {'Orders': {'Order': self.model_dump(mode='json', by_alias=True)}}

    # def model_dump(self, *args, **kwargs) -> dict:
    #     return {'Orders': {'Order': super().model_dump(*args, **kwargs)}}


#
# def serial_ship(v):
#     return {'Orders': {'Order': v.model_dump(mode='json')}}

#
# class APCShipment(APCBaseModel):
#     model_config = ConfigDict(json_encoders={Order: serial_ship})
#     order: Order
#
#     def export_dict(self) -> dict:
#         return {'Orders': {'Order': self.order.model_dump(mode='json')}}


