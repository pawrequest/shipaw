from __future__ import annotations

from typing import Protocol

from combadge.support.http.markers import Payload
from typing_extensions import Annotated

from combadge.core.interfaces import SupportsService
from combadge.support.soap.markers import operation_name

import shipr.models


class PrintManifest1Service(SupportsService, Protocol):
    @operation_name("PrintManifest1")
    def printmanifest1(
            self,
            request: Annotated[
                shipr.models.express.with_1.PrintManifestRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.PrintManifestResponse1:
        ...


class PrintLabel1Service(SupportsService, Protocol):
    @operation_name("PrintLabel1")
    def printlabel1(
            self,
            request: Annotated[
                shipr.models.express.with_1.PrintLabelRequest1, Payload(by_alias=True)],
    ) -> shipr.models.express.with_1.PrintLabelResponse1:
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
