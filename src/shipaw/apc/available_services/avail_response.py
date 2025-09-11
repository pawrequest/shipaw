from typing import Protocol

from resources.shared import AddressRough, MessagesProtocol


class OrderResponse(Protocol):
    Collection: AddressRough
    Delivery: AddressRough


class Service(Protocol):
    Carrier: str
    ServiceName: str
    ProductCode: str
    MinTransitDays: str
    MaxTransitDays: str
    Tracked: str
    Signed: str
    MaxCompensation: str
    MaxItemLength: str
    MaxItemWidth: str
    MaxItemHeight: str
    ItemType: str
    DeliveryGroup: str
    CollectionDate: str
    EstimatedDeliveryDate: str
    LatestBookingDateTime: str
    Rate: str
    ExtraCharges: str
    FuelCharge: str
    InsuranceCharge: str
    Vat: str
    TotalCost: str
    Currency: str
    VolumetricWeight: str
    WeightUnit: str


class ServiceAvailability(Protocol):
    AccountNumber: str
    Messages: MessagesProtocol
    Order: OrderResponse


response = {
    "ServiceAvailability": {
        "AccountNumber": "00000000",
        "Messages": {
            "Code": "SUCCESS",
            "Description": "SUCCESS"
        },
        "Order": {
            "Collection": {
                "PostalCode": "WS11 8LD",
                "CountryCode": "GB"
            },
            "Delivery": {
                "PostalCode": "M17 1WA",
                "CountryCode": "GB"
            }
        },
        "Services": {
            "Service": [
                {
                    "Carrier": "APC OVERNIGHT",
                    "ServiceName": "0900 COURIER PACK",
                    "ProductCode": "APCCP09",
                    "MinTransitDays": "1",
                    "MaxTransitDays": "1",
                    "Tracked": "false",
                    "Signed": "false",
                    "MaxCompensation": "15000.00",
                    "MaxItemLength": "60",
                    "MaxItemWidth": "45",
                    "MaxItemHeight": "45",
                    "ItemType": "PACK",
                    "DeliveryGroup": "NS Services",
                    "CollectionDate": "04/04/2018",
                    "EstimatedDeliveryDate": "05/04/2018",
                    "LatestBookingDateTime": "04/04/2018 12:00",
                    "Rate": "0.00",
                    "ExtraCharges": "0.00",
                    "FuelCharge": "0.00",
                    "InsuranceCharge": "0.00",
                    "Vat": "0.00",
                    "TotalCost": "0.00",
                    "Currency": "GBP",
                    "VolumetricWeight": "0.00",
                    "WeightUnit": "KG"
                }

            ]
        }
    }
}
