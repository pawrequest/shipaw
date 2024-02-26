import base64
import json
import os

from aiohttp import ClientSession

from shipr.apc.available_services.avail_request_v2 import Item, Order


def encode_b64(s: str) -> str:
    s_b = s.encode("ascii")
    base64_b = base64.b64encode(s_b)
    base64_s = base64_b.decode("ascii")
    return base64_s


def get_remote_user(login, password) -> str:
    usr_str = f'{login}:{password}'
    usr_str_encoded = encode_b64(usr_str)
    return f'Basic {usr_str_encoded}'


def get_headers() -> dict:
    usr = os.environ.get('APC_LOGIN')
    pwd = os.environ.get('APC_PASSWORD')
    res = {
        'Content-Type': 'application/json',
        'remote-user': get_remote_user(usr, pwd)
    }
    return res


async def request_from_dict(url, req_dict: dict, session=None) -> dict:
    session = session or ClientSession()
    req_json = json.dumps(req_dict)

    async with session:
        async with session.post(
                url=url,
                headers=get_headers(),
                data=req_json
        ) as response:
            response_txt = await response.text()
            response_json = json.loads(response_txt)
            return response_json


def make_avail_serv_dict(order_req: Order) -> dict:
    return {
        "Orders": {
            "Order": {
                "CollectionDate": order_req.collection_date.strftime('%d/%m/%Y'),
                "ReadyAt": order_req.ready_at.strftime('%H:%M'),
                "ClosedAt": order_req.closed_at.strftime('%H:%M'),
                # "DeliveryGroup": order_req.delivery_group,
                "Collection": {
                    "PostalCode": order_req.collection.postcode,
                    "CountryCode": order_req.collection.country_code
                },
                "Delivery": {
                    "PostalCode": order_req.delivery.postcode,
                    "CountryCode": order_req.delivery.country_code
                },
                "GoodsInfo": {
                    "GoodsValue": str(order_req.goods_info.goods_value),
                    "GoodsDescription": order_req.goods_info.goods_description,
                    "PremiumInsurance": str(order_req.goods_info.premium_insurance).title()
                },
                "ShipmentDetails": {
                    "NumberofPieces": str(order_req.shipment_details.number_of_pieces),
                    **Item.items_dict_many(order_req.shipment_details.items)

                }
            }
        }
    }
