import os
from typing import NamedTuple

from dotenv import load_dotenv
from zeep import Client, Settings, Transport

from shipr.expresslink import PFDicts

ENV_FILE = r'C:\Users\giles\prdev\am_dev\amherst\.env'

load_dotenv(ENV_FILE)

WSDL = os.environ.get('PF_WSDL')
username = os.getenv('PF_EXPR_SAND_USR')
password = os.getenv('PF_EXPR_SAND_PWD')
settings = Settings()

transport = Transport(timeout=10)

client = Client(wsdl=WSDL, settings=settings, transport=transport)

test_url = 'https://expresslink-test.parcelforce.net/ws/'

service = client.create_service(
    '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding',
    test_url
)


class PFAuth(NamedTuple):
    user: str
    pwd: str


postcode = 'NW6 4TE'

Auth = PFAuth(username, password)

response = service.Find(
    Authentication=dict(
        UserName=Auth.user,
        Password=Auth.pwd,
    ),
    **PFDicts.paf(postcode)
)

print(response)
