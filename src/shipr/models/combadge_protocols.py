from __future__ import annotations

from typing import Protocol

from typing_extensions import Annotated
from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name

import shipr.models.express.msg
import shipr.models.express.with_1
from .express import msg


class FindService(SupportsService, Protocol):
    @operation_name("Find")
    def find(self, request: Annotated[msg.FindRequest, Payload(by_alias=True)]) -> msg.FindResponse:
        ...


class CCReserveService(SupportsService, Protocol):
    @operation_name("CCReserve")
    def ccreserve(
            self,
            request: Annotated[msg.CCReserveRequest, Payload(by_alias=True)],
    ) -> msg.CCReserveResponse:
        ...


class CancelShipmentService(SupportsService, Protocol):
    @operation_name("CancelShipment")
    def cancelshipment(
            self,
            request: Annotated[
                msg.CancelShipmentRequest, Payload(by_alias=True)],
    ) -> msg.CancelShipmentResponse:
        ...


class PrintManifestService(SupportsService, Protocol):
    @operation_name("PrintManifest")
    def printmanifest(
            self,
            request: Annotated[
                msg.PrintManifestRequest, Payload(by_alias=True)],
    ) -> msg.PrintManifestResponse:
        ...


class CreateManifestService(SupportsService, Protocol):
    @operation_name("CreateManifest")
    def createmanifest(
            self,
            request: Annotated[
                msg.CreateManifestRequest, Payload(by_alias=True)],
    ) -> msg.CreateManifestResponse:
        ...


class CreateShipmentService(SupportsService, Protocol):
    @operation_name("CreateShipment")
    def createshipment(
            self,
            request: Annotated[
                msg.CreateShipmentRequest, Payload(by_alias=True)],
    ) -> msg.CreateShipmentResponse:
        ...


class PrintDocumentService(SupportsService, Protocol):
    @operation_name("PrintDocument")
    def printdocument(
            self,
            request: Annotated[
                msg.PrintDocumentRequest, Payload(by_alias=True)],
    ) -> msg.PrintDocumentResponse:
        ...


class ReturnShipmentService(SupportsService, Protocol):
    @operation_name("ReturnShipment")
    def returnshipment(
            self,
            request: Annotated[
                msg.ReturnShipmentRequest, Payload(by_alias=True)],
    ) -> msg.ReturnShipmentResponse:
        ...


class PrintLabelService(SupportsService, Protocol):
    @operation_name("PrintLabel")
    def printlabel(
            self,
            request: Annotated[shipr.models.express.msg.PrintLabelRequest, Payload(by_alias=True)],
    ) -> msg.PrintLabelResponse:
        ...


class PrintLabel1Service(SupportsService, Protocol):
    @operation_name("PrintLabel1")
    def printlabel1(
            self,
            request: Annotated[
                shipr.models.express.with_1.PrintLabelRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.PrintLabelResponse1:
        ...


class PrintManifest1Service(SupportsService, Protocol):
    @operation_name("PrintManifest1")
    def printmanifest1(
            self,
            request: Annotated[
                shipr.models.express.with_1.PrintManifestRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.PrintManifestResponse1:
        ...


class ReturnShipment1Service(SupportsService, Protocol):
    @operation_name("ReturnShipment1")
    def returnshipment1(
            self,
            request: Annotated[
                shipr.models.express.with_1.ReturnShipmentRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.ReturnShipmentResponse1:
        ...


class CCReserve1Service(SupportsService, Protocol):
    @operation_name("CCReserve1")
    def ccreserve1(
            self,
            request: Annotated[
                shipr.models.express.with_1.CCReserveRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.CCReserveResponse1:
        ...


class PrintDocument1Service(SupportsService, Protocol):
    @operation_name("PrintDocument1")
    def printdocument1(
            self,
            request: Annotated[
                shipr.models.express.with_1.PrintDocumentRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.PrintDocumentResponse1:
        ...


class CancelShipment1Service(SupportsService, Protocol):
    @operation_name("CancelShipment1")
    def cancelshipment1(
            self,
            request: Annotated[
                shipr.models.express.with_1.CancelShipmentRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.CancelShipmentResponse1:
        ...


class CreateManifest1Service(SupportsService, Protocol):
    @operation_name("CreateManifest1")
    def createmanifest1(
            self,
            request: Annotated[
                shipr.models.express.with_1.CreateManifestRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.CreateManifestResponse1:
        ...
