import os

import pytest
from dotenv import load_dotenv
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object

import shipr.expresslink_specs
from shipr import expresslink2 as pf
from shipr.models.remixed import FindReply, PAF, FindRequest
from shipr.models.messages import FindFunc

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def pf_config(pf_auth2):
    wsdl = os.environ.get('PF_WSDL')
    return pf.PFConfig(wsdl, pf_auth2)


@pytest.fixture
def pf_client(pf_config):
    return pf.PFExpressLink(pf_config)


def test_client(pf_client):
    assert isinstance(pf_client, pf.PFExpressLink)


def test_get_service(pf_client):
    serv = pf_client.get_service(shipr.expresslink_specs.PFEndPointSpec.sandbox())
    assert isinstance(serv, ServiceProxy)


def test_get_response(pf_client):
    find_f = FindFunc()
    resp = pf_client.get_response(find_f, 'NW6 4TE')
    ...


def test_from_zeep(pf_client):
    find_f = FindFunc()
    resp = pf_client.get_response(find_f, 'NW6 4TE')

    resp_type = FindReply
    dct = serialize_object(resp, target_cls=dict)
    result = resp_type.model_validate(dct)
    assert isinstance(result, resp_type)
    ...


def test_find_func(pf_client):
    postcode = 'NW6 4TE'
    paf = PAF(Postcode=postcode)
    req = FindFunc.get_request(dict(paf=paf, Authentication=pf_client.auth))
    assert isinstance(req, FindFunc.request_type)


def test_process_request(pf_client):
    find_f = FindFunc()
    paf = PAF(postcode='NW6 4TE')
    ath2 = pf_client.get_ath_request(find_f, paf)
    resp = pf_client.process_request(ath2, find_f)
    ser = serialize_object(resp, target_cls=dict)
    assert FindReply.model_validate(ser)
    ...
