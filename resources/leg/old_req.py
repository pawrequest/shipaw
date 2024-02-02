# from datetime import datetime
# from typing import Protocol, Sequence
#
# from resources.shared import AddressRough
#
#
# class GoodsInfo(Protocol):
#     goods_value: int
#     goods_description: str
#     premium_insurance: bool
#
#
# class ItemSingleProtocol(Protocol):
#     type: str
#     weight: int
#     length: int
#     width: int
#     height: int
#     value: int
#
#
# class ItemProtocol(Protocol):
#     # plural names are crazy in this API
#     item: Sequence[ItemSingleProtocol]
#
#
# class ShipmentDetails(Protocol):
#     number_of_pieces: int
#     items: ItemProtocol
#
#
# class Order(Protocol):
#     collection_date: datetime.date
#     ready_at: datetime.time
#     closed_at: datetime.time
#     delivery_group: str
#     collection: AddressRough
#     delivery: AddressRough
#     goods_info: GoodsInfo
#     shipment_details: ShipmentDetails
#
#
# # class AvailableServices(Protocol):
# #     Orders: Sequence[Order]
#
# available_services_request_json = {
#     "Orders": {
#         "Order": {
#             "CollectionDate": "04/04/2018",
#             "ReadyAt": "09:00",
#             "ClosedAt": "18:00",
#             "DeliveryGroup": "NS Services",
#             "Collection": {
#                 "PostalCode": "WS11 8LD",
#                 "CountryCode": "GB"
#             },
#             "Delivery": {
#                 "PostalCode": "M17 1WA",
#                 "CountryCode": "GB"
#             },
#             "GoodsInfo": {
#                 "GoodsValue": "1",
#                 "GoodsDescription": ".....",
#                 "PremiumInsurance": "False"
#             },
#             "ShipmentDetails": {
#                 "NumberofPieces": "1",
#                 "Items": {
#                     "Item": {
#                         "Type": "ALL",
#                         "Weight": "1",
#                         "Length": "1",
#                         "Width": "1",
#                         "Height": "1",
#                         "Value": "1"
#                     }
#                 }
#             }
#         }
#     }
# }
#
#
# def make_request(order: Order):
#     return {
#         "Orders": {
#             "Order": {
#                 "CollectionDate": order.collection_date.strftime('%d/%m/%Y'),
#                 "ReadyAt": order.ready_at.strftime('%H:%M'),
#                 "ClosedAt": order.closed_at.strftime('%H:%M'),
#                 "DeliveryGroup": order.delivery_group,
#
#                 "Collection": {
#                     "PostalCode": order.collection.postcode,
#                     "CountryCode": order.collection.country_code
#                 },
#
#                 "Delivery": {
#                     "PostalCode": order.delivery.postcode,
#                     "CountryCode": order.delivery.country_code
#                 },
#                 "GoodsInfo": {
#                     "GoodsValue": order.goods_info.goods_value,
#                     "GoodsDescription": order.goods_info.goods_description,
#                     "PremiumInsurance": False
#                 },
#                 "ShipmentDetails": {
#                     "NumberofPieces": order.shipment_details.number_of_pieces,
#                     "Items": {
#                         "Item": {
#                             "Type": order.shipment_details.items.item.type,
#                             "Weight": order.shipment_details.items.item.weight,
#                             "Length": order.shipment_details.items.item.length,
#                             "Width": order.shipment_details.items.item.width,
#                             "Height": order.shipment_details.items.item.height,
#                             "Value": order.shipment_details.items.item.Value
#                         }
#                     }
#                 }
#             }
#         }
#     }
#
#
#