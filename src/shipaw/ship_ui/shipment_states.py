from __future__ import annotations, annotations

import pathlib
from datetime import date

import pydantic as _p
import pydantic as pyd
import sqlmodel as sqm
from pydantic import ConfigDict
from loguru import logger

from shipaw import pf_config, ship_types
from shipaw.models import pf_models, pf_shared, pf_top
from shipaw.ship_types import PawdanticJSON, ShipDirection
from ..models.pf_lists import Alerts
from ..models.pf_msg import CreateShipmentResponse
from ..models.pf_shipment import ShipmentReferenceFields, ShipmentRequest
# from ..models.pf_shipment import ShipmentReferenceFields, ShipmentRequest
from ..models.pf_top import CollectionContact
from ..pf_config import pf_sett


class BookingState(sqm.SQLModel):
    requested_shipment: ShipmentRequest = sqm.Field(
        ...,
        sa_column=sqm.Column(ship_types.PawdanticJSON(ShipmentRequest))
    )
    response: CreateShipmentResponse | None = sqm.Field(
        None,
        sa_column=sqm.Column(ship_types.PawdanticJSON(CreateShipmentResponse))
    )
    direction: ShipDirection = 'out'
    label_downloaded: bool = False
    label_dl_path: pathlib.Path | None = None
    alerts: Alerts = sqm.Field(
        default_factory=list,
        sa_column=sqm.Column(PawdanticJSON(Alerts))
    )
    booked: bool = False

    @property
    def completed(self):
        if self.response:
            return self.response.completed_shipment_info is not None
        return False

    @_p.model_validator(mode='after')
    def get_alerts(self):
        if self.response:
            if self.response.alerts:
                # self.alert_dict = pawui_types.AlertDict({a.message: a.type for a in self.response.alerts.alert})
                self.alerts.append(self.response.alerts.alert)
        return self

    def shipment_num(self):
        return (
            self.response.completed_shipment_info.completed_shipments.completed_shipment[
                0].shipment_number
            if self.completed
            else None
        )

    # def state_alerts(self) -> list:
    #     return self.response.alerts.alert if self.response.alerts else []
    #
    # def alert_dict(self) -> dict[str, shipaw.types.AlertType]:
    #     return {a.message: a.type for a in self.state_alerts()}


class ShipmentPartial(ShipmentReferenceFields):
    boxes: pyd.PositiveInt | None = None
    service: pf_shared.ServiceCode | None = None
    ship_date: date | None = None
    contact: pf_top.Contact | None = None
    address: pf_models.AddressCollection | None = None
    direction: ShipDirection | None = None

    collection_times: pf_shared.DateTimeRange | None = None
    print_own_label: bool = True

    @property
    def pf_label_name(self):
        ln = f'Parcelforce {'DropOff' if self.direction == 'dropoff' else 'Collection'} Label for {self.contact.business_name} on {self.ship_date}'
        if not ln:
            logger.warning('pf_label_name not set')
        return ln

    @property
    def named_label_path(self):
        sett = pf_config.pf_sett()
        return (sett.label_dir / self.pf_label_name).with_suffix('.pdf')


class Shipment(ShipmentPartial):
    contact: pf_top.Contact
    address: pf_models.AddressCollection  # Recipient is more liberal with lengths, but differnetiating everywhere is tiresome
    ship_date: date
    boxes: pyd.PositiveInt = 1
    service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
    direction: ship_types.ShipDirection = 'out'

    @_p.field_validator('collection_times', mode='after')
    def validate_collection_times(cls, v, values):
        if values.data.get('direction') == 'in' and v is None:
            v = pf_shared.DateTimeRange.null_times_from_date(values.data.get('ship_date'))
        return v

    def shipment_request(self) -> ShipmentRequest:
        match self.direction:
            case 'in':
                return self.requested_shipment_inbound()
            case 'out':
                return self.requested_shipment_outbound()
            case 'dropoff':
                return self.requested_shipment_inbound_dropoff()

    def requested_shipment_outbound(self) -> ShipmentRequest:
        return ShipmentRequest(
            **self.standard_params,
            recipient_contact=self.contact,
            recipient_address=self.address,
        )

    def requested_shipment_inbound(self) -> ShipmentRequest:
        return ShipmentRequest(
            **self.standard_params,
            **self.collection_params,
            recipient_contact=pf_sett().home_contact,
            recipient_address=pf_sett().home_address,
        )

    def requested_shipment_inbound_dropoff(self) -> ShipmentRequest:
        return ShipmentRequest(
            **self.standard_params,
            recipient_contact=pf_sett().home_contact,
            recipient_address=pf_sett().home_address,
            shipment_type='DELIVERY',
        )

    @property
    def standard_params(self):
        return {
            'service_code': self.service,
            'shipping_date': self.ship_date,
            'total_number_of_parcels': self.boxes,
            'reference_number1': self.reference_number1,
            'special_instructions1': self.special_instructions1,
        }

    @property
    def collection_params(self):
        return {
            'shipment_type': 'COLLECTION',
            'print_own_label': self.print_own_label,
            'collection_info': pf_top.CollectionInfo(
                collection_contact=CollectionContact.model_validate(
                    self.contact.model_dump(exclude={'notifications'})
                ),
                collection_address=self.address,
                collection_time=pf_shared.DateTimeRange.null_times_from_date(self.ship_date),
            ),
        }


class ShipmentExtra(Shipment):
    model_config = ConfigDict(extra='ignore')


def response_alert_dict(response):
    return {a.message: a.type for a in response.alerts.alert} if response.alerts else {}


def shipment_alert_dict(booking_state: BookingState):
    return response_alert_dict(booking_state.response)


# class BookingStateDB(BookingState, table=True):
#     id: int | None = sqm.Field(primary_key=True)
