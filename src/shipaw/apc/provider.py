from dataclasses import fields

from shipaw.agnostic.providers import ShippingProvider, service_code_fetch
from shipaw.agnostic.shipment import Shipment
from shipaw.apc.address import Address
from shipaw.apc.services import APCServiceDict, APCServices
from shipaw.apc.shipment import GoodsInfo, Order, ShipmentDetails


def apc_shipment(shipment: Shipment) -> Order:
    service_code = APCServiceDict[shipment.service.upper()]
    ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

    order = Order(
        collection_date=shipment.shipping_date,
        product_code=service_code,
        reference=shipment.reference,
        delivery=Address.from_generic(shipment.recipient_address, shipment.recipient_contact),
        goods_info=GoodsInfo(),
        shipment_details=ship_deets,
    )
    return order


def service_code_fetch_apc(shipment: Shipment):
    prot = APCServices
    service_code = getattr(prot, shipment.service.upper())
    if service_code not in [_.default for _ in fields(prot)]:
        raise ValueError(f'Incorrect APC Product Code: {service_code}')
    return service_code


def apc_shipment_dict(shipment: Shipment) -> dict:
    order = apc_shipment(shipment)
    return {'Orders': {'Order': order.model_dump(mode='json', by_alias=True)}}


APCProvider = ShippingProvider(
    name='APC',
    service_dict=APCServiceDict,
    shipment_dict=apc_shipment_dict,
)
