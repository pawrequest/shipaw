from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.expresslink_client import ParcelforceClient

from shipaw.models.logging import log_obj


def cancel_parcelforce(ship_number):
    live_settings = ParcelforceSettings.from_env('PARCELFORCE_ENV')
    client = ParcelforceClient(settings=live_settings)
    resp = client.cancel_shipment(ship_number)
    log_obj(resp)
    return resp


if __name__ == '__main__':
    # res = cancel_parcelforce()

    ...