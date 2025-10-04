from shipaw.fapi.alerts import Alerts, Alert
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment as ShipmentAgnost


def booking_has_errors(res_json: dict):
    if messages := res_json.get('Orders').get('Order').get('Messages'):
        return 'ErrorFields' in messages.keys()
    return False


def errored_booking(shipment: ShipmentAgnost, res_json: dict):
    messages = res_json.get('Orders').get('Order').get('Messages')
    fieldname, message = strip_apc_error_msgs(messages)
    return errored_deets(fieldname, message, shipment, res_json)


def strip_apc_error_msgs(messages):
    fieldname = messages['ErrorFields']['ErrorField']['FieldName']
    message = messages['ErrorFields']['ErrorField']['ErrorMessage']
    return fieldname, message


def errored_deets(fieldname: str, message: str, shipment: ShipmentAgnost, data: dict):
    alerts = Alerts(alert=[Alert(message=f'Error booking shipment: {fieldname}: {message}')])
    return ShipmentBookingResponse(
        alerts=alerts,
        shipment=shipment,
        shipment_num='FAILED TO BOOK',
        tracking_link='NOT IMPLEMENTED',
        data=data,
        success=False,
    )

