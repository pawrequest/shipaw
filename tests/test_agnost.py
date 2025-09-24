from functools import reduce
from operator import getitem

import pytest

from conftest import TEST_DATE
from shipaw.agnostic.address import FullContact
from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.requests import ShipmentRequestAgnost
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.ship_types import ShipDirection, pydantic_export
from shipaw.agnostic.shipment import Shipment
from shipaw.apc.address import Address as AddressAPC, Contact as ContactAPC
from shipaw.apc.provider import APCProvider
from shipaw.apc.shared import apc_date
from shipaw.parcelforce.address import AddressBase as AddressPF, Contact as ContactPF
from shipaw.parcelforce.provider import ParcelforceProvider


def test_sample_fixtures(sample_contact, sample_address, sample_shipment):
    assert sample_contact.contact_name == 'Test Contact name'
    assert sample_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


@pytest.mark.parametrize(
    'provider, attr_path, expected_result',
    [
        (ParcelforceProvider(), ['ShippingDate'], TEST_DATE.isoformat()),
        (APCProvider(), ['Orders', 'Order', 'CollectionDate'], apc_date(TEST_DATE)),
    ],
)
def test_provider_makes_ship_dict(
    sample_shipment: Shipment, provider: ShippingProvider, attr_path: list[str], expected_result
):
    # ship = provider.provider_shipment(shipment=sample_shipment, mode='python-alias')
    ship = provider.shipment_type.from_generic(sample_shipment)
    ship = pydantic_export(ship, mode='python-alias')
    actual_result = reduce(getitem, attr_path, ship)
    assert actual_result == expected_result


@pytest.mark.parametrize('provider', [ParcelforceProvider(), APCProvider()], ids=['ParcelforceProvider', 'APCProvider'])
def test_provider_books_shipment(sample_shipment, provider: ShippingProvider):
    ship_req = ShipmentRequestAgnost(shipment=sample_shipment, provider_name=provider.name)
    response = provider.book_shipment(sample_shipment)
    assert isinstance(response, ShipmentBookingResponseAgnost)

    provider.handle_response(ship_req, response)


def test_address_conversions_pf(sample_full_contact):
    parcelforce_addr = AddressPF.from_generic(sample_full_contact.address)
    parcelforce_cont = ContactPF.from_generic(sample_full_contact.contact, sample_full_contact.address.business_name)
    generic_addr = parcelforce_addr.to_generic(business_name=parcelforce_cont.business_name)
    generic_cont = parcelforce_cont.to_generic()
    assert sample_full_contact == FullContact(address=generic_addr, contact=generic_cont)


def test_address_conversions_apc(sample_full_contact):
    apc_addr = AddressAPC.from_generic(sample_full_contact.address, sample_full_contact.contact)
    apc_contact = ContactAPC.from_generic(sample_full_contact.contact)
    generic_addr = apc_addr.to_generic()
    generic_contact = apc_contact.to_generic()
    full_contact = FullContact(address=generic_addr, contact=generic_contact)
    assert sample_full_contact == full_contact
