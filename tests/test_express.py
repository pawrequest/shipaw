import json
import os

import pytest
from dotenv import load_dotenv
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object

import shipr.expresslink_specs
from shipr import expresslink as pf
from shipr.expresslink_specs import FindFunc
from shipr.models.generated import FindReply, PAF

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


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
    serv = pf_client.get_service(shipr.expresslink_specs.PFEndPointSpec.sandbox())
    assert isinstance(serv, ServiceProxy)


def test_get_response(pf_client):
    find_f = FindFunc()
    resp = pf_client.get_response(find_f, 'NW6 4TE')
    ...


def test_models(pf_client):
    find_f = FindFunc()
    resp = pf_client.get_response(find_f, 'NW6 4TE')
    # resp_dict = resp.__dict__['__values__']
    res = PAF.model_validate(resp.PAF)
    ...


def test_from_zeep(pf_client):
    find_f = FindFunc()
    resp = pf_client.get_response(find_f, 'NW6 4TE')

    resp_type = FindReply
    subtype = PAF
    subres = resp[subtype.__name__]
    dct = serialize_object(resp, target_cls=dict)
    result = resp_type.model_validate(dct)
    ...
