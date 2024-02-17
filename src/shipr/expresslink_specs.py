from enum import StrEnum
from typing import NamedTuple


class PFExpressApiEndpoint(StrEnum):
    TEST = 'https://expresslink-test.parcelforce.net/ws/'


class PFFunc(StrEnum):
    FIND = 'Find'


class PFBinding(StrEnum):
    SHIP = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'


class PFEndPointSpec(NamedTuple):
    function: PFFunc
    binding: PFBinding
    api_address: PFExpressApiEndpoint

    @classmethod
    def sandbox(cls, func: PFFunc):
        return cls(
            function=func,
            binding=PFBinding.SHIP,
            api_address=PFExpressApiEndpoint.TEST
        )

    @classmethod
    def find(cls):
        return cls(
            function=PFFunc.FIND,
            binding=PFBinding.SHIP,
            api_address=PFExpressApiEndpoint.TEST
        )


class PFDicts:
    @classmethod
    def _postcode_only(cls, postcode):
        return dict(Postcode=postcode)

    @classmethod
    def paf(cls, postcode):
        return dict(PAF=cls._postcode_only(postcode))
