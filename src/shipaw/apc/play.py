import base64
import os
from datetime import date, time, timedelta

import httpx
from enum import StrEnum
import dotenv

from shipaw.apc.available_services.avail_request import ServiceRequest

dotenv.load_dotenv(r'C:\prdev\repos\amdev\shipaw\apc.env')
# class TrainingEndPoint(StrEnum):
#     BASE = 'https://apc-training.hypaship.com/api/3.0/'
#     SERVICE = BASE + 'ServiceAvailability'


EPT = 'https://apc.hypaship.com/api/3.0/ServiceAvailability.json'


email_password = f'{os.getenv('EMAIL')}:{os.getenv('PASSWORD')}'
encoded_credentials = base64.b64encode(email_password.encode('utf-8'))

headers = {
    'remote-user': f'Basic {encoded_credentials}',
    'Content-Type': 'application/json',
}

req = {
    'Orders': {
        'Order': {
            'CollectionDate': '12/09/2025',
            'ReadyAt': '09:00',
            'ClosedAt': '18:00',
            'Collection': {'PostalCode': 'WS11 8LD', 'CountryCode': 'GB'},
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

req2 = ServiceRequest(
    collection_date=date.today() + timedelta(days=1),
    ready_at=time(hour=9),
    closed_at=time(hour=17),



)
if __name__ == '__main__':
    res = httpx.post(EPT, headers=headers, json=req, timeout=30)
    # res.raise_for_status()

    print(res.status_code)
    ...