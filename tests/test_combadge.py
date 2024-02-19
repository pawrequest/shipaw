import datetime
import os

import pytest
from combadge.support.zeep.backends.sync import ZeepBackend
from dotenv import load_dotenv

from shipr.el_combadge import PFCom
from shipr.models.combadge_protocols import CreateShipmentService, FindService
from shipr.models.express.expresslink_pydantic import (
    DeliveryTypeEnum,
    DepartmentEnum,
    PAF,
    ServiceCode,
)
from shipr.models.express.address import Address, Contact
from shipr.models.express.msg import (
    CreateShipmentRequest,
    CreateShipmentResponse,
    FindRequest,
    FindResponse,
)
from shipr.models.express.shipment import RequestedShipmentMinimum
from .conftest import combadge_service

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)

CONTRACT_NO = os.environ.get('PF_CONT_NUM_1')


def test_find_paf(zconfig):
    pfc = PFCom.from_config(zconfig)
    service = ZeepBackend(pfc.service)[FindService]
    paf = PAF(postcode='NW6 4TE')
    req = FindRequest(authentication=zconfig.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], Address)


def test_get_shipment(min_shipment_r, service, pf_auth):
    cb = combadge_service(service, CreateShipmentService)
    req = CreateShipmentRequest(authentication=pf_auth, requested_shipment=min_shipment_r)
    resp: CreateShipmentResponse = cb.createshipment(request=req)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    assert isinstance(shipment_.shipment_number, str)


@pytest.fixture
def address_r() -> Address:
    return Address(
        address_line1='30 Bennet Close',
        town='East Wickham',
        postcode='DA16 3HU',
    )


@pytest.fixture
def contact_r() -> Contact:
    return Contact(
        business_name='Test Business',
        email_address='notreal@fake.com',
        mobile_phone='1234567890',
    )


@pytest.fixture
def min_shipment_r(address_r, contact_r) -> RequestedShipmentMinimum:
    return RequestedShipmentMinimum(
        department_id=DepartmentEnum.MAIN,
        shipment_type=DeliveryTypeEnum.DELIVERY,
        contract_number=CONTRACT_NO,
        service_code=ServiceCode.EXPRESS24,
        shipping_date=datetime.date(2024, 2, 21),
        recipient_contact=contact_r,
        recipient_address=address_r,
        total_number_of_parcels=1,
    )
