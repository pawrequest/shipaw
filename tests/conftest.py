import datetime
import os

import pytest

from shipaw import ELClient, ZeepConfig, pf_config
from shipaw.models import pf_ext, pf_shared, pf_top
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import DepartmentNum



@pytest.fixture
def sett():
    return pf_config.PF_SANDBOX_SETTINGS


# @pytest.fixture
# def pf_auth(sett):
#     auth = {'user_name': os.getenv('PF_EXPR_SAND_USR'), 'password': os.getenv('PF_EXPR_SAND_PWD')}
#     pfauth = pf_shared.Authentication.model_validate(auth)
#     return pfauth


@pytest.fixture
def pf_auth(sett):
    pfauth = pf_shared.Authentication.model_validate(
        {'user_name': sett.pf_expr_usr, 'password': sett.pf_expr_pwd}
    )
    return pfauth


@pytest.fixture
def zconfig(sett: pf_config.PFSandboxSettings, pf_auth):
    conf = ZeepConfig(binding=sett.pf_binding, wsdl=sett.pf_wsdl, auth=pf_auth, endpoint=sett.pf_endpoint)
    return conf


@pytest.fixture
def el_client():
    return ELClient.from_pyd(prod=False)


@pytest.fixture
def service(el_client):
    return el_client.new_service()


@pytest.fixture
def address_r() -> pf_ext.AddressRecipient:
    return pf_ext.AddressRecipient(
        address_line1='30 Bennet Close',
        town='East Wickham',
        postcode='DA16 3HU',
    )


@pytest.fixture
def contact_r() -> pf_top.Contact:
    return pf_top.Contact(
        business_name='Test Business',
        email_address='notreal@fake.com',
        mobile_phone='1234567890',
    )


@pytest.fixture
def min_shipment_r(address_r, contact_r, sett) -> pf_top.RequestedShipmentMinimum:
    return pf_top.RequestedShipmentMinimum(
        department_id=DepartmentNum,
        shipment_type='DELIVERY',
        contract_number=sett.pf_contract_num_1,
        service_code=ServiceCode.EXPRESS24,
        shipping_date=datetime.date.today() + datetime.timedelta(days=1),
        recipient_contact=contact_r,
        recipient_address=address_r,
        total_number_of_parcels=1,
    )
