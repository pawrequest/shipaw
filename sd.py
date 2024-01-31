str_j = {
    "Orders": {
        "Order": {
            "CollectionDate": "03/02/2024",
            "ReadyAt": "09:00",
            "ClosedAt": "18:00",
            "DeliveryGroup": null,
            "Collection": {
                "PostalCode": "NW6 4TE", "CountryCode": "GB"
            },
            "Delivery": {
                "PostalCode": "M17 1WA", "CountryCode": "GB"
            },
            "GoodsInfo": {
                "GoodsValue": 100, "GoodsDescription": "description", "PremiumInsurance": "False"
            },
            "ShipmentDetails": {
                "NumberofPieces": 1, "Items": {
                    "Item": {
                        "Type": "an item", "Weight": 12, "Length": 600, "Width": 400, "Height": 200,
                        "Value": 100
                    }
                }
            }
        }
    }
}

fail = {
    "Orders": {
        "Order": {
            "CollectionDate": "03/02/2024",
            "ReadyAt": "09:00",
            "ClosedAt": "18:00",
            "Collection": {
                "PostalCode": "NW6 4TE", "CountryCode": "GB"},
            "Delivery": {
                "PostalCode": "M17 1WA", "CountryCode": "GB"},
            "GoodsInfo": {
                "GoodsValue": 100,
                "GoodsDescription": "description",
                "PremiumInsurance": "False"
            }, "ShipmentDetails": {
                "NumberofPieces": 1, "Items": {
                    "Item": {
                        "Type": "an item", "Weight": 12, "Length": 600, "Width": 400, "Height": 200,
                        "Value": 100
                    }
                }
            }
        }
    }
}
