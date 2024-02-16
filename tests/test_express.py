import os

import pytest
from dotenv import load_dotenv
from zeep.proxy import ServiceProxy

import shipr.expresslink as pf

ENV_FILE = r'C:\Users\giles\prdev\am_dev\amherst\.env'
load_dotenv(ENV_FILE)


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


def tst_get_service(pf_client):
    serv = pf_client.get_service(pf.FIND)
    assert isinstance(serv, ServiceProxy)


def test_get_find_service(pf_client):
    serv = pf_client.find_service()
    assert isinstance(serv, ServiceProxy)


def test_find2(pf_client):
    find_serv = pf_client.find2()

    # serv = pf_client.find_service()
    # resp = getattr(serv, 'Find')(
    #     Authentication={'UserName': AUTH.user, 'Password': AUTH.pwd},
    #     PAF={'Postcode': 'NW6 4TE'}
    # )
    #
    # au = pf.PFAuth.get_auth()
    ...


def test_go_find(pf_client):
    resp = pf_client.go_find('NW6 4TE')
    assert resp
    ...
