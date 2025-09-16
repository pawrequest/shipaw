import httpx
import pytest

from shipaw.apc.shared import EndPoints, get_headers
from test_apc import TEST_DATE


@pytest.fixture
def anorder():
    yield {
        'Orders': {
            'Order': {
                'CollectionDate': TEST_DATE,
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


@pytest.fixture
def anorder2():
    yield {
        'Orders': {
            'Order': {
                'CollectionDate': TEST_DATE,
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
                    'NumberOfPieces': 2,
                    'Items': {
                        'Item': [
                            {
                                'Type': 'ALL',
                                'Weight': 10,
                                'Length': 60,
                                'Width': 30,
                                'Height': 30,
                                'Reference': 'Test Reference',
                            },
                            {
                                'Type': 'ALL',
                                'Weight': 10,
                                'Length': 60,
                                'Width': 30,
                                'Height': 30,
                                'Reference': 'Test Reference',
                            },
                        ]
                    },
                },
            }
        }
    }


#
def test_2(anorder2):
    # req_json = req2.model_dump(by_alias=True, mode='json')
    req_json = anorder2
    res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=req_json)
    res.raise_for_status()
    res_json = res.json()
    assert res_json['Orders']['Order']['Collection']
    ...


#