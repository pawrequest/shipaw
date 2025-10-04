from apc_hypaship.models.request.address import Address, Contact
from apc_hypaship.models.request.shipment import GoodsInfo, Order, Orders, Shipment as ShipmentAPC, ShipmentDetails
from shipaw.fapi.alerts import Alert, Alerts
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from shipaw.models.services import Services
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment as ShipmentAgnost

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
        collect_ready=order.ready_at,
        collect_closed=order.closed_at,
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

