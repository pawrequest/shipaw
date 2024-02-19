import os

import pytest
from dotenv import load_dotenv
from combadge.support.zeep.backends.sync import ZeepBackend

from shipr.el_combadge import PFCom, ZeepConfig
from shipr.models.combadge_protocols import FindService
from shipr.models.expresslink_pydantic import (Address, FindRequest, FindResponse, PAF)

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)

WSDL = os.environ.get('PF_WSDL')


def test_find_paf(zconfig):
    pfc = PFCom.from_config(zconfig)
    service = ZeepBackend(pfc.service)[FindService]
    paf = PAF(postcode='NW6 4TE')
    req = FindRequest(authentication=zconfig.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], Address)
