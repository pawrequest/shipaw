from combadge.support.zeep.backends.sync import ZeepBackend

from shipr.el_combadge import PFCom
from shipr.models.combadge_protocols import FindService
from shipr.models.express.expresslink_pydantic import Address, PAF
from shipr.models.express.msg import FindRequest, FindResponse


def test_find_paf(zconfig):
    pfc = PFCom.from_config(zconfig)
    service = ZeepBackend(pfc.service)[FindService]
    paf = PAF(postcode='NW6 4TE')
    req = FindRequest(authentication=zconfig.auth, paf=paf)
    response = service.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], Address)
