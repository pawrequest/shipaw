from __future__ import annotations

from abc import ABC
from typing import ClassVar, Sequence

from pydantic import BaseModel

import shipr.models.bases
import shipr.express_com
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
    request_type = shipr.express_com.FindRequest
    response_type = shipr.express_com.FindResponse


class CCReserveFunc(PFFunc):
    name: str = 'CCReserve'
    request_type = shipr.express_com.CCReserveRequest
    response_type = shipr.express_com.CCReserveResponse


class CancelShipmentFunc(PFFunc):
    name: str = 'CancelShipment'
    request_type = shipr.express_com.CancelShipmentRequest
    response_type = shipr.express_com.CancelShipmentResponse


class PrintManifestFunc(PFFunc):
    name: str = 'PrintManifest'
    request_type = shipr.express_com.PrintManifestRequest
    response_type = shipr.express_com.PrintManifestResponse


class CreateManifestFunc(PFFunc):
    name: str = 'CreateManifest'
    request_type = shipr.express_com.CreateManifestRequest
    response_type = shipr.express_com.CreateManifestResponse


class CreateShipmentFunc(PFFunc):
    name: str = 'CreateShipment'
    request_type = shipr.express_com.CreateShipmentRequest
    response_type = shipr.express_com.CreateShipmentResponse


class PrintDocumentFunc(PFFunc):
    name: str = 'PrintDocument'
    request_type = shipr.express_com.PrintDocumentRequest
    response_type = shipr.express_com.PrintDocumentResponse


class ReturnShipmentFunc(PFFunc):
    name: str = 'ReturnShipment'
    request_type = shipr.express_com.ReturnShipmentRequest
    response_type = shipr.express_com.ReturnShipmentResponse


class PrintLabelFunc(PFFunc):
    name: str = 'PrintLabel'
    request_type = elp.PrintLabelRequest
    response_type = shipr.express_com.PrintLabelResponse


class PrintLabel1Func(PFFunc):
    name: str = 'PrintLabel1'
    request_type = shipr.express_com.PrintLabelRequest1
    response_type = shipr.express_com.PrintLabelResponse1


class PrintManifest1Func(PFFunc):
    name: str = 'PrintManifest1'
    request_type = shipr.express_com.PrintManifestRequest1
    response_type = shipr.express_com.PrintManifestResponse1


class ReturnShipment1Func(PFFunc):
    name: str = 'ReturnShipment1'
    request_type = shipr.express_com.ReturnShipmentRequest1
    response_type = shipr.express_com.ReturnShipmentResponse1


class CCReserve1Func(PFFunc):
    name: str = 'CCReserve1'
    request_type = shipr.express_com.CCReserveRequest1
    response_type = shipr.express_com.CCReserveResponse1


class PrintDocument1Func(PFFunc):
    name: str = 'PrintDocument1'
    request_type = shipr.express_com.PrintDocumentRequest1
    response_type = shipr.express_com.PrintDocumentResponse1


class CancelShipment1Func(PFFunc):
    name: str = 'CancelShipment1'
    request_type = shipr.express_com.CancelShipmentRequest1
    response_type = shipr.express_com.CancelShipmentResponse1


class CreateManifest1Func(PFFunc):
    name: str = 'CreateManifest1'
    request_type = shipr.express_com.CreateManifestRequest1
    response_type = shipr.express_com.CreateManifestResponse1
