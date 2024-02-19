from __future__ import annotations

from pydantic import Field

import shipr.models.express.shared
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


class CancelShipmentResponse1(shipr.models.express.shared.BasePFType):
    cancel_shipment_reply: CancelShipmentResponse = Field(...)


class CCReserveRequest1(shipr.models.express.shared.BasePFType):
    cc_reserve_request: CCReserveRequest = Field(...)


class CCReserveResponse1(shipr.models.express.shared.BasePFType):
    cc_reserve_reply: CCReserveResponse = Field(...)


class CreateManifestRequest1(shipr.models.express.shared.BasePFType):
    create_manifest_request: CreateManifestRequest = Field(
        ...
    )


class CreateManifestResponse1(shipr.models.express.shared.BasePFType):
    create_manifest_reply: CreateManifestResponse = Field(...)


class PrintDocumentRequest1(shipr.models.express.shared.BasePFType):
    print_document_request: PrintDocumentRequest = Field(
        ...
    )


class PrintDocumentResponse1(shipr.models.express.shared.BasePFType):
    print_document_reply: PrintDocumentResponse = Field(...)


class PrintLabelRequest1(shipr.models.express.shared.BasePFType):
    print_label_request: PrintLabelRequest = Field(...)


class PrintLabelResponse1(shipr.models.express.shared.BasePFType):
    print_label_reply: PrintLabelResponse = Field(...)


class PrintManifestRequest1(shipr.models.express.shared.BasePFType):
    print_manifest_request: PrintManifestRequest = Field(
        ...
    )


class PrintManifestResponse1(shipr.models.express.shared.BasePFType):
    print_manifest_reply: PrintManifestResponse = Field(...)


class ReturnShipmentRequest1(shipr.models.express.shared.BasePFType):
    return_shipment_request: ReturnShipmentRequest = Field(
        ...
    )


class ReturnShipmentResponse1(shipr.models.express.shared.BasePFType):
    return_shipment_reply: ReturnShipmentResponse = Field(...)


class FindResponse1(shipr.models.express.shared.BasePFType):
    find_reply: FindResponse = Field(...)


class CreatePrintRequest1(shipr.models.express.shared.BasePFType):
    create_print_request: CreatePrintRequest = Field(...)


class CreatePrintResponse1(shipr.models.express.shared.BasePFType):
    create_print_reply: CreatePrintResponse = Field(...)


class CreateShipmentResponse1(shipr.models.express.shared.BasePFType):
    create_shipment_reply: CreateShipmentResponse = Field(...)


class CreateShipmentRequest1(shipr.models.express.shared.BasePFType):
    create_shipment_request: CreateShipmentRequest = Field(
        ...
    )


class CancelShipmentRequest1(shipr.models.express.shared.BasePFType):
    cancel_shipment_request: CancelShipmentRequest = Field(
        ...
    )


class FindRequest1(shipr.models.express.shared.BasePFType):
    find_request: FindRequest = Field(...)
