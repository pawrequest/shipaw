import datetime

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
def el_client(sett):
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




"""
col_info = collection_contact = CollectionContact(
    business_name='Trampoline League',
    mobile_phone='07845 419917',
    email_address='jayne2911@gmail.com',
    contact_name='Jayne Armitage',
    telephone='07845 419917',
    senders_name='',
    notifications=CollectionNotifications(notification_type=['EMAIL']),
)
collection_address = AddressCollection(
    address_line1='98 KENPAS HIGHWAY',
    address_line2='',
    address_line3='',
    town='COVENTRY',
    postcode='CV3 6BQ',
    country='GB',
)
collection_time = DateTimeRange(from_='2024-04-23T09:00:00', to='2024-04-23T17:00:00')
"""
"""
collection_contact = CollectionContact(
    business_name='Test Business',
    mobile_phone='1234567890',
    email_address='notreal@fake.com',
    contact_name='Test Contact',
    telephone='07999999999',
    senders_name='',
    notifications=CollectionNotifications(notification_type=['EMAIL']),
)
collection_address = AddressRecipient(
    address_line1='30 Bennet Close',
    address_line2='',
    address_line3='',
    town='East Wickham',
    postcode='DA16 3HU',
    country='GB',
)
collection_time = DateTimeRange(from_='2024-04-23T09:00:00', to='2024-04-23T17:00:00')
"""
