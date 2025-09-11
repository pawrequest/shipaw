from pydantic import ConfigDict

from shipaw.apc.shared import APCBaseModel


class ServiceSpec(APCBaseModel):
    model_config = ConfigDict(extra='ignore')
    Carrier: str
    CollectionDate: str
    Currency: str
    DeliveryGroup: str
    EstimatedDeliveryDate: str
    ExtraCharges: str
    FuelCharge: str
    InsuranceCharge: str
    ItemType: str
    LatestBookingDateTime: str
    MaxCompensation: str
    MaxItemHeight: str
    MaxItemLength: str
    MaxItemWidth: str
    MaxTransitDays: str
    MinTransitDays: str
    ProductCode: str
    Rate: str
    ServiceName: str
    Signed: str
    TotalCost: str
    Tracked: str
    Vat: str
    VolumetricWeight: str
    WeightUnit: str


#
# class ServiceRequest(APCBaseModel):
#     collection_date: datetime.date
#     ready_at: datetime.time = time(hour=9)
#     closed_at: datetime.time = time(hour=17)
#     collection: AddressRough
#     delivery: AddressRough
#     goods_info: GoodsInfo
#     shipment_details: ShipmentDetails
#     delivery_group: str | None = None
