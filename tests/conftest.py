import os

import pytest
from dotenv import load_dotenv

from shipr import expresslink as pf

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')
    auth = pf.PFAuth(username, password)
    return auth

#
# @pytest.fixture
# def zeep_client(pf_auth):
#     username = pf_auth.user
#     password = pf_auth.pwd
#     try:
#         wsdl = r'C:\Users\RYZEN\prdev\workbench\shipr\resources\expresslink_api.wsdl'
#         session = Session()
#         session.auth = HTTPBasicAuth(username, password)
#         client = Client(wsdl=wsdl, transport=Transport(session=session))
#         return client
#     except Fault as fault:
#         parsed_fault_detail = client.wsdl.types.deserialize(fault.detail[0])
