import contextlib

import pytest

from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.ship_types import ShipDirection
from shipaw.providers.provider_abc import ProviderName


def test_sample_fixtures(sample_remote_contact, sample_remote_address, sample_shipment):
    assert sample_remote_contact.contact_name == 'Test Remote Contact Name'
    assert sample_remote_address.postcode == 'DA16 3HU'
    assert sample_shipment.direction == ShipDirection.OUTBOUND


def test_provider_makes_ship_dict(all_sample_shipment_requests: ShipmentRequest):
    provider = all_sample_shipment_requests.provider
    with provider_context(all_sample_shipment_requests):
        service_code = provider.default_service
        ship = provider.provider_shipment(all_sample_shipment_requests.shipment, service_code=service_code)
        ship = ship.model_dump(by_alias=True)
        assert isinstance(ship, dict)


def test_provider_books_shipment(all_sample_shipment_requests):
    provider = all_sample_shipment_requests.provider
    with provider_context(all_sample_shipment_requests):
        response = provider.book_shipment_agnostic(all_sample_shipment_requests)
        assert isinstance(response, ShipmentBookingResponse)
        assert response.shipment_num
        assert response.success


def test_provider_converts_shiments(all_sample_shipment_requests: ShipmentRequest):
    provider = all_sample_shipment_requests.provider
    service = provider.service_codes_type(all_sample_shipment_requests.service_code)
    sampo_shipment = all_sample_shipment_requests.shipment

    with provider_context(all_sample_shipment_requests):
        ship = provider.provider_shipment(sampo_shipment, service_code=service)
        back = provider.agnostic_shipment(ship)
        assert sampo_shipment == back


def provider_context(shipment_request):
    provider = shipment_request.provider
    ctx = contextlib.nullcontext()
    if provider.name == ProviderName.APC:
        if shipment_request.shipment.direction == ShipDirection.DROPOFF:
            ctx = pytest.raises(NotImplementedError)
    elif provider.name == ProviderName.ROYAL_MAIL:
        if shipment_request.shipment.direction not in [ShipDirection.OUTBOUND]:
            ctx = pytest.raises(NotImplementedError)
    return ctx


# def test_address_conversions(provider: ShippingProvider, sample_full_contact):
#     for addrtype in provider.address_types:
#         for contact_type in provider.contact_types:
#             converted_address = provider.address_from_agnostic(addrtype, sample_full_contact)
#             converted_contact = provider.contact_from_agnostic(contact_type, sample_full_contact)
#
#             full_contact = provider.full_contact_from_provider(converted_contact, converted_address)
#             assert sample_full_contact == full_contact
#
