from dataclasses import fields

import httpx

from shipaw.agnostic.address import Address, Contact
from shipaw.agnostic.providers import ConvertMode, ShippingProvider, maybe_dict
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.shipment import FullContact, Shipment as ShipmentAgnost
from shipaw.apc.address import Address as AddressAPC, apc_address, apc_contact, Contact as ContactAPC
from shipaw.apc.services import APCServiceDict, APCServices
from shipaw.apc.shared import EndPoints, get_headers
from shipaw.apc.shipment import GoodsInfo, Order, ShipmentDetails


def apc_shipment(shipment: ShipmentAgnost) -> Order:
    service_code = APCServiceDict[shipment.service]
    ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

    order = Order(
        collection_date=shipment.shipping_date,
        product_code=service_code,
        reference=shipment.reference,
        delivery=AddressAPC.from_generic(shipment.recipient_address, shipment.recipient_contact),
        goods_info=GoodsInfo(),
        shipment_details=ship_deets,
    )
    return order


def service_code_fetch_apc(shipment: ShipmentAgnost):
    prot = APCServices
    service_code = getattr(prot, shipment.service.upper())
    if service_code not in [_.default for _ in fields(prot)]:
        raise ValueError(f'Incorrect APC Product Code: {service_code}')
    return service_code


def apc_shipment_dict(shipment: ShipmentAgnost) -> dict:
    order = apc_shipment(shipment)
    return {'Orders': {'Order': order.model_dump(mode='json', by_alias=True)}}


#
# APCProvider = ShippingProvider(
#     name='APC',
#     service_dict=APCServiceDict,
#     shipment_dict=apc_shipment_dict,
#     send_request=make_shipment_request,
# )


class APCProvider(ShippingProvider):
    service_dict = APCServiceDict

    @staticmethod
    def convert_contact(full_contact: FullContact, mode: ConvertMode = 'dict') -> ContactAPC | dict:
        res = ContactAPC(
            person_name=full_contact.contact.contact_name,
            phone_number=full_contact.contact.mobile_phone,
            mobile_number=full_contact.contact.mobile_phone,
            email=full_contact.contact.email_address,
        )
        return maybe_dict(res, mode)

    @staticmethod
    def convert_address(full_contact: FullContact, mode: ConvertMode = 'dict') -> AddressAPC | dict:
        res = AddressAPC(
            postal_code=full_contact.address.postcode,
            address_line_1=full_contact.address.address_lines[0],
            address_line_2=', '.join(full_contact.address.address_lines[1:]),
            city=full_contact.address.town,
            contact=APCProvider.convert_contact(full_contact),
            company_name=full_contact.contact.business_name,
        )
        return maybe_dict(res, mode)

    @staticmethod
    def convert_shipment(shipment: ShipmentAgnost, mode: ConvertMode = 'dict') -> dict:
        res = apc_shipment(shipment)
        return maybe_dict(res, mode)

    def send_request(self, ship_dict: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        if isinstance(ship_dict, ShipmentAgnost):
            ship_dict = self.convert_shipment(ship_dict, mode='dict')

        res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=ship_dict)
        res.raise_for_status()
        res_json = res.json()
        order = res_json['Orders']['Order']
        order_number = order['OrderNumber']
        return ShipmentBookingResponseAgnost(shipment_num=order_number)

    def handle_response(self, response: ShipmentBookingResponseAgnost) -> bool:
        raise NotImplementedError
