from datetime import date, datetime, time
from typing import Literal, Sequence

from pydantic import ConfigDict, field_validator, model_validator

from shipaw.agnostic.agnost import Shipment
from shipaw.apc.address import Address, AddressDelivery, apc_address
from shipaw.apc.services import ProductCode
from shipaw.apc.shared import APCBaseModel, apc_date


class Item(APCBaseModel):
    type: Literal['ALL'] = 'ALL'
    weight: float | None = 1
    length: float | None = None
    width: float | None = None
    height: float | None = None
    reference: str | None = None

    # @property
    # def formatted_items(self):
    #     return {'Item': self.model_dump()}
    #
    # def model_dump(self, **kwargs):
    #     # Override the dump method to include the formatted structure
    #     return self.formatted_items


class Items(APCBaseModel):
    item: Sequence[Item]

    @classmethod
    def basic(cls, boxes: int):
        return cls(item=[Item() for _ in range(boxes)])

    # @model_validator(mode='after')
    # def itemiser(self):
    #     self.items = {'Item': item.model_dump() if isinstance(item, Item) else item for item in self.items}
    #
    #     # self.items = {'Item': item.model_dump() for item in self.items if isinstance(item, Item) else item}
    #     return self



class ShipmentDetails(APCBaseModel):
    number_of_pieces: int
    items: Items


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
    product_code: ProductCode = ProductCode.NEXT_DAY16
    reference: str
    collection: Address | None = None
    delivery: Address
    goods_info: GoodsInfo
    shipment_details: ShipmentDetails

    def export_dict(self) -> dict:
        return {'Orders': {'Order': self.model_dump(mode='json', by_alias=True)}}


def serial_ship(v):
    return {'Orders': {'Order': v.model_dump(mode='json')}}


class APCShipment(APCBaseModel):
    model_config = ConfigDict(json_encoders={Order: serial_ship})
    order: Order

    def export_dict(self) -> dict:
        return {'Orders': {'Order': self.order.model_dump(mode='json')}}


def apc_shipment(shipment: Shipment) -> Order:
    service_code = shipment.service.code
    if service_code not in ProductCode.__members__.values():
        raise ValueError(f'Incorrect APC Product Code: {service_code}')
    service_code = ProductCode(service_code)
    ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes, items=Items.basic(shipment.boxes))

    order = Order(
        collection_date=shipment.shipping_date,
        product_code=service_code,
        reference=shipment.reference,
        delivery=apc_address(shipment.recipient_address, shipment.recipient_contact),
        goods_info=GoodsInfo(),
        shipment_details=ship_deets,
    )
    return order


def apc_shipment_dict(shipment: Shipment) -> dict:
    service_code = shipment.service
    if service_code not in ProductCode.__members__:
        raise ValueError('Incorrect Product Code')
    ship_dict = {
        'Orders': {
            'Order': {
                'CollectionDate': apc_date(shipment.shipping_date),
                'ReadyAt': '09:00',
                'ClosedAt': '17:00',
                'ProductCode': service_code,
                'Reference': ', '.join(shipment.references),
                'Delivery': {
                    'PostalCode': shipment.recipient_address.postcode,
                    'CountryCode': 'GB',
                    'CompanyName': shipment.recipient_contact.business_name,
                    'AddressLine1': shipment.recipient_address.address_lines[0],
                    'AddressLine2': ', '.join(shipment.recipient_address[1:]),
                    'City': shipment.recipient_address.town,
                    # 'County': 'Kent',
                    'Contact': {
                        'PersonName': shipment.recipient_contact.contact_name,
                        'PhoneNumber': shipment.recipient_contact.mobile_phone,
                        'MobileNumber': shipment.recipient_contact.mobile_phone,
                        'Email': shipment.recipient_contact.email_address,
                    },
                },
                'GoodsInfo': {
                    'GoodsValue': 1000,
                    'GoodsDescription': 'Radios',
                },
                'ShipmentDetails': {
                    'NumberOfPieces': 1,
                    'Items': {
                        'Item': {
                            'Type': 'ALL',
                            'Weight': 10,
                            'Length': 60,
                            'Width': 30,
                            'Height': 30,
                            'Reference': 'Test Reference',
                        },
                    },
                },
            }
        }
    }
