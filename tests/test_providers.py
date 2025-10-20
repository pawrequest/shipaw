from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment


def test_sample_fixtures(sample_remote_contact, sample_remote_address, sample_shipment):
    assert sample_remote_contact.contact_name == 'Test Remote Contact Name'
    assert sample_remote_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


def test_provider_makes_ship_dict(all_sample_shipments: Shipment, sample_provider):
    ship = sample_provider.provider_shipment(all_sample_shipments)
    ship = ship.model_dump(by_alias=True)
    assert isinstance(ship, dict)


def test_provider_books_shipment(all_sample_shipments, sample_provider):
    response = sample_provider.book_shipment(all_sample_shipments)
    assert isinstance(response, ShipmentBookingResponse)
    assert response.shipment_num
    assert response.success


def test_provider_converts_shiments(sample_shipment: Shipment, sample_provider):
    ship = sample_provider.provider_shipment(sample_shipment)
    back = sample_provider.agnostic_shipment(ship)
    assert sample_shipment == back


# def test_address_conversions(provider: ShippingProvider, sample_full_contact):
#     for addrtype in provider.address_types:
#         for contact_type in provider.contact_types:
#             converted_address = provider.address_from_agnostic(addrtype, sample_full_contact)
#             converted_contact = provider.contact_from_agnostic(contact_type, sample_full_contact)
#
#             full_contact = provider.full_contact_from_provider(converted_contact, converted_address)
#             assert sample_full_contact == full_contact
#
