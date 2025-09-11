import json
from datetime import date, timedelta

import dotenv
import httpx
import pytest

from shipaw.apc.address import Address, Contact
from shipaw.apc.services import ServiceSpec
from shipaw.apc.shared import APC_ENV, EndPoints, get_headers
from shipaw.apc.shipment import GoodsInfo, Item, Order, Orders, ShipmentDetails

dotenv.load_dotenv(APC_ENV)


contact = Contact(person_name='Test Contact name', phone_number='07666666666', email='sdkjgksdjgfbn@ksdhjfgbkdsbgf.com')

del_addr = Address(
    postal_code='DA16 3HU',
    company_name='Test Company',
    address_line_1='25 Bennet Close',
    city='Welling',
    county='Kent',
    contact=contact,
)
ship_details = ShipmentDetails(
    number_of_pieces=1,
    items=[
        Item(
            weight=10,
            length=60,
            height=30,
            width=30,
            reference='Test Reference',
        )
    ],
)

req2 = Orders(
    order=Order(
        collection_date=date.today() + timedelta(days=1),
        reference='Test Reference',
        delivery=del_addr,
        goods_info=GoodsInfo(),
        shipment_details=ship_details,
    )
)

req = {
    'Orders': {
        'Order': {
            'CollectionDate': '12/09/2025',
            'ReadyAt': '09:00',
            'ClosedAt': '18:00',
            'ProductCode': 'ND16',
            'Reference': 'Test',
            # 'Collection': {'PostalCode': 'WS11 8LD', 'CountryCode': 'GB'},
            'Delivery': {'PostalCode': 'M17 1WA', 'CountryCode': 'GB'},
            'GoodsInfo': {'GoodsValue': '1', 'GoodsDescription': '.....', 'PremiumInsurance': 'False'},
            'ShipmentDetails': {
                'NumberofPieces': '1',
                'Items': {
                    'Item': {'Type': 'ALL', 'Weight': '1', 'Length': '1', 'Width': '1', 'Height': '1', 'Value': '1'}
                },
            },
        }
    }
}

anorder = {
    'Orders': {
        'Order': {
            'CollectionDate': '12/09/2025',
            'ReadyAt': '09:00',
            'ClosedAt': '17:00',
            'ProductCode': 'ND16',
            'Reference': 'Test Reference',
            'Delivery': {
                'PostalCode': 'DA16 3HU',
                'CountryCode': 'GB',
                'CompanyName': 'Test Company',
                'AddressLine1': '25 Bennet Close',
                'City': 'Welling',
                'County': 'Kent',
                'Contact': {
                    'PersonName': 'Test Contact name',
                    'PhoneNumber': '07666666666',
                    'Email': 'sdkjgksdjgfbn@ksdhjfgbkdsbgf.com',
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


def test_service_avail():
    res = httpx.post(EndPoints.SERVICES, headers=get_headers(), json=req, timeout=30)
    res.raise_for_status()
    avail = res.json()['ServiceAvailability']['Services']['Service']
    services = [ServiceSpec(**_) for _ in avail]
    nd = [_ for _ in services if _.ProductCode == 'APCND12']
    assert nd


def test_2():
    # req_json = {"Orders": req2.model_dump(by_alias=True)}
    req_json = req2.model_dump_json(by_alias=True)
    req_json = f'{{"Orders": {req_json}}}'
    # req_json = req2.model_dump_json(by_alias=True)
    order = json.dumps(anorder)
    res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=anorder)
    ...