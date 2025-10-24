from royal_mail_click_and_drop.v2.services import RoyalMailServiceCode

from shipaw.providers.provider_abc import ShippingProvider


def test_it(sample_provider: ShippingProvider):
    print('\n\n')
    for _ in sample_provider.services_as_tups():
        print(_)


def test_y():
    mynum = RoyalMailServiceCode
    ...
