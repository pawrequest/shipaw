"""
Standalone business logic for the NiceGUI frontend.

All imports come from shipaw.models / shipaw.providers / shipaw.config / shipaw.utils —
NOT from shipaw.fapi — so the fapi module can be safely deleted.
"""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from pathlib import Path
from typing import Any

from apc_hypaship.error import apc_http_status_alerts
from httpx import HTTPStatusError
from loguru import logger
from pawdf.array_pdf.array_p import on_a4
from pydantic import Field

from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.alerts import Alerts, Alert, AlertType
from shipaw.models.base import ShipawBaseModel
from shipaw.models.responses import ShipmentResponse
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.utils.consts_enums import ShipDirection


# ── Alert models ──────────────────────────────────────────────────────────────

#
# class AlertType(StrEnum):
#     ERROR = 'ERROR'
#     WARNING = 'WARNING'
#     NOTIFICATION = 'NOTIFICATION'

#
# class Alert(ShipawBaseModel):
#     code: int | None = None
#     message: str
#     type: AlertType = AlertType.NOTIFICATION
#
#     def __eq__(self, other):
#         if not isinstance(other, Alert):
#             return NotImplemented
#         return (self.code, self.message, self.type) == (other.code, other.message, other.type)
#
#     def __hash__(self):
#         return hash((self.code, self.message, self.type))
#
#     @classmethod
#     def from_exception(cls, e: Exception):
#         return cls(message=str(e), type=AlertType.ERROR)


# class Alerts(ShipawBaseModel):
#     alert: list[Alert] = Field(default_factory=list)
#
#     @property
#     def errors(self):
#         return [a for a in self.alert if a.type == AlertType.ERROR]
#
#     @property
#     def warnings(self):
#         return [a for a in self.alert if a.type == AlertType.WARNING]
#
#     @property
#     def notifications(self):
#         return [a for a in self.alert if a.type == AlertType.NOTIFICATION]
#
#     def __bool__(self):
#         return bool(self.alert)
#
#     def __add__(self, other: Alerts | Alert):
#         if isinstance(other, Alert):
#             other = Alerts(alert=[other])
#         return Alerts(alert=list(set(self.alert) | set(other.alert)))
#
#     def __iadd__(self, other: Alerts | Alert):
#         if isinstance(other, Alert):
#             other = Alerts(alert=[other])
#         self.alert = list(set(self.alert) | set(other.alert))
#         return self
#
#     @classmethod
#     def empty(cls):
#         return cls(alert=[])
#

# ── ShipmentRequest model ─────────────────────────────────────────────────────


class ShipmentRequest(ShipawBaseModel):
    shipment: Shipment
    provider_name: ProviderName
    service_code: str

    @property
    def provider(self) -> ShippingProvider:
        if not self.provider_name:
            raise ValueError('Provider name is not set')
        if self.provider_name not in PROVIDER_REGISTER:
            raise ValueError(f'Unknown provider: {self.provider_name}')
        return PROVIDER_REGISTER[self.provider_name]


# ── Response model (minimal) ──────────────────────────────────────────────────

#
# class ShipmentResponse(ShipawBaseModel):
#     shipment: Shipment
#     alerts: Alerts = Field(default_factory=Alerts.empty)
#     label_data: bytes | None = None
#     shipment_num: str | None = None
#     shipment_numbers: list[str] = Field(default_factory=list)
#     tracking_links: list[str] = Field(default_factory=list)
#     collection_id: str | None = None
#     success: bool | None = None
#     _label_path: Path | None = None
#
#     @property
#     def label_path(self) -> Path:
#         from shipaw.config import SHIPAW_SETTINGS
#         from shipaw.utils.label_file import get_label_stem, unused_path
#         if self._label_path is None:
#             folder = SHIPAW_SETTINGS.label_dir / self.shipment.direction
#             label_stem = get_label_stem(self.shipment)
#             label_filepath = (folder / label_stem).with_suffix('.pdf')
#             self._label_path = unused_path(label_filepath)
#         return self._label_path


# ── Booking ───────────────────────────────────────────────────────────────────


async def try_book_shipment(shipment_request: ShipmentRequest) -> ShipmentResponse:
    response = ShipmentResponse(shipment=shipment_request.shipment)
    try:
        raw = shipment_request.provider.book_shipment_request(shipment_request)
        # coerce to our local ShipmentResponse
        response = ShipmentResponse.model_validate(raw, from_attributes=True)
    except HTTPStatusError as e:
        if shipment_request.provider_name == ProviderName.APC:
            for alert in await apc_http_status_alerts(e):
                response.alerts += alert
        else:
            logger.exception(e)
            response.alerts += Alert.from_exception(e)
    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        response.alerts += Alert.from_exception(e)
    return response


