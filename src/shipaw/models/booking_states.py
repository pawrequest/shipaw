# from __future__ import annotations, annotations

import datetime as dt

import pydantic as _p
import sqlmodel as sqm
from loguru import logger
from pawdantic.pawsql import default_json_field, optional_json_field, required_json_field

from shipaw.models import pf_shared
from shipaw.pf_config import pf_sett
from shipaw.ship_types import ShipDirection
from shipaw.models.pf_msg import Alerts, ShipmentResponse
from shipaw.models.pf_shipment import Shipment


class BookingState(sqm.SQLModel):
    shipment_request: Shipment = required_json_field(Shipment)
    response: ShipmentResponse | None = optional_json_field(ShipmentResponse)
    direction: ShipDirection = ShipDirection.Outbound
    label_downloaded: bool = False
    alerts: Alerts = default_json_field(Alerts, Alerts.empty)

    booked: bool = False
    tracking_logged: bool = False
    booking_date: dt.date = dt.date.today()
    label_path: str | None = None

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
            logger.debug('Setting collection times to null times from shipping date')
            self.shipment_request.collection_info.collection_time = pf_shared.DateTimeRange.null_times_from_date(
                self.shipment_request.shipping_date
            )
        return self

    def get_label_path(self):
        logger.debug(f'Getting label path for {self.pf_label_filestem}')
        sub_dir = pf_sett().label_dir
        if self.direction != 'out':
            sub_dir = sub_dir / self.direction
        lpath = (sub_dir / self.pf_label_filestem).with_suffix('.pdf')
        incremented = 2
        while lpath.exists():
            logger.warning(f'Label path {lpath} already exists')
            lpath = lpath.with_name(f'{lpath.stem}_{incremented}{lpath.suffix}')
            incremented += 1
        logger.debug(f'Using label path={lpath}')
        return lpath

    @property
    def pf_label_filestem(self):
        ln = (
            (
                f'Parcelforce {self.shipment_request.shipment_type.title()} Label '
                f'{f'from {self.shipment_request.collection_info.collection_contact.business_name} ' if self.shipment_request.collection_info else ''}'
                # f'{f'from {self.shipment_request.collection_info.collection_contact.business_name} ' if self.direction == 'in' else ''}'
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
