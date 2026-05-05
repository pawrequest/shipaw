from shipaw.providers.registry import PROVIDER_REGISTER
from test_providers import provider_context


def test_rm_converts_shipment(all_sample_shipment_requests):
    provider = PROVIDER_REGISTER[all_sample_shipment_requests.provider_name]
    with provider_context(all_sample_shipment_requests):
        service_code = all_sample_shipment_requests.service_code
        shipment = all_sample_shipment_requests.shipment
        rm_shipment = provider.provider_shipment(shipment, service_code)
        back_shipment = provider.agnostic_shipment(rm_shipment)
        assert all_sample_shipment_requests.shipment == back_shipment
