import os

import pytest

import shipr.expresslink_specs
import shipr.shipr_types
from shipr import expresslink2 as pf, expresslink_specs2 as pf_specs


@pytest.fixture
def pf_endpoint():
    return shipr.expresslink_specs.PFEndPointSpec.ship()


@pytest.fixture
def pf_config(pf_auth, pf_endpoint):
    wsdl = os.environ.get('PF_WSDL')
    return pf.PFConfig(wsdl=wsdl, auth=pf_auth, pf_endpoint=pf_endpoint)


@pytest.fixture
def pf_client(pf_config):
    assert isinstance(pf_config, pf.PFConfig)
    return pf.PFExpressLink(pf_config)


def test_client(pf_client):
    assert isinstance(pf_client, pf.PFExpressLink)


def test_go_find(pf_client):
    resp = pf_client.addresses_from_postcode('NW6 4TE')
    assert resp
    ...


def test_go_find2(pf_client):
    try:
        serv = pf_client._client.service
        fnc = getattr(serv, 'Find')
        resp = fnc(
            Authentication=pf_client.config.auth.get_auth(),
            PAF={'Postcode': 'NW6 4TE'}
        )
        assert resp
    except Exception as e:
        ...

