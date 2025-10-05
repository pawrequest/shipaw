from parcelforce_expresslink.address import (
    AddressCollection,
    ContactCollection,
    AddressSender,
    ContactSender,
    AddressRecipient,
    Contact,
)
from parcelforce_expresslink.shared import DateTimeRange
from parcelforce_expresslink.top import CollectionInfo
from parcelforce_expresslink.types import ShipmentType


def test_parcelforce_shipment_direction(sample_shipment, sample_parcelforce_provider):
    out = sample_parcelforce_provider.provider_shipment(sample_shipment)
    assert out.shipment_type == ShipmentType.DELIVERY
    assert out.print_own_label is None
    assert out.collection_info is None
    assert out.sender_address is None
    assert out.sender_contact is None
    ...


def test_parcelforce_shipment_direction_in(sample_shipment_inbound, sample_parcelforce_provider):
    in_ = sample_parcelforce_provider.provider_shipment(sample_shipment_inbound)
    assert in_.shipment_type == ShipmentType.COLLECTION
    assert in_.print_own_label == True
    assert isinstance(in_.collection_info, CollectionInfo)
    assert isinstance(in_.collection_info.collection_address, AddressCollection)
    assert isinstance(in_.collection_info.collection_contact, ContactCollection)
    assert isinstance(in_.collection_info.collection_time, DateTimeRange)


def test_parcelforce_shipment_direction_dropoff(sample_shipment_dropoff, sample_parcelforce_provider):
    drop = sample_parcelforce_provider.provider_shipment(sample_shipment_dropoff)
    assert drop.shipment_type == ShipmentType.DELIVERY
    assert drop.print_own_label is None
    assert drop.collection_info is None
    assert isinstance(drop.sender_address, AddressSender)
    assert isinstance(drop.sender_contact, ContactSender)
    assert isinstance(drop.recipient_address, AddressRecipient)
    assert isinstance(drop.recipient_contact, Contact)
    ...
