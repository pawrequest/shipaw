import os

import pytest
from dotenv import load_dotenv
from zeep.proxy import ServiceProxy

from shipr import expresslink as pf, expresslink_specs as pf_specs

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def find_func():
    return pf_specs.PFFunc.FIND


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')
    auth = pf.PFAuth(username, password)
    return auth


@pytest.fixture
def pf_config(pf_auth):
    wsdl = os.environ.get('PF_WSDL')
    return pf.PFConfig(wsdl, pf_auth)


@pytest.fixture
def pf_client(pf_config):
    return pf.PFExpressLink(pf_config)


def test_client(pf_client):
    assert isinstance(pf_client, pf.PFExpressLink)


def test_get_service(pf_client):
    serv = pf_client.get_service(pf_specs.PFEndPointSpec.find())
    assert isinstance(serv, ServiceProxy)


def test_get_find_service(pf_client):
    serv = pf_client.find_service()
    assert isinstance(serv, ServiceProxy)


def test_find2(pf_client):
    find_serv = pf_client.find2()


def test_sandbox_spec():
    spec = pf_specs.PFEndPointSpec.sandbox(pf_specs.PFFunc.FIND)
    assert spec.function == pf_specs.PFFunc.FIND


def test_go_find(pf_client):
    resp = pf_client.addresses_from_postcode('NW6 4TE')
    assert resp
    ...
