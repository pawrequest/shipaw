from __future__ import annotations

from datetime import date
from typing import Callable, Optional, Self, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, PositiveInt
from pydantic.alias_generators import to_snake
import sqlalchemy as sqa
import sqlmodel as sqm

from . import extended, shipr_shared as shared

if TYPE_CHECKING:
    from shipr import ELClient


class BaseUIState(sqm.SQLModel):
    model_config = ConfigDict(
        use_enum_values=True,
    )

    @staticmethod
    def call_and_get_method_query(method: Callable, *args, **kwargs) -> dict[str, str]:
        """returns {update_func name: jsonified result of update_func}"""
        json_res = method(*args, **kwargs).model_dump_json(exclude_none=True)
        return {to_snake(method.__name__): json_res}

    def update(self, updater: BookingStateUpdater) -> Self:
        """return a new BookingStateUpdate with the values of other merged into self."""
        for update in updater.model_fields_set:
            setattr(self, update, getattr(updater, update))
        return self

    def update_query(self) -> dict[str, str]:
        return {"updater": self.model_dump_json(exclude_none=True)}

    def update_get_query(self, *, updater: BookingStateUpdater) -> dict[str, str]:
        """returns {'update': updated json}"""
        return self.call_and_get_method_query(self.update, updater)


class BookingStateUpdater(BaseUIState):
    boxes: Optional[PositiveInt] = None
    ship_date: Optional[shared.ValidShipDate] = None
    ship_service: Optional[shared.ServiceCode] = None
    contact: Optional[extended.Contact] = sqm.Field(sa_column=sqa.Column(sqa.JSON))
    address: Optional[extended.AddressRecipient] = sqm.Field(sa_column=sqa.Column(sqa.JSON))
    input_address: Optional[extended.AddressRecipient] = sqm.Field(
        sa_column=sqa.Column(sqa.JSON)
    )


class Shipable(BaseModel):
    boxes: PositiveInt
    ship_date: shared.ValidShipDate
    ship_service: shared.ServiceCode
    contact: extended.Contact
    input_address: extended.AddressRecipient


# ContactJsonType = Annotated[extended.ContactPF, Column(el_json_types.ContactPFJsonType)]


class BookingStateIn(BookingStateUpdater):
    @classmethod
    def from_shipable(cls, shipable: Shipable) -> BookingStateIn:
        return cls(**shipable.model_dump())

    boxes: PositiveInt = sqm.Field(1)
    ship_date: shared.ValidShipDate = sqm.Field(default_factory=date.today)
    ship_service: shared.ServiceCode = shared.ServiceCode.EXPRESS24
    contact: extended.Contact = sqm.Field(sa_column=sqa.Column(sqa.JSON))
    address: extended.AddressRecipient = sqm.Field(sa_column=sqa.Column(sqa.JSON))

    @classmethod
    def hire_initial(cls, hire: Shipable, pfcom: ELClient) -> BookingStateIn:
        return cls(
            boxes=hire.boxes,
            ship_date=hire.ship_date,
            ship_service=shared.ServiceCode.EXPRESS24,
            contact=hire.contact,
            address=pfcom.choose_address(hire.input_address),
            # candidates=pfcom.get_candidates(hire.address.postcode),
        )
