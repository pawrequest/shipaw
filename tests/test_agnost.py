from functools import reduce
from operator import getitem

import pytest

from conftest import TEST_DATE
from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.ship_types import ShipDirection
from shipaw.agnostic.shipment import Shipment
from shipaw.apc.provider import APCProvider
from shipaw.apc.shared import apc_date
from shipaw.parcelforce.provider import ParcelforceProvider


def test_sample_fixtures(sample_contact, sample_address, sample_shipment):
    assert sample_contact.contact_name == 'Test Contact name'
    assert sample_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


@pytest.mark.parametrize(
    'provider, attr_path, expected_result',
    [
        (ParcelforceProvider(), ['shipping_date'], TEST_DATE.isoformat()),
        (APCProvider(), ['Orders', 'Order', 'CollectionDate'], apc_date(TEST_DATE)),
    ],
)
def test_provider_makes_ship_dict(
    sample_shipment: Shipment, provider: ShippingProvider, attr_path: list[str], expected_result
):
    ship = provider.make_shipment_dict(shipment=sample_shipment)
    actual_result = reduce(getitem, attr_path, ship)
    assert actual_result == expected_result


@pytest.mark.parametrize('provider', [ParcelforceProvider(), APCProvider()], ids=['ParcelforceProvider', 'APCProvider'])
def test_provider_books_shipment(sample_shipment, provider: ShippingProvider):
    response = provider.send_request(sample_shipment)
    assert isinstance(response, ShipmentBookingResponseAgnost)


    with pytest.raises(NotImplementedError):
        result = provider.handle_response(response)
        assert result

