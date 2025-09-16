from enum import StrEnum
from typing import Literal, Self

from pydantic import ConfigDict

from shipaw.agnostic.agnost import ShippingService
from shipaw.apc.shared import APCBaseModel


class ProductCode(StrEnum):
    NEXT_DAY16 = 'ND16'
# ProductCode = Literal['ND16']


class APCService(ShippingService):
    code: ProductCode

    @classmethod
    def next_day_16(cls) -> Self:
        return cls(name='Next Day 16', code=ProductCode.NEXT_DAY16)


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
