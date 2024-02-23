from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import NamedTuple

from enum import StrEnum, auto
from pydantic import BaseModel


class PFExpressApiEndpoint(StrEnum):
    TEST = 'https://expresslink-test.parcelforce.net/ws/'


class PFBinding(StrEnum):
    SHIP = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'


class PFFuncName(StrEnum):
    Find = auto()


class PFFunc(ABC):
    def __init__(self, pf_func: PFFuncName):
        self._pf_func = pf_func

    def get_pf_dict(self, data) -> dict:
        raise NotImplementedError

    @property
    def name(self):
        return self._pf_func.name


class PFFunc2(ABC, BaseModel):
    name: str
    request_type: type[BaseModel]
    response_type: type[BaseModel]

    def get_pf_dict(self, data) -> dict:
        raise NotImplementedError


@dataclass
class PFDicts:
    @classmethod
    def _postcode_only(cls, postcode):
        return dict(
            Postcode=postcode
        )

    @classmethod
    def paf(cls, postcode):
        return dict(
            PAF=cls._postcode_only(postcode)
        )


class PFEndPointSpec(NamedTuple):
    binding: PFBinding
    api_address: PFExpressApiEndpoint

    @classmethod
    def sandbox(cls):
        return cls(
            binding=PFBinding.SHIP,
            api_address=PFExpressApiEndpoint.TEST
        )


class PFAddress(BaseModel):
    AddressLine1: str
    AddressLine2: str
    AddressLine3: str
    Town: str
    Postcode: str
    Country: str
