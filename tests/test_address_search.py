from helpers import dump_result_model
from shipaw import RoyalMailProvider
from shipaw.config import populate_providers
from shipaw.providers.registry import PROVIDER_REGISTER


def test_address_search(sample_remote_address):
    populate_providers()
    provider: RoyalMailProvider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    # search_text = sample_remote_address.search_string
    search_text = 'East Avenue, Hayes, Middlesex'
    res = provider.client.address_search(search_text)
    dump_result_model(res)
    addr_id = res.addresses[0].address_id
    retrieved = provider.client.address_retrieve(addr_id)
    dump_result_model(retrieved)
