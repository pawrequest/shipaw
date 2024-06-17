from __future__ import annotations, annotations

import functools
import datetime as dt
import pydantic as _p
import sqlmodel as sqm
from loguru import logger
from pawdantic.pawsql import optional_json_field, required_json_field, default_json_field

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
    # alerts: Alerts | None = optional_json_field(Alerts)
    alerts: Alerts | None = default_json_field(Alerts, Alerts)

    booked: bool = False
    tracking_logged: bool = False
    booking_date: dt.date = dt.date.today()

    @property
    def remote_contact(self):
        return self.shipment_request.recipient_contact if self.direction == 'out' else self.shipment_request.collection_info.collection_contact

    @property
    def remote_address(self):
        return self.shipment_request.recipient_address if self.direction == 'out' else self.shipment_request.collection_info.collection_address

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

    # @functools.lru_cache
    @functools.cached_property
    def label_path(self):
        lpath = (pf_sett().label_dir / self.direction / self.pf_label_filestem).with_suffix('.pdf')
        original_stem = lpath.stem
        suffix = 2
        while lpath.exists():
            lpath = lpath.with_name(f'{original_stem}_{suffix}{lpath.suffix}')
            suffix += 1
        return lpath

    @property
    def pf_label_filestem(self):
        ln = (
            f'Parcelforce {'DropOff' if self.direction == ShipDirection.DROPOFF else 'Collection'} Label '
            f'{f'from {self.shipment_request.collection_info.collection_contact.business_name} ' if self.shipment_request.collection_info else ''}'
            f'to {self.shipment_request.recipient_contact.business_name}'
            f' on {self.shipment_request.shipping_date}')
        if not ln:
            logger.warning('pf_label_name not set')
        return ln

    # def collection_params(self):
    #     return {
    #         'shipment_type': 'COLLECTION',
    #         'print_own_label': True,
    #         'collection_info': pf_top.CollectionInfo(
    #             collection_contact=CollectionContact.model_validate(
    #                 self.shipment_request.recipient_contact.model_dump(exclude={'notifications'})
    #             ),
    #             collection_address=self.shipment_request.,
    #             collection_time=pf_shared.DateTimeRange.null_times_from_date(self.ship_date),
    #         ),
    #     }

    # @_p.model_validator(mode='after')
    # def get_alerts(self):
    #     if self.response:
    #         if self.response.alerts:
    #             self.alerts.alert.extend(self.response.alerts.alert)
    #     return self


    # @property
    # def shipment_num(self):
    #     return (
    #         self.response.completed_shipment_info.completed_shipments.completed_shipment[
    #             0].shipment_number
    #         if self.response.completed_shipment_info
    #         else None
    #     )

    @property
    def status(self):
        return self.response.completed_shipment_info.status

# class ShipmentPartial(ShipmentReferenceFields):
#     boxes: pyd.PositiveInt | None = None
#     service: pf_shared.ServiceCode | None = None
#     ship_date: date | None = None
#     contact: pf_top.Contact | None = None
#     address: pf_models.AddressCollection | None = None
#     direction: ShipDirection | None = None
#
#     collection_times: pf_shared.DateTimeRange | None = None
#     print_own_label: bool = True
#
#     @property
#     def pf_label_name(self):
#         ln = f'Parcelforce {'DropOff' if self.direction == 'dropoff' else 'Collection'} Label for {self.contact.business_name} on {self.ship_date}'
#         if not ln:
#             logger.warning('pf_label_name not set')
#         return ln
#
#     @property
#     def named_label_path(self):
#         sett = pf_config.pf_sett()
#         return (sett.label_dir / self.pf_label_name).with_suffix('.pdf')
#
#
# class Shipment(ShipmentPartial):
#     contact: pf_top.Contact
#     address: pf_models.AddressCollection  # Recipient is more liberal with lengths, but differnetiating everywhere is tiresome
#     ship_date: date
#     boxes: pyd.PositiveInt = 1
#     service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24
#     direction: ship_types.ShipDirection = 'out'
#
#     @_p.field_validator('collection_times', mode='after')
#     def validate_collection_times(cls, v, values):
#         if values.data.get('direction') == 'in' and v is None:
#             v = pf_shared.DateTimeRange.null_times_from_date(values.data.get('ship_date'))
#         return v
#
#     def shipment_request(self) -> ShipmentRequest:
#         match self.direction:
#             case 'in':
#                 return self.requested_shipment_inbound()
#             case 'out':
#                 return self.requested_shipment_outbound()
#             case 'dropoff':
#                 return self.requested_shipment_inbound_dropoff()
#
#     def requested_shipment_outbound(self) -> ShipmentRequest:
#         return ShipmentRequest(
#             **self.standard_params,
#             recipient_contact=self.contact,
#             recipient_address=self.address,
#         )
#
#     def requested_shipment_inbound(self) -> ShipmentRequest:
#         return ShipmentRequest(
#             **self.standard_params,
#             **self.collection_params,
#             recipient_contact=pf_sett().home_contact,
#             recipient_address=pf_sett().home_address,
#         )
#
#     def requested_shipment_inbound_dropoff(self) -> ShipmentRequest:
#         return ShipmentRequest(
#             **self.standard_params,
#             recipient_contact=pf_sett().home_contact,
#             recipient_address=pf_sett().home_address,
#             shipment_type='DELIVERY',
#         )
#
#     @property
#     def standard_params(self):
#         return {
#             'service_code': self.service,
#             'shipping_date': self.ship_date,
#             'total_number_of_parcels': self.boxes,
#             'reference_number1': self.reference_number1,
#             'special_instructions1': self.special_instructions1,
#         }
#
#     @property
#     def collection_params(self):
#         return {
#             'shipment_type': 'COLLECTION',
#             'print_own_label': self.print_own_label,
#             'collection_info': pf_top.CollectionInfo(
#                 collection_contact=CollectionContact.model_validate(
#                     self.contact.model_dump(exclude={'notifications'})
#                 ),
#                 collection_address=self.address,
#                 collection_time=pf_shared.DateTimeRange.null_times_from_date(self.ship_date),
#             ),
#         }
#
#
# class ShipmentExtra(Shipment):
#     model_config = ConfigDict(extra='ignore')
#
#
# def response_alert_dict(response):
#     return {a.message: a.type for a in response.alerts.alert} if response.alerts else {}
#
#
# def shipment_alert_dict(booking_state: BookingState):
#     return response_alert_dict(booking_state.response)
