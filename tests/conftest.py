import os

import pytest
from dotenv import load_dotenv

from shipr.models.expresslink_pydantic import Authentication

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')

    auth = Authentication(user_name=username, password=password)
    return auth


