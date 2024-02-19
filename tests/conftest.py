import os

import pytest
from dotenv import load_dotenv

from shipr.el_combadge import ZeepConfig
from shipr.models.express.expresslink_pydantic import Authentication

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')

    auth = Authentication(user_name=username, password=password)
    return auth


@pytest.fixture
def zconfig(pf_auth):
    wsdl = os.environ.get('PF_WSDL')
    binding = os.environ.get('PF_BINDING')
    ep = os.environ.get('PF_ENDPOINT_SAND')
    return ZeepConfig(
        binding=binding,
        wsdl=wsdl,
        auth=pf_auth,
        endpoint=ep
    )
