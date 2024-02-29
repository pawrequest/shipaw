import datetime
import os

import pytest
from dotenv import load_dotenv

from shipr import ZeepConfig, ELClient
from shipr.models.shipr_shared import DeliveryKind, DepartmentNum, ServiceCode
from shipr.express.pf_shipment import RequestedShipmentMinimum
from shipr.express.pf_types import AddressPF, ContactPF, Authentication

ENV_FILE = r"../../amherst/.env"
load_dotenv(ENV_FILE)
CONTRACT_NO = os.environ.get("PF_CONT_NUM_1")
...


@pytest.fixture
def pf_auth():
    auth = {"user_name": os.getenv("PF_EXPR_SAND_USR"), "password": os.getenv("PF_EXPR_SAND_PWD")}
    pfauth = Authentication.model_validate(auth)
    return pfauth


@pytest.fixture
def zconfig(pf_auth):
    pf_auth = Authentication.model_validate(pf_auth)
    wsdl = os.environ.get("PF_WSDL")
    binding = os.environ.get("PF_BINDING")
    ep = os.environ.get("PF_ENDPOINT_SAND")
    conf = ZeepConfig(binding=binding, wsdl=wsdl, auth=pf_auth, endpoint=ep)
    return conf


@pytest.fixture
def pf_com(zconfig):
    return ELClient.from_config(zconfig)


@pytest.fixture
def service(pf_com):
    return pf_com.new_service()


@pytest.fixture
def address_r() -> AddressPF:
    return AddressPF(
        address_line1="30 Bennet Close",
        town="East Wickham",
        postcode="DA16 3HU",
    )


@pytest.fixture
def contact_r() -> ContactPF:
    return ContactPF(
        business_name="Test Business",
        email_address="notreal@fake.com",
        mobile_phone="1234567890",
    )


@pytest.fixture
def min_shipment_r(address_r, contact_r) -> RequestedShipmentMinimum:
    return RequestedShipmentMinimum(
        department_id=DepartmentNum.MAIN,
        shipment_type=DeliveryKind.DELIVERY,
        contract_number=CONTRACT_NO,
        service_code=ServiceCode.EXPRESS24,
        shipping_date=datetime.date(2024, 2, 21),
        recipient_contact=contact_r,
        recipient_address=address_r,
        total_number_of_parcels=1,
    )
