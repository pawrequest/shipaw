from helpers import dump_result_model
from shipaw import RoyalMailProvider
from shipaw.config import SHIPAW_SETTINGS, populate_providers
from shipaw.providers.registry import PROVIDER_REGISTER


def test_address_search(sample_remote_address):
    populate_providers()
    search_text = sample_remote_address.search_string
    provider: RoyalMailProvider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    res = provider.client.address_search(search_text)
    dump_result_model(res)

    ...
