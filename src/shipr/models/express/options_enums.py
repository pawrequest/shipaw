from __future__ import annotations

from typing import Optional

from pydantic import Field

from shipr.models.express.expresslink_pydantic import ConvenientCollect, SpecifiedPostOffice
from shipr.models.express.shared import BasePFType


class DeliveryOptions(BasePFType):
    convenient_collect: Optional[ConvenientCollect] = Field(
        None
    )
    irts: Optional[bool] = Field(None)
    letterbox: Optional[bool] = Field(None)
    specified_post_office: Optional[SpecifiedPostOffice] = Field(
        None
    )
    specified_neighbour: Optional[str] = Field(None)
    safe_place: Optional[str] = Field(None)
    pin: Optional[int] = Field(None)
    named_recipient: Optional[bool] = Field(None)
    address_only: Optional[bool] = Field(None)
    nominated_delivery_date: Optional[str] = Field(None)
    personal_parcel: Optional[str] = Field(None)
