######################

from typing import List, Optional, Protocol, TypedDict

from shipr.resources.shared import MessagesProtocol


######################

class OrderHeader(TypedDict):
    AccountNumber: str
    Messages: MessagesProtocol


class MessageProtocol(Protocol):
    Code: str
    Description: str


class ContactProtocol(Protocol):
    PersonName: str
    PhoneNumber: str
    MobileNumber: Optional[str]
    Email: Optional[str]


class AddressProtocol(Protocol):
    CompanyName: str
    AddressLine1: str
    AddressLine2: str
    PostalCode: str
    City: str
    County: str
    CountryCode: str
    CountryName: str
    Contact: ContactProtocol
    Instructions: Optional[str]


class ItemProtocol(Protocol):
    ItemNumber: str
    TrackingNumber: str
    Type: str
    Weight: str
    Length: str
    Width: str
    Height: str
    Value: str
    Reference: str


class ItemsProtocol(Protocol):
    Item: ItemProtocol


class ShipmentDetailsProtocol(Protocol):
    NumberOfPieces: str
    TotalWeight: str
    VolumetricWeight: str
    Items: ItemsProtocol


class GoodsInfoProtocol(Protocol):
    GoodsValue: str
    GoodsDescription: str
    PremiumInsurance: str
    Fragile: str
    Security: str
    IncreasedLiability: str
    Premium: str
    NonConv: str


class DepotProtocol(Protocol):
    RequestDepot: str
    CollectingDepot: str
    DeliveryDepot: str
    Route: str
    IsScottish: str
    Zone: str
    Presort: Optional[str]


class RateProtocol(Protocol):
    Rate: str
    ExtraCharges: str
    FuelCharge: str
    InsuranceCharge: str
    Vat: str
    TotalCost: str
    Currency: str


class OrderProtocol(Protocol):
    Messages: MessageProtocol
    AccountNumber: Optional[List[str]]
    EntryType: str
    CollectionDate: str
    ReadyAt: str
    ClosedAt: str
    ProductCode: str
    RuleName: Optional[str]
    ItemOption: str
    OrderNumber: str
    WayBill: str
    Reference: str
    CustomReference1: Optional[str]
    CustomReference2: Optional[str]
    CustomReference3: Optional[str]
    AdultSignature: Optional[str]
    Depots: DepotProtocol
    Collection: AddressProtocol
    Delivery: AddressProtocol
    GoodsInfo: GoodsInfoProtocol
    ShipmentDetails: ShipmentDetailsProtocol
    Rates: RateProtocol


class OrderRespProtocol(Protocol):
    Messages: MessageProtocol
    AccountNumber: Optional[str]
    Order: OrderProtocol


#############
class OrderResponseSingleProtocol(Protocol):
    AccountNumber: str
    Messages: MessagesProtocol


class OrderResponse(Protocol):
    Orders: OrderResponseSingleProtocol


resp = {
    "Orders": {
        "AccountNumber": null,
        "Messages": {
            "Code": "SUCCESS",
            "Description": "SUCCESS"
        },
        "Order": {
            "Messages": {
                "Code": "SUCCESS",
                "Description": "SUCCESS"
            },
            "AccountNumber": [
                "ANC001",
                "ANC001"
            ],
            "EntryType": "API",
            "CollectionDate": "19/04/2018",
            "ReadyAt": "18:00",
            "ClosedAt": "18:30",
            "ProductCode": "ND16",
            "RuleName": null,
            "ItemOption": "Weight",
            "OrderNumber": "000000000149567219",
            "WayBill": "2018041910099660000599",
            "Reference": "TEST",
            "CustomReference1": null,
            "CustomReference2": null,
            "CustomReference3": null,
            "AdultSignature": null,
            "Depots": {
                "RequestDepot": "100",
                "CollectingDepot": "44",
                "DeliveryDepot": "53",
                "Route": "APC",
                "IsScottish": "true",
                "Zone": "Z",
                "Presort": null
            },
            "Collection": {
                "CompanyName": "APC API and Co",
                "AddressLine1": "National Sortation Centre",
                "AddressLine2": "Kingswood Lakeside",
                "PostalCode": "WS11 8LD",
                "City": "Cannock",
                "County": "Staffordshire",
                "CountryCode": "GB",
                "CountryName": "United Kingdom",
                "Contact": {
                    "PersonName": "Fred Smith",
                    "PhoneNumber": "01922702580",
                    "Email": null
                },
                "Instructions": null
            },
            "Delivery": {
                "CompanyName": "The Big Company Ltd",
                "AddressLine1": "Big Company House",
                "AddressLine2": "177 Big Street",
                "PostalCode": "M17 1WA",
                "City": "Sale",
                "County": "Cheshire",
                "CountryCode": "GB",
                "CountryName": "United Kingdom",
                "Contact": {
                    "PersonName": "Jack Fox",
                    "PhoneNumber": "08000280000",
                    "MobileNumber": null,
                    "Email": "api_support@apc-overnight.com"
                },
                "Instructions": "leave with neighbour"
            },
            "GoodsInfo": {
                "GoodsValue": "200",
                "GoodsDescription": ".....",
                "PremiumInsurance": "false",
                "Fragile": "false",
                "Security": "false",
                "IncreasedLiability": "false",
                "Premium": "false",
                "NonConv": "false"
            },
            "ShipmentDetails": {
                "NumberOfPieces": "1",
                "TotalWeight": "1",
                "VolumetricWeight": "1.96",
                "Items": {
                    "Item": {
                        "ItemNumber": "000000000149567219",
                        "TrackingNumber": "2018041910099660000599001",
                        "Type": "PARCEL",
                        "Weight": "1.000",
                        "Length": "32.000",
                        "Width": "23.000",
                        "Height": "16.000",
                        "Value": "200",
                        "Reference": "PartA"
                    }
                }
            },
            "Rates": {
                "Rate": "0.00",
                "ExtraCharges": "0.00",
                "FuelCharge": "0.00",
                "InsuranceCharge": "0.00",
                "Vat": "0.00",
                "TotalCost": "0.00",
                "Currency": "GBP"
            }
        }
    }
}

