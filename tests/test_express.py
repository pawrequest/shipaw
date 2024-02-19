import pytest
from dotenv import load_dotenv
from zeep.proxy import ServiceProxy
from zeep.helpers import serialize_object

import shipr.expresslink_specs
from shipr import expresslink2 as pf
from shipr.models.bases import obj_dict
from shipr.models.remixed import FindReply, PAF
from shipr.models.messages import FindFunc

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


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
    req = find_f.request_type(PAF=paf, Authentication=pf_client.auth)
    # dct = alias_dict(paf)
    dct = obj_dict(paf)
    req2 = find_f.request(**dct)
    resp = pf_client.get_response(req2, find_f)


    ser = serialize_object(resp)
    res = FindReply(**ser)
    ret = find_f.response_type.model_validate(res)
    ret2 = find_f.response_type.model_validate(ser)

    ser_paf = ser.get('PAF')
    val_paf = PAF(**ser_paf)
    resp_paf = resp.PAF
    # pro = pf_client.process_response(resp, pf_func=find_f)

    ...



    # param = RequestParams(params=[paf])
    # ath2 = pf_client.get_request(find_f, paf)
    # assert isinstance(resp, FindReply)
    # assert resp.paf.Postcode == 'NW6 4TE'
    ...
