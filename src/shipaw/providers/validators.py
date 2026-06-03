from datetime import date

from shipaw.fapi.alerts import Alert, Alerts, AlertType, maybe_alert_phone_number
from shipaw.fapi.requests import ShipmentRequest
from shipaw.providers.apc.apc_funcs import apc_shipment_request_alerts
from shipaw.providers.provider_abc import ProviderName
from shipaw.utils.consts_enums import ShipDirection


def validate_shipment_request(shipment_request: ShipmentRequest):
    if shipment_request.provider_name == ProviderName.ROYAL_MAIL:
        if shipment_request.shipment.direction in [ShipDirection.INBOUND]:  # todo add thirdparty
            if shipment_request.shipment.shipping_date == date.today():
                raise ValueError('Can not collect today')


async def royal_mail_shipment_request_alerts(shipment_request) -> Alerts:
    alerts = Alerts.empty()
    if shipment_request.provider_name == ProviderName.ROYAL_MAIL:
        if shipment_request.shipment.direction in [ShipDirection.INBOUND]:  # todo add thirdparty
            if shipment_request.shipment.shipping_date == date.today():
                alerts += Alert(message='Royal Mail Can Not Collect Today', type=AlertType.ERROR)
    return alerts


async def get_shipment_request_alerts(shipment_request: ShipmentRequest) -> Alerts:
    alerts = Alerts.empty()  # todo async
    alerts += await maybe_alert_phone_number(shipment_request.shipment.remote_full_contact.contact.mobile_phone)
    alerts += await royal_mail_shipment_request_alerts(shipment_request)
    alerts += await apc_shipment_request_alerts(shipment_request)
    return alerts
