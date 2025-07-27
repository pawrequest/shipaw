import datetime
from typing import Any, Generator

import pytest

from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressRecipient
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_top import Contact, RequestedShipmentMinimum
from shipaw.pf_config import pf_sandbox_sett, PFSandboxSettings
from shipaw.ship_types import DepartmentNum


@pytest.fixture
def sett():
    settings = pf_sandbox_sett()
    PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett) -> Generator[ELClient, Any, None]:
    yield ELClient(settings=sett)


@pytest.fixture
def address_r() -> AddressRecipient:
    return AddressRecipient(
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
def contact_collection(contact_r):
    contact_r.contact_name = 'Test Contact'
    return contact_r


