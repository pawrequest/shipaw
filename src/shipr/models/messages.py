from shipr.expresslink_specs import PFFunc2
from shipr.models import generated as gen


class CCReserveFunc(PFFunc2):
    name = 'CCReserve'
    request = gen.CCReserveRequest
    response = gen.CCReserveReply


class CCReserve1Func(PFFunc2):
    name = 'CCReserve1'
    request = gen.CCReserveRequest1
    response = gen.CCReserveReply1


class CancelShipmentFunc(PFFunc2):
    name = 'CancelShipment'
    request = gen.CancelShipmentRequest
    response = gen.CancelShipmentReply


class CancelShipment1Func(PFFunc2):
    name = 'CancelShipment1'
    request = gen.CancelShipmentRequest1
    response = gen.CancelShipmentReply1


class CreateManifestFunc(PFFunc2):
    name = 'CreateManifest'
    request = gen.CreateManifestRequest
    response = gen.CreateManifestReply


class CreateManifest1Func(PFFunc2):
    name = 'CreateManifest1'
    request = gen.CreateManifestRequest1
    response = gen.CreateManifestReply1


class CreateShipmentFunc(PFFunc2):
    name = 'CreateShipment'
    request = gen.CreateShipmentRequest
    response = gen.CreateShipmentReply


class PrintDocumentFunc(PFFunc2):
    name = 'PrintDocument'
    request = gen.PrintDocumentRequest
    response = gen.PrintDocumentReply


class PrintDocument1Func(PFFunc2):
    name = 'PrintDocument1'
    request = gen.PrintDocumentRequest1
    response = gen.PrintDocumentReply1


class PrintLabelFunc(PFFunc2):
    name = 'PrintLabel'
    request = gen.PrintLabelRequest
    response = gen.PrintLabelReply


class PrintLabel1Func(PFFunc2):
    name = 'PrintLabel1'
    request = gen.PrintLabelRequest1
    response = gen.PrintLabelReply1


class PrintManifestFunc(PFFunc2):
    name = 'PrintManifest'
    request = gen.PrintManifestRequest
    response = gen.PrintManifestReply


class PrintManifest1Func(PFFunc2):
    name = 'PrintManifest1'
    request = gen.PrintManifestRequest1
    response = gen.PrintManifestReply1


class ReturnShipmentFunc(PFFunc2):
    name = 'ReturnShipment'
    request = gen.ReturnShipmentRequest
    response = gen.ReturnShipmentReply


class ReturnShipment1Func(PFFunc2):
    name = 'ReturnShipment1'
    request = gen.ReturnShipmentRequest1
    response = gen.ReturnShipmentReply1
