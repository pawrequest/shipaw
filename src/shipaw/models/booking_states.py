from __future__ import annotations, annotations

import datetime as dt

import pydantic as _p
import sqlmodel as sqm
from loguru import logger
from pawdantic.pawsql import default_json_field, optional_json_field, required_json_field
from pydantic import field_validator

from shipaw.models import pf_shared
from shipaw.pf_config import pf_sett
from shipaw.ship_types import ShipDirection
from shipaw.models.pf_msg import Alerts, CreateShipmentResponse
from shipaw.models.pf_shipment import ShipmentRequest


class BookingState(sqm.SQLModel):
    shipment_request: ShipmentRequest = required_json_field(ShipmentRequest)
    response: CreateShipmentResponse | None = optional_json_field(CreateShipmentResponse)
    direction: ShipDirection = ShipDirection.OUT
    label_downloaded: bool = False
    alerts: Alerts = default_json_field(Alerts, Alerts.empty)
    # alerts: Alerts | None = default_json_field(Alerts, Alerts)

    booked: bool = False
    tracking_logged: bool = False
    booking_date: dt.date = dt.date.today()
    label_path: str | None = None

    # @field_validator('label_path', mode='before')
    # def label_path_is_str(cls, v):
    #     if v:
    #         return str(v)

    @property
    def remote_contact(self):
        return (
            self.shipment_request.recipient_contact
            if self.direction == 'out'
            else self.shipment_request.collection_info.collection_contact
        )

    @property
    def remote_address(self):
        return (
            self.shipment_request.recipient_address
            if self.direction == 'out'
            else self.shipment_request.collection_info.collection_address
        )

    @_p.field_validator('booked', mode='after')
    def completed(cls, v, values):
        if v is False:
            if values.data['response'] and values.data['response'].completed_shipment_info:
                logger.warning('Booking has completed shipment data, setting booked to True')
                v = True
        return v

    @_p.model_validator(mode='after')
    def validate_collection_times(self):
        if self.direction == 'in' and self.shipment_request.collection_info.collection_time is None:
            self.shipment_request.collection_info.collection_time = pf_shared.DateTimeRange.null_times_from_date(
                self.shipment_request.shipping_date
            )
        return self

    def get_label_path(self):
        logger.debug(f'Getting label path for {self.pf_label_filestem}')
        lpath = (pf_sett().label_dir / self.direction / self.pf_label_filestem).with_suffix('.pdf')
        original_stem = lpath.stem
        incremented = 2
        while lpath.exists():
            logger.warning(f'Label path {lpath} already exists, trying {original_stem}_{incremented}{lpath.suffix}')
            lpath = lpath.with_name(f'{original_stem}_{incremented}{lpath.suffix}')
            incremented += 1
        return lpath

    @property
    def pf_label_filestem(self):
        ln = (
            (
                f'Parcelforce {'DropOff' if self.direction == ShipDirection.DROPOFF else 'Collection'} Label '
                f'{f'from {self.shipment_request.collection_info.collection_contact.business_name} ' if self.shipment_request.collection_info else ''}'
                f'to {self.shipment_request.recipient_contact.business_name}'
                f' on {self.shipment_request.shipping_date}'
            )
            .replace(' ', '_')
            .replace('/', '_')
            .replace(':', '-')
            .replace(',', '')
            .replace('.', '_')
        )
        return ln

    @property
    def status(self):
        return self.response.completed_shipment_info.status
