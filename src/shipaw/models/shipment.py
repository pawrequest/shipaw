import datetime as dt

from pydantic import Field

from shipaw.models.address_contact import FullContact
from shipaw.models.base import ShipawBaseModel
from shipaw.utils.consts_enums import PackageFormat, ShipDirection


class Shipment(ShipawBaseModel):
    recipient: FullContact
    sender: FullContact | None = None  # default to ShipawSettings.address/contact if None

    boxes: int = 1
    shipping_date: dt.date
    direction: ShipDirection
    own_label: bool | None = None  # print own label vs driver brings
    # service: AgnostServiceName = AgnostServiceName.NEXT_DAY
    reference: str = ''

    # todo is context still used?
    context: dict = Field(default_factory=dict)

    collect_ready: dt.time = dt.time(hour=9, minute=0)
    collect_closed: dt.time = dt.time(hour=17, minute=0)

    package_format: PackageFormat = PackageFormat.PARCEL
    weight_kg: int = 10

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
    from shipaw.models.address_contact import Address, Contact

    contact = Contact(
        name='Test Contact name',
        mobile_phone='07666666666',
        email_address='sdgsdg@sdgsdg.com',
    )
    address = Address(
        postcode='DA16 3HU',
        address_lines=['25 Bennet Close'],
        town='Welling',
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
        # service=AgnostServiceName.NEXT_DAY,
    )
