from shipaw.parcelforce.pf_top import parcelforce_shipment

from shipaw.agnostic.agnost import Shipment, ShippingProvider
from shipaw.apc.shipment import apc_shipment


def convert_shipment(shipment: Shipment, provider: ShippingProvider):
    match provider:
        case ShippingProvider.PARCELFORCE:
            return parcelforce_shipment(shipment)
        case ShippingProvider.APC:
            return apc_shipment(shipment)
        case _: raise ValueError('Invalid Provider')

