from datetime import date, time

from pydantic import ConfigDict

from shipaw.agnostic.base import ShipawBaseModel


class APCBaseModel(ShipawBaseModel):
    model_config = ConfigDict(
        json_encoders={
            time: lambda v: v.strftime('%H:%M'),
            date: lambda v: v.strftime('%d/%m/%Y'),
        },
    )


# class EndPoints(StrEnum):
#     BASE = r'https://apc-training.hypaship.com/api/3.0/'
#     SERVICES = BASE + 'ServiceAvailability.json'
#     ORDERS = BASE + 'Orders.json'

#
# def order_endpoint(order_num: str):
#     return EndPoints.BASE + f'Orders/{order_num}.json'


