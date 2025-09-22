from base64 import b64decode
from typing import ClassVar

import httpx

from shipaw.agnostic.address import Address, Contact, FullContact
from shipaw.agnostic.providers import ShippingProvider, service_lookup_agnost
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.ship_types import ConvertMode, ProviderName, ShipDirection, pydantic_export
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.apc.address import Address as AddressAPC, Contact as ContactAPC
from shipaw.apc.requests import order_endpoint
from shipaw.apc.services import APCServiceDict
from shipaw.apc.shared import EndPoints, get_headers
from shipaw.apc.shipment import GoodsInfo, Order, Orders, ShipmentAPC, ShipmentDetails


def get_label_content(order_num: str):
    params = {'labelformat': 'PDF'}
    label = httpx.get(order_endpoint(order_num), headers=get_headers(), params=params)
    content = label.json()['Orders']['Order']['Label']['Content']
    return b64decode(content)


def apc_shipment(shipment: ShipmentAgnost) -> Order:
    service_code = APCServiceDict[shipment.service]
    ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

    order = Order(
        collection_date=shipment.shipping_date,
        product_code=service_code,
        reference=shipment.reference,
        delivery=AddressAPC.from_generic(shipment.recipient.address, shipment.recipient.contact),
        goods_info=GoodsInfo(),
        shipment_details=ship_deets,
    )
    return order


# def service_code_fetch_apc(shipment: ShipmentAgnost):
#     prot = APCServices
#     service_code = getattr(prot, shipment.service.upper())
#     if service_code not in [_.default for _ in fields(prot)]:
#         raise ValueError(f'Incorrect APC Product Code: {service_code}')
#     return service_code


# def apc_shipment_dict(shipment: ShipmentAgnost) -> dict:
#     order = apc_shipment(shipment)
#     return {'Orders': {'Order': order.model_dump(mode='json', by_alias=True)}}


#
# APCProvider = ShippingProvider(
#     name='APC',
#     service_dict=APCServiceDict,
#     shipment_dict=apc_shipment_dict,
#     send_request=make_shipment_request,
# )


# class ServiceEnumAPC(ServiceEnum):
#     NEXT_DAY = 'N'
#     NEXT_DAY_12 = 'D'
#     NEXT_DAY_9 = 'M'


class APCProvider(ShippingProvider):
    name: ClassVar[ProviderName] = 'APC'
    service_dict: ClassVar[ServiceDict] = APCServiceDict
    shipment_type: ClassVar[type[ShipmentAPC]] = ShipmentAPC

    @staticmethod
    def contact_only(contact: Contact, mode: ConvertMode = 'python') -> ContactAPC | dict:
        return pydantic_export(
            ContactAPC(
                person_name=contact.contact_name,
                phone_number=contact.mobile_phone,
                mobile_number=contact.mobile_phone,
                email=contact.email_address,
            ),
            mode,
        )

    @staticmethod
    def provider_contact(full_contact: FullContact, mode: ConvertMode = 'python') -> ContactAPC | dict:
        return APCProvider.contact_only(full_contact.contact, mode)

    @staticmethod
    def provider_address(full_contact: FullContact, mode: ConvertMode = 'python') -> AddressAPC | dict:
        return pydantic_export(
            AddressAPC(
                postal_code=full_contact.address.postcode,
                address_line_1=full_contact.address.address_lines[0],
                address_line_2=', '.join(full_contact.address.address_lines[1:]),
                city=full_contact.address.town,
                contact=APCProvider.provider_contact(full_contact),
                company_name=full_contact.contact.business_name,
            ),
            mode,
        )

    @staticmethod
    def provider_shipment(shipment: ShipmentAgnost, mode: ConvertMode = 'python') -> dict | ShipmentAPC:
        # todo handle direction
        if shipment.direction not in [ShipDirection.INBOUND, ShipDirection.OUTBOUND]:
            raise NotImplementedError('APCProvider does not support DROPOFF shipments')

        service_code = APCProvider.service_dict[shipment.service]
        ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

        order = Order(
            collection_date=shipment.shipping_date,
            product_code=service_code,
            reference=shipment.reference,
            delivery=APCProvider.provider_address(shipment.recipient, mode='python'),
            collection=APCProvider.provider_address(shipment.sender, mode='python') if shipment.sender else None,
            goods_info=GoodsInfo(),
            shipment_details=ship_deets,
        )

        shipment_out = ShipmentAPC(orders=Orders(order=order))

        return pydantic_export(shipment_out, mode)

    @staticmethod
    def generic_full_contact(
        contact: ContactAPC, address: AddressAPC, mode: ConvertMode = 'python'
    ) -> FullContact | dict:
        return pydantic_export(
            FullContact(
                contact=Contact(
                    contact_name=address.contact.person_name,
                    mobile_phone=address.contact.mobile_number,
                    email_address=address.contact.email,
                    business_name=address.company_name,
                ),
                address=Address(
                    postcode=address.postal_code,
                    address_lines=[address.address_line_1]
                    + ([address.address_line_2] if address.address_line_2 else []),
                    town=address.city,
                ),
            ),
            mode,
        )

    @staticmethod
    def generic_shipment(shipment: ShipmentAPC, mode: ConvertMode = 'python') -> dict | ShipmentAgnost:
        order = shipment.orders.order
        fc = APCProvider.generic_full_contact(order.delivery.contact, order.delivery, mode='python')

        ship = ShipmentAgnost(
            service=service_lookup_agnost(APCProvider.service_dict, order.product_code),
            shipping_date=order.collection_date,
            reference=order.reference,
            recipient=fc,
            boxes=order.shipment_details.number_of_pieces,
            direction=ShipDirection.INBOUND if order.collection is not None else ShipDirection.OUTBOUND,
        )
        return pydantic_export(ship, mode)

    @staticmethod
    def book_shipment(shipment: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        shipment = ShipmentAgnost.model_validate(shipment)
        shipment_apc = APCProvider.provider_shipment(shipment, mode='python-alias')

        res = httpx.post(EndPoints.ORDERS, headers=get_headers(), json=shipment_apc)
        res.raise_for_status()
        res_json = res.json()
        order = res_json['Orders']['Order']
        order_number = order['OrderNumber']
        return ShipmentBookingResponseAgnost(
            shipment=shipment,
            shipment_num=order_number,
            tracking_link='NOT IMPLEMENTED',
            data=res_json,
            status=str(res.status_code),
            success=res.is_success,
            label_data=APCProvider.get_label_content(order_number),
        )

    # @staticmethod
    # def handle_response(request: ShipmentRequestAgnost, response: ShipmentBookingResponseAgnost):
    #     raise NotImplementedError

    @staticmethod
    def get_label_content(shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        label = httpx.get(order_endpoint(shipment_num), headers=get_headers(), params=params)
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)