async def resize_and_write_labels(label_content: bytes, label_path: Path) -> None:
    og_path = label_path.parent / 'original_size' / label_path.name
    og_path.parent.mkdir(parents=True, exist_ok=True)
    og_path.write_bytes(label_content)
    logger.info(f'Resizing {og_path} → {label_path}')
    on_a4(input_file=og_path, output_file=label_path)
    logger.info(f'Wrote label to {label_path}')


# ── Validation helpers ────────────────────────────────────────────────────────


async def maybe_alert_apc(shipment_request: ShipmentRequest) -> Alerts:
    alerts = Alerts.empty()
    if (
        shipment_request.provider_name == ProviderName.APC
        and shipment_request.shipment.direction == ShipDirection.DROPOFF
    ):
        alerts += Alert(
            message='APC does not support drop-off shipments — please select Outbound or Inbound Collection',
            type=AlertType.ERROR,
        )
    return alerts


def notify_dev() -> Alerts:
    alerts = Alerts.empty()
    if any('prdev' in str(p).lower() for p in Path(__file__).parents):
        msg = '"prdev" in path tree — BETA MODE — development version'
        logger.info(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)
    return alerts


# ── Address lookup ────────────────────────────────────────────────────────────


def address_search_text(address: Address) -> str:
    fields = [address.business_name] + address.address_lines + [address.town, address.postcode]
    return ', '.join(f for f in fields if f)


async def address_search_summaries(search_text: str) -> list[Any]:
    """Call Royal Mail address search and return AddressSummaryDef list."""
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    if not provider:
        return []
    res = provider.client.address_search(search_text)
    return res.addresses


async def address_lookup(address: Address) -> list[Any]:
    """Return list of AddressRecordDef matching the address / postcode."""
    from shipaw.utils.funcs import compare_texts

    royalmail_provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    if not royalmail_provider:
        return []
    search_text = address_search_text(address)
    if not search_text.strip():
        return []

    postcode = address.postcode.strip()

    summaries = royalmail_provider.client.address_search(search_text).addresses
    # summaries = res.addresses
    # summaries = await address_search_summaries(search_text)

    hits = []
    for summary in summaries:
        if summary.type != 'Address':
            continue
        try:
            rec = royalmail_provider.client.address_retrieve(summary.address_id)
            if compare_texts(rec.postal_code, postcode):
                hits.append(rec)
        except Exception as exc:
            logger.warning(f'Address retrieve failed for {summary.address_id}: {exc}')
    return hits


# def retrieve_address(addr_id: str) -> Any | None:
#     """Retrieve a single AddressRecordDef by ID."""
#     provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
#     if not provider or not addr_id:
#         return None
#     try:
#         return provider.client.address_retrieve(addr_id)
#     except Exception as exc:
#         logger.exception(f'Address retrieve error for {addr_id}: {exc}')
#         return None


# ── Utilities ─────────────────────────────────────────────────────────────────


def make_nice_str(s: str) -> str:
    return s.replace('_', ' ').title()


# ── Shipment builder ──────────────────────────────────────────────────────────


def build_shipment(
    remote_fc: FullContact,
    reference: str,
    boxes: int | float,
    shipping_date: dt.date,
    direction: str,
    custom_sender_fc: FullContact | None = None,
) -> Shipment:
    """Construct a :class:`Shipment` from a remote contact and metadata.

    Parameters
    ----------
    remote_fc:
        The contact being shipped to (OUTBOUND) or collected from (INBOUND).
    custom_sender_fc:
        Optional explicit sender override.  When *None* the provider/config
        default applies (``Shipment.sender = None``).
    """
    from shipaw.config import SHIPAW_SETTINGS

    direction_e = ShipDirection(direction)
    if direction_e == ShipDirection.OUTBOUND:
        recipient = remote_fc
        sender = custom_sender_fc  # None → provider uses config default
    else:
        recipient = SHIPAW_SETTINGS.full_contact
        sender = remote_fc

    return Shipment(
        recipient=recipient,
        sender=sender,
        boxes=int(boxes or 1),
        shipping_date=shipping_date,
        direction=direction_e,
        reference=reference,
    )


