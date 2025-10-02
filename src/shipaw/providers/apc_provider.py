import json
from base64 import b64decode

import httpx
from pydantic import BaseModel

from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.fapi.alerts import Alert, Alerts
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment, Shipment as ShipmentAgnost
from apc_hypaship.models.request.address import Address, Contact
from apc_hypaship.config import apc_settings
from apc_hypaship.models.request.shipment import GoodsInfo, Order, Orders, Shipment as ShipmentAPC, ShipmentDetails
from shipaw.models.provider import ShippingProvider, register_provider

APC_SERVICES = Services(
    NEXT_DAY='ND16',
    NEXT_DAY_12='ND12',
    NEXT_DAY_9='ND09',
)


def address_from_agnostic_fc[addr_type: Address](cls: type[addr_type], full_contact: FullContact) -> addr_type:
    lines_ = [_ for _ in full_contact.address.address_lines[1:] if _]
    lines = ', '.join(lines_)
    return cls(
        company_name=full_contact.address.business_name,
        address_line_1=full_contact.address.address_lines[0],
        address_line_2=lines,
        city=full_contact.address.town,
        postal_code=full_contact.address.postcode,
        country_code=full_contact.address.country,
        contact=Contact(
            person_name=full_contact.contact.contact_name,
            email=full_contact.contact.email_address,
            mobile_number=full_contact.contact.mobile_phone,
            phone_number=full_contact.contact.phone_number or full_contact.contact.mobile_phone,
        ),
    )


def contact_from_agnostic_fc[contact_type: Contact](cls: type[contact_type], full_contact: FullContact) -> contact_type:
    return cls(
        person_name=full_contact.contact.contact_name,
        email=full_contact.contact.email_address,
        mobile_number=full_contact.contact.mobile_phone,
        phone_number=full_contact.contact.phone_number,
    )


def full_contact_from_apc_contact_address(contact: Contact, address: Address) -> FullContact:
    return FullContact(
        address=AddressAgnost(
            business_name=address.company_name,
            address_lines=[line for line in [address.address_line_1, address.address_line_2] if line],
            town=address.city,
            postcode=address.postal_code,
            country=address.country_code,
        ),
        contact=ContactAgnost(
            contact_name=contact.person_name,
            email_address=contact.email,
            mobile_phone=contact.mobile_number,
            phone_number=contact.phone_number or contact.mobile_number,
        ),
    )


def apc_shipment_to_agnostic(shipment: ShipmentAPC) -> ShipmentAgnost:
    order = shipment.orders.order
    del_fc = full_contact_from_apc_contact_address(order.delivery.contact, order.delivery)
    send_fc = (
        full_contact_from_apc_contact_address(order.collection.contact, order.collection) if order.collection else None
    )
    service = APC_SERVICES.reverse_lookup(order.product_code)

    return ShipmentAgnost(
        service=service,
        shipping_date=order.collection_date,
        reference=order.reference,
        recipient=del_fc,
        sender=send_fc,
        boxes=order.shipment_details.number_of_pieces,
        direction=ShipDirection.INBOUND if order.collection is not None else ShipDirection.OUTBOUND,
    )


def apc_shipment_from_agnostic(shipment: ShipmentAgnost) -> ShipmentAPC:
    # todo handle direction
    if shipment.direction not in [ShipDirection.INBOUND, ShipDirection.OUTBOUND]:
        raise NotImplementedError('APCShippingProvider does not support DROPOFF shipments')

    service_code = APC_SERVICES.lookup(shipment.service)
    ship_deets = ShipmentDetails(number_of_pieces=shipment.boxes)

    order = Order(
        ready_at=shipment.collect_ready,
        closed_at=shipment.collect_closed,
        collection_date=shipment.shipping_date,
        product_code=service_code,
        reference=shipment.reference,
        delivery=address_from_agnostic_fc(Address, shipment.recipient),
        collection=address_from_agnostic_fc(Address, shipment.sender) if shipment.sender else None,
        goods_info=GoodsInfo(),
        shipment_details=ship_deets,
    )
    return ShipmentAPC(orders=Orders(order=order))


# @dataclass
@register_provider
class APCShippingProvider(ShippingProvider):
    name = 'APC'
    services = APC_SERVICES

    def agnostic_shipment(self, shipment: ShipmentAPC) -> Shipment:
        return apc_shipment_to_agnostic(shipment)

    def provider_shipment(self, shipment: Shipment) -> BaseModel:
        return apc_shipment_from_agnostic(shipment)

    def book_shipment(self, shipment: dict | ShipmentAgnost, settings=apc_settings()) -> ShipmentBookingResponse:
        """Takes provider ShipmnentDict, or ShipmentAgnost object"""
        shipment_dict = self.get_shipment_alias_dict(shipment)
        res = httpx.post(settings.orders_endpoint, headers=settings.headers, json=shipment_dict)
        res.raise_for_status()
        res_json = res.json()
        messages = json.loads(res.text).get('Orders').get('Order').get('Messages')
        if 'ErrorFields' in messages.keys():
            fieldname = messages['ErrorFields']['ErrorField']['FieldName']
            message = messages['ErrorFields']['ErrorField']['ErrorMessage']
            alerts = Alerts(alert=[Alert(message=f'Error booking shipment: {fieldname}: {message}')])
            return ShipmentBookingResponse(
                alerts=alerts,
                shipment=shipment,
                shipment_num='FAILED TO BOOK',
                tracking_link='NOT IMPLEMENTED',
                data=res_json,
                status=str(res.status_code),
                success=False,
                label_data=b'',
            )
        order = res_json['Orders']['Order']
        order_number = order['OrderNumber']

        return ShipmentBookingResponse(
            shipment=shipment,
            shipment_num=order_number,
            tracking_link='NOT IMPLEMENTED',
            data=res_json,
            status=str(res.status_code),
            success=res.is_success,
            label_data=self.get_label_content(order_number),
        )

    def get_label_content(self, shipment_num: str) -> bytes:
        params = {'labelformat': 'PDF'}
        settings = apc_settings()
        label = httpx.get(settings.one_order_endpoint(shipment_num), headers=settings.headers, params=params)
        label.raise_for_status()
        content = label.json()['Orders']['Order']['Label']['Content']
        return b64decode(content)

