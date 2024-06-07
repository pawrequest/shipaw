from __future__ import annotations

from typing import Annotated, Protocol

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name

from . import pf_msg


class FindService(SupportsService, Protocol):
    @operation_name('Find')
    def find(
            self,
            request: Annotated[pf_msg.FindRequest, Payload(by_alias=True)]
    ) -> pf_msg.FindResponse:
        ...


class CreateShipmentService(SupportsService, Protocol):
    @operation_name('createShipment')
    def createshipment(
            self,
            request: Annotated[pf_msg.CreateRequest, Payload(by_alias=True)],
    ) -> pf_msg.CreateShipmentResponse:
        ...


class CCReserveService(SupportsService, Protocol):
    @operation_name('CCReserve')
    def ccreserve(
            self,
            request: Annotated[pf_msg.CCReserveRequest, Payload(by_alias=True)],
    ) -> pf_msg.CCReserveResponse:
        ...


class CancelShipmentService(SupportsService, Protocol):
    @operation_name('CancelShipment')
    def cancelshipment(
            self,
            request: Annotated[pf_msg.CancelShipmentRequest, Payload(by_alias=True)],
    ) -> pf_msg.CancelShipmentResponse:
        ...


class PrintManifestService(SupportsService, Protocol):
    @operation_name('printManifest')
    def printmanifest(
            self,
            request: Annotated[pf_msg.PrintManifestRequest, Payload(by_alias=True)],
    ) -> pf_msg.PrintManifestResponse:
        ...


class CreateManifestService(SupportsService, Protocol):
    @operation_name('createManifest')
    def createmanifest(
            self,
            request: Annotated[pf_msg.CreateManifestRequest, Payload(by_alias=True)],
    ) -> pf_msg.CreateManifestResponse:
        ...


class PrintDocumentService(SupportsService, Protocol):
    @operation_name('printDocument')
    def printdocument(
            self,
            request: Annotated[pf_msg.PrintDocumentRequest, Payload(by_alias=True)],
    ) -> pf_msg.PrintDocumentResponse:
        ...


class ReturnShipmentService(SupportsService, Protocol):
    @operation_name('returnShipment')
    def returnshipment(
            self,
            request: Annotated[pf_msg.ReturnShipmentRequest, Payload(by_alias=True)],
    ) -> pf_msg.ReturnShipmentResponse:
        ...


class PrintLabelService(SupportsService, Protocol):
    @operation_name('printLabel')
    def printlabel(
            self,
            request: Annotated[pf_msg.PrintLabelRequest, Payload(by_alias=True)],
    ) -> pf_msg.PrintLabelResponse:
        ...
