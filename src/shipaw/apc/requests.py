from base64 import b64decode
from pathlib import Path

import httpx

from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.apc.shared import EndPoints, get_headers


def order_endpoint(order_num: str):
    return EndPoints.BASE + f'Orders/{order_num}.json'


def make_shipment_request(ship_dict: dict) -> ShipmentBookingResponseAgnost:
    res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=ship_dict)
    res.raise_for_status()
    res_json = res.json()
    order = res_json['Orders']['Order']
    order_number = order['OrderNumber']
    return ShipmentBookingResponseAgnost(shipment_num=order_number)

