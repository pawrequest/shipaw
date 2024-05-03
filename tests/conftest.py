import datetime

import pytest

from shipaw import ELClient, Shipment, pf_config
from shipaw.models import pf_ext, pf_top
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import DepartmentNum


@pytest.fixture
def sett():
    settings = pf_config.pf_sandbox_sett()
    pf_config.PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett):
    yield ELClient(settings=sett)


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
def contact_collection(contact_r):
    contact_r.contact_name = 'Test Contact'
    return contact_r


@pytest.fixture
def shipment_outbound(address_r, contact_r, sett) -> pf_top.RequestedShipmentMinimum:
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


@pytest.fixture
def shipment():
    return Shipment(
        contact=pf_top.Contact(
            business_name='Test Business',
            mobile_phone='07999999999',
            email_address='fake@aslrksf.com',
            contact_name='Test Contact',
        ),
        address=pf_ext.AddressRecipient(
            address_line1='30 Bennet Close',
            town='East Wickham',
            postcode='DA16 3HU',
        ),
        ship_date=datetime.date.today() + datetime.timedelta(days=1),
    )


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
