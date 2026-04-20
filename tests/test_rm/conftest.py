from pprint import pprint
from typing import Generator

import pytest
from royal_mail_combined import RoyalMailClient
from royal_mail_combined.click_and_drop_api.models import GetOrdersResponse
from royal_mail_combined.config import RoyalMailSettingsGlobal


@pytest.fixture(scope='session')
def fxt_settings() -> RoyalMailSettingsGlobal:
    return RoyalMailSettingsGlobal.from_env()


@pytest.fixture(scope='session')
def fxt_client(fxt_settings) -> Generator[RoyalMailClient]:
    """Test client - automatically removes orders created during testing on completion"""
    client = RoyalMailClient(fxt_settings)
    orders_before: GetOrdersResponse = client.fetch_orders()
    pprint(orders_before.model_dump())

    yield client

    orders_after: GetOrdersResponse = client.fetch_orders()
    for o in orders_after.orders:
        if o not in orders_before.orders:
            print('Deleting Test Order')
            res = client.cancel_outbound_shipment(order_identifiers=str(o.order_identifier))
            assert o.order_identifier in res.order_idents(), 'WARNING, FAILED TO DELETE TEST ORDERS!!'
            print('Deleted Test Orders')
