from enum import StrEnum
from typing import NamedTuple


class PFExpressApiEndpoint(StrEnum):
    TEST = 'https://expresslink-test.parcelforce.net/ws/'


class PFFunc(StrEnum):
    FIND = 'Find'


# use local WSDL?
class PFBinding(StrEnum):
    SHIP = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'


class PFEndPointSpec(NamedTuple):
    binding: PFBinding
    url: PFExpressApiEndpoint

    @classmethod
    def ship(cls):
        return cls(
            binding=PFBinding.SHIP,
            url=PFExpressApiEndpoint.TEST
        )


class PFDicts:
    @classmethod
    def _postcode_only(cls, postcode):
        return dict(Postcode=postcode)

    @classmethod
    def paf(cls, postcode):
        return dict(PAF=cls._postcode_only(postcode))
