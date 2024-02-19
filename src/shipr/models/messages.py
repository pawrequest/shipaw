from __future__ import annotations

from abc import ABC
from typing import ClassVar, Sequence

from pydantic import BaseModel

import shipr.models.bases
from shipr.models import expresslink_pydantic as elp
from shipr.models.bases import BaseResponse


class PFFunc(ABC, BaseModel):
    name: str
    request_type: ClassVar[type[shipr.models.bases.BaseRequest]]
    response_type: ClassVar[type[BaseResponse]]

    @classmethod
    def get_auth_request(
            cls,
            auth: elp.Authentication,
            params: Sequence[shipr.models.bases.BasePFType]
    ) -> shipr.models.bases.BaseRequest:
        ...

    def request(self, **params) -> shipr.models.bases.BaseRequest:
        return self.request_type(**params)


class FindFunc(PFFunc):
    name: str = 'Find'
    request_type = elp.FindRequest
    response_type = elp.FindResponse


class CCReserveFunc(PFFunc):
    name: str = 'CCReserve'
    request_type = elp.CCReserveRequest
    response_type = elp.CCReserveResponse


class CancelShipmentFunc(PFFunc):
    name: str = 'CancelShipment'
    request_type = elp.CancelShipmentRequest
    response_type = elp.CancelShipmentResponse


class PrintManifestFunc(PFFunc):
    name: str = 'PrintManifest'
    request_type = elp.PrintManifestRequest
    response_type = elp.PrintManifestResponse


class CreateManifestFunc(PFFunc):
    name: str = 'CreateManifest'
    request_type = elp.CreateManifestRequest
    response_type = elp.CreateManifestResponse


class CreateShipmentFunc(PFFunc):
    name: str = 'CreateShipment'
    request_type = elp.CreateShipmentRequest
    response_type = elp.CreateShipmentResponse


class PrintDocumentFunc(PFFunc):
    name: str = 'PrintDocument'
    request_type = elp.PrintDocumentRequest
    response_type = elp.PrintDocumentResponse


class ReturnShipmentFunc(PFFunc):
    name: str = 'ReturnShipment'
    request_type = elp.ReturnShipmentRequest
    response_type = elp.ReturnShipmentResponse


class PrintLabelFunc(PFFunc):
    name: str = 'PrintLabel'
    request_type = elp.PrintLabelRequest
    response_type = elp.PrintLabelResponse


class PrintLabel1Func(PFFunc):
    name: str = 'PrintLabel1'
    request_type = elp.PrintLabelRequest1
    response_type = elp.PrintLabelResponse1


class PrintManifest1Func(PFFunc):
    name: str = 'PrintManifest1'
    request_type = elp.PrintManifestRequest1
    response_type = elp.PrintManifestResponse1


class ReturnShipment1Func(PFFunc):
    name: str = 'ReturnShipment1'
    request_type = elp.ReturnShipmentRequest1
    response_type = elp.ReturnShipmentResponse1


class CCReserve1Func(PFFunc):
    name: str = 'CCReserve1'
    request_type = elp.CCReserveRequest1
    response_type = elp.CCReserveResponse1


class PrintDocument1Func(PFFunc):
    name: str = 'PrintDocument1'
    request_type = elp.PrintDocumentRequest1
    response_type = elp.PrintDocumentResponse1


class CancelShipment1Func(PFFunc):
    name: str = 'CancelShipment1'
    request_type = elp.CancelShipmentRequest1
    response_type = elp.CancelShipmentResponse1


class CreateManifest1Func(PFFunc):
    name: str = 'CreateManifest1'
    request_type = elp.CreateManifestRequest1
    response_type = elp.CreateManifestResponse1
