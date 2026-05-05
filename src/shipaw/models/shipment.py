import datetime as dt

from pydantic import Field, model_validator

from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.models.base import ShipawBaseModel
from shipaw.utils.consts_enums import PackageFormat, ShipDirection


def build_reference(
    reference: str, max_chars: int, total_boxes: int, send_date: dt.date, box: int | None = None
) -> str:
    if max_chars < 14:
        raise ValueError('max_chars must be at least 14 to fit date and box info')
    if max_chars < 16 and box is not None:
        raise ValueError('max_chars must be at least 16 to include box numbering')
    date_str = send_date.strftime('%d/%m')  # 5 chars
    box_str = f' {box}/{total_boxes} boxes' if box else f' {total_boxes} boxes'  # 9 or 11 chars
    box_str_len = len(box_str)
    date_str_len = len(date_str)
    max_ref_len = max_chars - date_str_len - box_str_len  # n-14 or n-16 chars left
    ref_str = reference[:max_ref_len] if max_ref_len > 0 else ''
    ref_str_len = len(ref_str)
    num_spaces = max_chars - date_str_len - box_str_len - ref_str_len
    return ref_str + ' ' * num_spaces + date_str + box_str


class Shipment(ShipawBaseModel):
    recipient: FullContact
    sender: FullContact | None = None  # default to ShipawSettings.address/contact if None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection
    own_label: bool | None = None  # print own label vs driver brings
    reference: str = ''

    # todo is context still used?
    context: dict = Field(default_factory=dict)

    collect_ready: dt.time = dt.time(hour=9, minute=0)
    collect_closed: dt.time = dt.time(hour=17, minute=0)

    package_format: PackageFormat = PackageFormat.PARCEL
    weight_kg: int = 10

    @model_validator(mode='after')
    def val_direction(self):
        match self.direction:
            case ShipDirection.OUTBOUND:
                if not self.recipient:
                    raise ValueError('Recipient must be provided for OUTBOUND shipments')
            case ShipDirection.INBOUND | ShipDirection.DROPOFF:
                if not self.sender:
                    raise ValueError('Sender must be provided for INBOUND and DROPOFF shipments')
            case ShipDirection.THIRD_PARTY:
                if not self.recipient or not self.sender:
                    raise ValueError('Both sender and recipient must be provided for THIRD_PARTY shipments')
            case _:
                raise ValueError('Invalid ShipDirection')
        return self

    @property
    def remote_full_contact(self) -> FullContact:
        match self.direction:
            case ShipDirection.OUTBOUND:
                return self.recipient
            case ShipDirection.INBOUND | ShipDirection.DROPOFF:
                return self.sender
            case _:
                raise ValueError('Bad ShipDirection')


def sample_shipment() -> Shipment:
    contact = Contact(
        name='Test Contact name',
        mobile_phone='07666666666',
        email='sdgsdg@sdgsdg.com',
    )
    address = Address(
        postcode='NW11 8AA',
        address_line1='Test Street',
        address_line2='Test Area',
        town='Test Town',
        country='GB',
        business_name='Test Company',
    )
    full_contact = FullContact(contact=contact, address=address)
    return Shipment(
        recipient=full_contact,
        boxes=2,
        shipping_date=dt.date.today() + dt.timedelta(days=2),
        direction=ShipDirection.OUTBOUND,
        reference='Test Reference',
    )
