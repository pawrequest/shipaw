from __future__ import annotations

from pydantic import Field

from shipr.models.express import expresslink_pydantic as elp
from shipr.models.express.msg import (
    CancelShipmentResponse,
    CCReserveRequest,
    CCReserveResponse,
    CreateManifestRequest,
    CreateManifestResponse,
    PrintDocumentRequest,
    PrintDocumentResponse,
    PrintLabelRequest,
    PrintLabelResponse,
    PrintManifestRequest,
    PrintManifestResponse,
    ReturnShipmentRequest,
    ReturnShipmentResponse,
    FindResponse,
    CreatePrintRequest,
    CreatePrintResponse,
    CreateShipmentResponse,
    CreateShipmentRequest,
    CancelShipmentRequest,
    FindRequest,
)


class CancelShipmentResponse1(elp.BasePFType):
    cancel_shipment_reply: CancelShipmentResponse = Field(...)


class CCReserveRequest1(elp.BasePFType):
    cc_reserve_request: CCReserveRequest = Field(...)


class CCReserveResponse1(elp.BasePFType):
    cc_reserve_reply: CCReserveResponse = Field(...)


class CreateManifestRequest1(elp.BasePFType):
    create_manifest_request: CreateManifestRequest = Field(
        ...
    )


class CreateManifestResponse1(elp.BasePFType):
    create_manifest_reply: CreateManifestResponse = Field(...)


class PrintDocumentRequest1(elp.BasePFType):
    print_document_request: PrintDocumentRequest = Field(
        ...
    )


class PrintDocumentResponse1(elp.BasePFType):
    print_document_reply: PrintDocumentResponse = Field(...)


class PrintLabelRequest1(elp.BasePFType):
    print_label_request: PrintLabelRequest = Field(...)


class PrintLabelResponse1(elp.BasePFType):
    print_label_reply: PrintLabelResponse = Field(...)


class PrintManifestRequest1(elp.BasePFType):
    print_manifest_request: PrintManifestRequest = Field(
        ...
    )


class PrintManifestResponse1(elp.BasePFType):
    print_manifest_reply: PrintManifestResponse = Field(...)


class ReturnShipmentRequest1(elp.BasePFType):
    return_shipment_request: ReturnShipmentRequest = Field(
        ...
    )


class ReturnShipmentResponse1(elp.BasePFType):
    return_shipment_reply: ReturnShipmentResponse = Field(...)


class FindResponse1(elp.BasePFType):
    find_reply: FindResponse = Field(...)


class CreatePrintRequest1(elp.BasePFType):
    create_print_request: CreatePrintRequest = Field(...)


class CreatePrintResponse1(elp.BasePFType):
    create_print_reply: CreatePrintResponse = Field(...)


class CreateShipmentResponse1(elp.BasePFType):
    create_shipment_reply: CreateShipmentResponse = Field(...)


class CreateShipmentRequest1(elp.BasePFType):
    create_shipment_request: CreateShipmentRequest = Field(
        ...
    )


class CancelShipmentRequest1(elp.BasePFType):
    cancel_shipment_request: CancelShipmentRequest = Field(
        ...
    )


class FindRequest1(elp.BasePFType):
    find_request: FindRequest = Field(...)
