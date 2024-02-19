from __future__ import annotations

from typing import Protocol

from typing_extensions import Annotated
from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name

from shipr.models import expresslink_pydantic as elp


class FindService(SupportsService, Protocol):
    @operation_name("Find")
    def find(
            self,
            request: Annotated[elp.FindRequest, Payload(by_alias=True)],
    ) -> elp.FindReply:
        ...


class CCReserveService(SupportsService, Protocol):
    @operation_name("CCReserve")
    def ccreserve(
            self,
            request: Annotated[elp.CCReserveRequest, Payload(by_alias=True)],
    ) -> elp.CCReserveReply:
        ...


class CancelShipmentService(SupportsService, Protocol):
    @operation_name("CancelShipment")
    def cancelshipment(
            self,
            request: Annotated[elp.CancelShipmentRequest, Payload(by_alias=True)],
    ) -> elp.CancelShipmentReply:
        ...


class PrintManifestService(SupportsService, Protocol):
    @operation_name("PrintManifest")
    def printmanifest(
            self,
            request: Annotated[elp.PrintManifestRequest, Payload(by_alias=True)],
    ) -> elp.PrintManifestReply:
        ...


class CreateManifestService(SupportsService, Protocol):
    @operation_name("CreateManifest")
    def createmanifest(
            self,
            request: Annotated[elp.CreateManifestRequest, Payload(by_alias=True)],
    ) -> elp.CreateManifestReply:
        ...


class CreateShipmentService(SupportsService, Protocol):
    @operation_name("CreateShipment")
    def createshipment(
            self,
            request: Annotated[elp.CreateShipmentRequest, Payload(by_alias=True)],
    ) -> elp.CreateShipmentReply:
        ...


class PrintDocumentService(SupportsService, Protocol):
    @operation_name("PrintDocument")
    def printdocument(
            self,
            request: Annotated[elp.PrintDocumentRequest, Payload(by_alias=True)],
    ) -> elp.PrintDocumentReply:
        ...


class ReturnShipmentService(SupportsService, Protocol):
    @operation_name("ReturnShipment")
    def returnshipment(
            self,
            request: Annotated[elp.ReturnShipmentRequest, Payload(by_alias=True)],
    ) -> elp.ReturnShipmentReply:
        ...


class PrintLabelService(SupportsService, Protocol):
    @operation_name("PrintLabel")
    def printlabel(
            self,
            request: Annotated[elp.PrintLabelRequest, Payload(by_alias=True)],
    ) -> elp.PrintLabelReply:
        ...


class PrintLabel1Service(SupportsService, Protocol):
    @operation_name("PrintLabel1")
    def printlabel1(
            self,
            request: Annotated[elp.PrintLabelRequest1, Payload(by_alias=True)],
    ) -> elp.PrintLabelReply1:
        ...


class PrintManifest1Service(SupportsService, Protocol):
    @operation_name("PrintManifest1")
    def printmanifest1(
            self,
            request: Annotated[elp.PrintManifestRequest1, Payload(by_alias=True)],
    ) -> elp.PrintManifestReply1:
        ...


class ReturnShipment1Service(SupportsService, Protocol):
    @operation_name("ReturnShipment1")
    def returnshipment1(
            self,
            request: Annotated[elp.ReturnShipmentRequest1, Payload(by_alias=True)],
    ) -> elp.ReturnShipmentReply1:
        ...


class CCReserve1Service(SupportsService, Protocol):
    @operation_name("CCReserve1")
    def ccreserve1(
            self,
            request: Annotated[elp.CCReserveRequest1, Payload(by_alias=True)],
    ) -> elp.CCReserveReply1:
        ...


class PrintDocument1Service(SupportsService, Protocol):
    @operation_name("PrintDocument1")
    def printdocument1(
            self,
            request: Annotated[elp.PrintDocumentRequest1, Payload(by_alias=True)],
    ) -> elp.PrintDocumentReply1:
        ...


class CancelShipment1Service(SupportsService, Protocol):
    @operation_name("CancelShipment1")
    def cancelshipment1(
            self,
            request: Annotated[elp.CancelShipmentRequest1, Payload(by_alias=True)],
    ) -> elp.CancelShipmentReply1:
        ...


class CreateManifest1Service(SupportsService, Protocol):
    @operation_name("CreateManifest1")
    def createmanifest1(
            self,
            request: Annotated[elp.CreateManifestRequest1, Payload(by_alias=True)],
    ) -> elp.CreateManifestReply1:
        ...
