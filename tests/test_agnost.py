from conftest import sample_provider
from shipaw.providers.providers import ShippingProvider
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.ship_types import ShipDirection
from shipaw.models.shipment import Shipment


def test_sample_fixtures(sample_contact, sample_address, sample_shipment):
    assert sample_contact.contact_name == 'Test Contact name'
    assert sample_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


def test_provider_makes_ship_dict(sample_shipment: Shipment, sample_provider):
    ship = sample_provider.provider_shipment(sample_shipment)
    ship = ship.model_dump(by_alias=True)
    assert isinstance(ship, dict)


def test_provider_books_shipment(sample_shipment, sample_provider):
    response = sample_provider.book_shipment(sample_shipment)
    assert isinstance(response, ShipmentBookingResponse)
    assert response.shipment_num
    assert response.label_data


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
