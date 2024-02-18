from __future__ import annotations

from abc import ABC
from typing import ClassVar, Sequence

from pydantic import BaseModel

from shipr.models import remixed as gen
from shipr.models.remixed import BaseResponse


class PFFunc3(ABC, BaseModel):
    name: str
    request_type: ClassVar[type[gen.BaseRequest]]
    response_type: ClassVar[type[BaseResponse]]

    @classmethod
    def get_auth_request(
            cls,
            auth: gen.Authentication,
            *data: gen.BasePFType
    ) -> gen.BaseRequest:
        req_dict = {d.__class__.__name__: d for d in
                    data}
        return cls.request_type(authentication=auth.model_dump(), **req_dict)

    # @classmethod
    # def get_auth_request(
    #         cls,
    #         auth: gen.Authentication,
    #         data: Sequence[gen.BasePFType]
    # ) -> gen.BaseRequest:
    #     req_dict = cls.get_request_dict(data)
    #     return cls.request_type(authentication=auth, **data)

    # @classmethod
    # def get_request(cls, data: Sequence[gen.BasePFType]) -> gen.BaseRequest:
    #     return cls.request_type(**cls.get_request_dict(data))

    @staticmethod
    def get_request_dict(data: Sequence[gen.BasePFType]) -> dict:
        unpacked = [_.model_dump() for _ in data]
        # up2 = [**_ for _ in unpacked]
        # unpacked2 = {k: v for _ in unpacked for k, v in _.items()}
        res = {
            name: value
            for _ in data
            for name, value in _.model_dump().items()
        }
        return res


class FindFunc(PFFunc3):
    name: str = 'Find'
    request_type = gen.FindRequest
    response_type = gen.FindReply

    # @classmethod
    # def get_request(cls, data: PAF) -> gen.FindRequest:
    #     dt = [_.model_dump() for _ in data]
    #     return cls.request_type()


class CCReserveFunc(PFFunc3):
    name: str = 'CCReserve'
    request_type = gen.CCReserveRequest
    response_type = gen.CCReserveReply


class CancelShipmentFunc(PFFunc3):
    name: str = 'CancelShipment'
    request_type = gen.CancelShipmentRequest
    response_type = gen.CancelShipmentReply


class PrintManifestFunc(PFFunc3):
    name: str = 'PrintManifest'
    request_type = gen.PrintManifestRequest
    response_type = gen.PrintManifestReply


class CreateManifestFunc(PFFunc3):
    name: str = 'CreateManifest'
    request_type = gen.CreateManifestRequest
    response_type = gen.CreateManifestReply


class CreateShipmentFunc(PFFunc3):
    name: str = 'CreateShipment'
    request_type = gen.CreateShipmentRequest
    response_type = gen.CreateShipmentReply


class PrintDocumentFunc(PFFunc3):
    name: str = 'PrintDocument'
    request_type = gen.PrintDocumentRequest
    response_type = gen.PrintDocumentReply


class ReturnShipmentFunc(PFFunc3):
    name: str = 'ReturnShipment'
    request_type = gen.ReturnShipmentRequest
    response_type = gen.ReturnShipmentReply


class PrintLabelFunc(PFFunc3):
    name: str = 'PrintLabel'
    request_type = gen.PrintLabelRequest
    response_type = gen.PrintLabelReply


class PrintLabel1Func(PFFunc3):
    name: str = 'PrintLabel1'
    request_type = gen.PrintLabelRequest1
    response_type = gen.PrintLabelReply1


class PrintManifest1Func(PFFunc3):
    name: str = 'PrintManifest1'
    request_type = gen.PrintManifestRequest1
    response_type = gen.PrintManifestReply1


class ReturnShipment1Func(PFFunc3):
    name: str = 'ReturnShipment1'
    request_type = gen.ReturnShipmentRequest1
    response_type = gen.ReturnShipmentReply1


class CCReserve1Func(PFFunc3):
    name: str = 'CCReserve1'
    request_type = gen.CCReserveRequest1
    response_type = gen.CCReserveReply1


class PrintDocument1Func(PFFunc3):
    name: str = 'PrintDocument1'
    request_type = gen.PrintDocumentRequest1
    response_type = gen.PrintDocumentReply1


class CancelShipment1Func(PFFunc3):
    name: str = 'CancelShipment1'
    request_type = gen.CancelShipmentRequest1
    response_type = gen.CancelShipmentReply1


class CreateManifest1Func(PFFunc3):
    name: str = 'CreateManifest1'
    request_type = gen.CreateManifestRequest1
    response_type = gen.CreateManifestReply1
