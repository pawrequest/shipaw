from datetime import date, time

import pytest

from shipr.apc.available_services.avail_request import Item, GoodsInfo, ShipmentDetails, Order, \
    AddressRoughDC


@pytest.fixture
def dummy_item() -> Item:
    return Item(
        type='ALL',
        weight=1,
        length=1,
        width=1,
        height=1,
        value=1,
    )


@pytest.fixture
def dummy_goods_info() -> GoodsInfo:
    return GoodsInfo(
        goods_value=1,
        goods_description='test description',
        premium_insurance=False
    )


@pytest.fixture
def dummy_shipment_details(dummy_item) -> ShipmentDetails:
    return ShipmentDetails(
        number_of_pieces=1,
        items=[dummy_item]
    )


@pytest.fixture
def order_fxt(dummy_item, dummy_goods_info, dummy_shipment_details) -> Order:
    dummy_request = Order(
        collection_date=date(2024, 2, 5),
        ready_at=time(9),
        closed_at=time(18),
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
    return dummy_request


@pytest.fixture
def avail_req_fxt(dummy_item, dummy_goods_info, dummy_shipment_details) -> Order:
    dummy_request = Order(
        collection_date=date(2024, 2, 5),
        ready_at=time(9),
        closed_at=time(18),
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
    return dummy_request


# @pytest.mark.asyncio
# async def test_avail(order_fxt):
#     req_dict = make_avail_serv_dict(order_fxt)
#     response = await request_from_dict(SandboxEndPoints.SERVICE_AVAILABILITY, req_dict)
#     assert response['ServiceAvailability']['Messages']['Code'] == 'SUCCESS'
# 

@pytest.mark.asyncio
async def test_avail_v2(order_fxt):
    print(order_fxt.get_dict)


@pytest.mark.asyncio
async def test_item(dummy_item):
    print(dummy_item.get_dict)
    ...

@pytest.mark.asyncio
async def test_order(order_fxt):
    print(order_fxt.get_dict2)
    ...