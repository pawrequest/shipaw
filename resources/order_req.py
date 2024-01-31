from typing import Optional, Protocol, Sequence


class ContactProtocol(Protocol):
    person_name: str
    phone_number: str
    email: Optional[str]


class AddressProtocol(Protocol):
    company_name: str
    address_line_1: str
    address_line_2: str
    postal_code: str
    city: str
    county: str
    country_code: str
    contact: ContactProtocol


class AddressDeliveryProtocol(AddressProtocol):
    instructions: str


class ItemSingleProtocol(Protocol):
    type: str
    weight: str
    length: str
    width: str
    height: str
    reference: str


class ShipmentDetailsProtocol(Protocol):
    number_of_pieces: str
    items: Sequence[ItemSingleProtocol]


class GoodsInfoProtocol(Protocol):
    goods_value: str
    goods_description: str
    fragile: str
    security: str
    increased_liability: str


class OrderProtocol(Protocol):
    collection_date: str
    ready_at: str
    closed_at: str
    product_code: str
    reference: str
    collection: AddressProtocol
    delivery: AddressDeliveryProtocol
    goods_info: GoodsInfoProtocol
    shipment_details: ShipmentDetailsProtocol


class OrdersProtocol(Protocol):
    order: OrderProtocol


OrdersJson = {
    "Order": {
        "CollectionDate": "01\/03\/2018",
        "ReadyAt": "18:00",
        "ClosedAt": "18:30",
        "ProductCode": "ND16",
        "Reference": "TEST",
        "Collection": {
            "CompanyName": "APC API and Co",
            "AddressLine1": "National Sortation Centre",
            "AddressLine2": "Kingswood Lakeside",
            "PostalCode": "WS11 8LD",
            "City": "Cannock",
            "County": "Staffordshire",
            "CountryCode": "GB",
            "Contact": {
                "PersonName": "Fred Smith",
                "PhoneNumber": "01922 700080",
                "Email": null
            },
        },
        "Delivery": {
            "CompanyName": "The Big Company Ltd",
            "AddressLine1": "Big Company House",
            "AddressLine2": "177 Big Street",
            "PostalCode": "M17 1WA",
            "City": "Sale",
            "County": "Cheshire",
            "CountryCode": "GB",
            "Contact": {
                "PersonName": "Jack Jones",
                "PhoneNumber": "0800 0000000",
                "Email": "api_support@apc-overnight.com"
            },
            "Instructions": "Leave with neighbour"
        },
        "GoodsInfo": {
            "GoodsValue": "20",
            "GoodsDescription": ".....",
            "Fragile": "false",
            "Security": "false",
            "IncreasedLiability": "false"
        },
        "ShipmentDetails": {
            "NumberOfPieces": "1",
            "Items": {
                "Item": {
                    "Type": "ALL",
                    "Weight": "1",
                    "Length": "32",
                    "Width": "23",
                    "Height": "16",
                    "Reference": "PartA"
                }
            }
        }
    }
}