resp = {
    "Orders": {
        "AccountNumber": null,
        "Messages": {
            "Code": "SUCCESS",
            "Description": "SUCCESS"
        },
        "Order": {
            "Messages": {
                "Code": "SUCCESS",
                "Description": "SUCCESS"
            },
            "AccountNumber": [
                "ANC001",
                "ANC001"
            ],
            "EntryType": "API",
            "CollectionDate": "19/04/2018",
            "ReadyAt": "18:00",
            "ClosedAt": "18:30",
            "ProductCode": "ND16",
            "RuleName": null,
            "ItemOption": "Weight",
            "OrderNumber": "000000000149567219",
            "WayBill": "2018041910099660000599",
            "Reference": "TEST",
            "CustomReference1": null,
            "CustomReference2": null,
            "CustomReference3": null,
            "AdultSignature": null,
            "Depots": {
                "RequestDepot": "100",
                "CollectingDepot": "44",
                "DeliveryDepot": "53",
                "Route": "APC",
                "IsScottish": "true",
                "Zone": "Z",
                "Presort": null
            },
            "Collection": {
                "CompanyName": "APC API and Co",
                "AddressLine1": "National Sortation Centre",
                "AddressLine2": "Kingswood Lakeside",
                "PostalCode": "WS11 8LD",
                "City": "Cannock",
                "County": "Staffordshire",
                "CountryCode": "GB",
                "CountryName": "United Kingdom",
                "Contact": {
                    "PersonName": "Fred Smith",
                    "PhoneNumber": "01922702580",
                    "Email": null
                },
                "Instructions": null
            },
            "Delivery": {
                "CompanyName": "The Big Company Ltd",
                "AddressLine1": "Big Company House",
                "AddressLine2": "177 Big Street",
                "PostalCode": "M17 1WA",
                "City": "Sale",
                "County": "Cheshire",
                "CountryCode": "GB",
                "CountryName": "United Kingdom",
                "Contact": {
                    "PersonName": "Jack Fox",
                    "PhoneNumber": "08000280000",
                    "MobileNumber": null,
                    "Email": "api_support@apc-overnight.com"
                },
                "Instructions": "leave with neighbour"
            },
            "GoodsInfo": {
                "GoodsValue": "200",
                "GoodsDescription": ".....",
                "PremiumInsurance": "false",
                "Fragile": "false",
                "Security": "false",
                "IncreasedLiability": "false",
                "Premium": "false",
                "NonConv": "false"
            },
            "ShipmentDetails": {
                "NumberOfPieces": "1",
                "TotalWeight": "1",
                "VolumetricWeight": "1.96",
                "Items": {
                    "Item": {
                        "ItemNumber": "000000000149567219",
                        "TrackingNumber": "2018041910099660000599001",
                        "Type": "PARCEL",
                        "Weight": "1.000",
                        "Length": "32.000",
                        "Width": "23.000",
                        "Height": "16.000",
                        "Value": "200",
                        "Reference": "PartA"
                    }
                }
            },
            "Rates": {
                "Rate": "0.00",
                "ExtraCharges": "0.00",
                "FuelCharge": "0.00",
                "InsuranceCharge": "0.00",
                "Vat": "0.00",
                "TotalCost": "0.00",
                "Currency": "GBP"
            }
        }
    }
}
