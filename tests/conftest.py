import datetime

import pytest

from shipaw import ELClient, pf_config
from shipaw.models import pf_ext, pf_top
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import DepartmentNum


@pytest.fixture
def sett():
    settings = pf_config.sandbox_settings()
    pf_config.PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett):
    yield ELClient(settings=sett)


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
