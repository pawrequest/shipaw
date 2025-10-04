# import httpx
# import pytest
# # from pawdantic.paw_types import pydantic_export
#
# from conftest import TEST_DATE
# from shipaw.fapi.responses import ShipmentBookingResponse
# from apc_hypaship.models.request.address import Address as APCAddress, Contact, Contact as APCContact
# from apc_hypaship.config import apc_date, APCSettings
# from apc_hypaship.models.request.services import ServiceSpec
# from apc_hypaship.models.request.shipment import Shipment as APCShipment
# from shipaw.providers.apc.provider import (
#     APCShippingProvider,
# )
# from shipaw.providers.apc.provider_funcs import (
#     address_from_agnostic_fc,
#     apc_shipment_from_agnostic,
#     contact_from_agnostic_fc,
# )
#
# TEST_DATE_STR = apc_date(TEST_DATE)
# PROVIDER = APCShippingProvider()
#
#
# def test_convert_contact_to_apc(sample_full_contact):
#     contact = contact_from_agnostic_fc(Contact, sample_full_contact)
#     assert isinstance(contact, APCContact)
#     assert contact.person_name == 'Test Contact name'
#
#
# def test_convert_address_to_apc(sample_full_contact):
#     addr = address_from_agnostic_fc(APCAddress, sample_full_contact)
#     assert isinstance(addr, APCAddress)
#     assert addr.postal_code == 'DA16 3HU'
#     assert addr.contact.person_name == 'Test Contact name'
#
#
# def test_convert_shipment_to_apc(sample_shipment):
#     shipment: APCShipment = apc_shipment_from_agnostic(sample_shipment)
#     assert isinstance(shipment, APCShipment)
#     assert shipment.orders.order.delivery.postal_code == 'DA16 3HU'
#
#
