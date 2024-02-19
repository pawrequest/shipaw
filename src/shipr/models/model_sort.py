import shipr.models.documents
import shipr.models.pf_responses
import shipr.models.pf_types
import shipr.models.requests
import shipr.models.simple
from . import remixed as pfgen

class PFType:

    ADDRESS = shipr.models.pf_types.Address
    ALERT_TYPE = shipr.models.pf_types.AlertType
    AUTHENTICATION = shipr.models.pf_types.Authentication
    BARCODE = shipr.models.documents.Barcode
    COMPLETED_CANCEL_INFO = shipr.models.pf_types.CompletedCancelInfo
    COMPLETED_RETURN_INFO = shipr.models.pf_types.CompletedReturnInfo
    COMPLETED_SHIPMENT = shipr.models.pf_types.CompletedShipment
    COMPLETED_SHIPMENT_INFO = shipr.models.pf_types.CompletedShipmentInfo
    CONTACT = shipr.models.pf_types.Contact
    CONTENT_DATA = shipr.models.pf_types.ContentData
    CONTENT_DETAIL = shipr.models.pf_types.ContentDetail
    CONVENIENT_COLLECT = shipr.models.pf_types.ConvenientCollect
    DATE_TIME_RANGE = shipr.models.pf_types.DateTimeRange
    DELIVERY_OPTIONS = shipr.models.pf_types.DeliveryOptions
    DOCUMENT = shipr.models.documents.Document
    ENHANCEMENT = shipr.models.pf_types.Enhancement
    HAZARDOUS_GOOD = shipr.models.pf_types.HazardousGood
    HOURS = shipr.models.pf_types.Hours
    IMAGE = shipr.models.documents.Image
    LABEL_ITEM = shipr.models.documents.LabelItem
    MANIFEST_SHIPMENT = shipr.models.pf_types.ManifestShipment
    NOMINATED_DELIVERY_DATE_LIST = shipr.models.pf_types.NominatedDeliveryDateList
    PAF = shipr.models.pf_types.PAF
    PARCEL = shipr.models.simple.Parcel
    PARCELS = shipr.models.simple.Parcels
    POSITION = shipr.models.pf_types.Position
    PRINT_TYPE = shipr.models.documents.PrintType
    REQUESTED_SHIPMENT = shipr.models.pf_types.RequestedShipment
    RETURNS = shipr.models.pf_types.Returns
    SAFE_PLACE_LIST = shipr.models.pf_types.SafePlaceList
    SERVICE_CODES = shipr.models.pf_types.ServiceCodes
    SPECIFIED_NEIGHBOUR = shipr.models.pf_types.SpecifiedNeighbour
    SPECIFIED_POST_OFFICE = shipr.models.pf_types.SpecifiedPostOffice

    IN_BOUND_DETAILS = shipr.models.pf_types.InBoundDetails
    HAZARDOUS_GOODS = shipr.models.pf_types.HazardousGoods
    CONTENT_DETAILS = shipr.models.pf_types.ContentDetails
    COLLECTION_INFO = shipr.models.pf_types.CollectionInfo
    PARCEL_CONTENTS = shipr.models.pf_types.ParcelContents
    LABEL_DATA = shipr.models.documents.LabelData









class Response:
    BASE = shipr.models.pf_responses.BaseReply
    CREATE_PRINT = shipr.models.pf_responses.CreatePrintReply
    PRINT_LABEL = shipr.models.pf_responses.PrintLabelReply
    PRINT_DOCUMENT = shipr.models.pf_responses.PrintDocumentReply
    CREATE_MANIFEST = shipr.models.pf_responses.CreateManifestReply
    PRINT_MANIFEST = shipr.models.pf_responses.PrintManifestReply
    RETURN_SHIPMENT = shipr.models.pf_responses.ReturnShipmentReply
    CC_RESERVE = shipr.models.pf_responses.CCReserveReply
    CANCEL_SHIPMENT = shipr.models.pf_responses.CancelShipmentReply
    FIND = shipr.models.pf_responses.FindReply
    CREATE_SHIPMENT = shipr.models.pf_responses.CreateShipmentReply



class Request:
    BASE = shipr.models.requests.BaseRequest
    PRINT_LABEL = shipr.models.requests.PrintLabelRequest
    PRINT_DOCUMENT = shipr.models.requests.PrintDocumentRequest
    CREATE_MANIFEST = shipr.models.requests.CreateManifestRequest
    PRINT_MANIFEST = shipr.models.requests.PrintManifestRequest
    RETURN_SHIPMENT = shipr.models.requests.ReturnShipmentRequest
    CC_RESERVE = shipr.models.requests.CCReserveRequest
    CANCEL_SHIPMENT = shipr.models.requests.CancelShipmentRequest
    FIND = shipr.models.requests.FindRequest
    CREATE_SHIPMENT = shipr.models.requests.CreateShipmentRequest
    CREATE_PRINT = shipr.models.requests.CreatePrintRequest




