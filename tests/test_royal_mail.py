from shipaw.models.shipment import Shipment


def test_rm_converts_shipment(sample_shipment: Shipment, sample_provider_rm):
    rm_shipment = sample_provider_rm.provider_shipment(sample_shipment)
    back_shipment = sample_provider_rm.agnostic_shipment(rm_shipment)
    assert sample_shipment == back_shipment
