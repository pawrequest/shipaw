from __future__ import annotations

from typing import Protocol

from typing_extensions import Annotated
from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name

from .express import msg

class FindService(SupportsService, Protocol):
    @operation_name("Find")
    def find(self, request: Annotated[msg.FindRequest, Payload(by_alias=True)]) -> msg.FindResponse:
        ...


class CreateShipmentService(SupportsService, Protocol):
    @operation_name("createShipment")
    def createshipment(
            self,
            request: Annotated[
                msg.CreateShipmentRequest, Payload(by_alias=True)],
    ) -> msg.CreateShipmentResponse:
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
            request: Annotated[msg.PrintLabelRequest, Payload(by_alias=True)],
    ) -> msg.PrintLabelResponse:
        ...
