from datetime import datetime

import pytest
from resources.shared import AddressRoughDC
from shipr.apc.available_services.avail_funcs import do_request, make_avail_serv_dict
from shipr.apc.available_services.avail_request import GoodsInfo, Item, ServiceRequest, \
    ShipmentDetails
from shipr.apc.strs import SandboxEndPoints


@pytest.fixture
def avail_req_fxt():
    dummy_item = Item(
        type='ALL',
        weight=1,
        length=1,
        width=1,
        height=1,
        value=1,
    )
    dummy_goods_info = GoodsInfo(1, '.....', False)
    dummy_shipment_details = ShipmentDetails(
        number_of_pieces=1,
        items=[dummy_item]
    )
    dummy_order = ServiceRequest(
        collection_date=datetime(2024, 2, 1),
        ready_at=datetime(2024, 2, 1, 9),
        closed_at=datetime(2024, 2, 1, 18),
        collection=AddressRoughDC(
            postcode='NW6 4TE',
            country_code='GB'
        ),
        delivery=AddressRoughDC(
            postcode='M17 1WA',
            country_code='GB'
        ),
        goods_info=dummy_goods_info,
        shipment_details=dummy_shipment_details
    )
    return dummy_order


@pytest.mark.asyncio
async def test_avail(avail_req_fxt):
    req_dict = make_avail_serv_dict(avail_req_fxt)
    response = await do_request(SandboxEndPoints.SERVICE_AVAILABILITY, req_dict)
    assert response['ServiceAvailability']['Messages']['Code'] == 'SUCCESS'
