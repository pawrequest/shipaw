from . import pf_msg

working_models = [
    pf_msg.PrintLabelRequest,
    pf_msg.PrintDocumentRequest,
    pf_msg.CreateManifestRequest,
    pf_msg.PrintManifestRequest,
    pf_msg.ReturnShipmentRequest,
    pf_msg.CCReserveRequest,
    pf_msg.CancelShipmentRequest

]

not_working_array_fields = [
    pf_msg.CreatePrintRequest,
    pf_msg.FindRequest,
    pf_msg.CreateRequest,

]
