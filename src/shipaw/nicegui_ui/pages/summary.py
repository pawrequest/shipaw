"""
Step 2 — Order summary page.

Shows a read-only review of sender/recipient/details before confirming.
Calls *goto_results* on success or *goto_form* on back/error.
"""

from __future__ import annotations

from typing import Callable

from loguru import logger
from nicegui import ui

from shipaw.models.address_contact import FullContact
from shipaw.models.requests import ShipmentRequest
from shipaw.nicegui_ui import theme
from shipaw.utils.backend import resize_and_write_labels, try_book_shipment
from shipaw.utils.callbacks import ShipmentCallbackFn


def _fc_card(title: str, fc: FullContact) -> None:
    """Render a compact contact/address card."""
    with ui.card().classes(theme.CARD_SM):
        ui.label(title).classes('text-subtitle2 text-weight-bold')
        ui.separator()
        ui.label(fc.contact.name)
        ui.label(fc.address.business_name).classes('text-grey-7')
        for line in fc.address.address_lines:
            if line:
                ui.label(line)
        ui.label(fc.address.town)
        ui.label(fc.address.postcode)


class SummaryPage:
    """
    Renders the order-summary review step.

    Parameters
    ----------
    ship_req:     The request built on the form page.
    goto_form:    Callback to return to the form (Back button).
    goto_results: Callback(ship_req, response) called after a successful booking.
    """

    def __init__(
            self,
            ship_req: ShipmentRequest,
            goto_form: Callable,
            goto_results: Callable,
            on_booking: ShipmentCallbackFn | None = None
    ) -> None:
        self._ship_req = ship_req
        self._goto_form = goto_form
        self._goto_results = goto_results
        self._on_complete = on_booking
        self._build()

    def _build(self) -> None:
        shipment = self._ship_req.shipment

        with ui.card().classes(theme.CARD + ' q-mb-md'):
            ui.label(
                f'{shipment.direction.title()} — {self._ship_req.provider_name.replace("_", " ").title()} Shipment'
            ).classes('text-h6 text-weight-bold text-center q-mb-md')

            with ui.row().classes('w-full q-gutter-md justify-center'):
                if shipment.sender:
                    _fc_card('Sender', shipment.sender)
                _fc_card('Recipient', shipment.recipient)

                with ui.card().classes(theme.CARD_SM):
                    ui.label('Details').classes('text-subtitle2 text-weight-bold')
                    ui.separator()
                    ui.label(f'Boxes: {shipment.boxes}')
                    ui.label(f'Date: {shipment.shipping_date}')
                    ui.label(f'Service: {self._ship_req.service_code}')
                    ui.label(f'Reference: {shipment.reference or "—"}')

        with ui.row().classes(theme.CENTER_ROW):
            ui.button('← Back', on_click=self._goto_form).props(theme.BTN_FLAT)
            self._confirm_btn = (
                ui.button('Confirm Booking ✓', on_click=self._on_confirm, icon='check')
                .props(theme.BTN_POSITIVE)
                .classes('text-subtitle1 q-px-xl q-py-sm')
            )

    async def _on_confirm(self) -> None:
        self._confirm_btn.props('loading')
        self._confirm_btn.disable()
        navigated = False
        try:
            response = await try_book_shipment(self._ship_req)
            if self._on_complete and callable(self._on_complete):
                self._on_complete(self._ship_req, response)
            theme.show_alerts(response.alerts)
            if not response.alerts.errors:
                if response.label_data:
                    await resize_and_write_labels(response.label_data, response.label_path)
                navigated = True
                self._goto_results(self._ship_req, response)
        except Exception as exc:
            logger.exception(f'Booking error: {exc}')
            ui.notify(str(exc), type='negative', timeout=0)
        finally:
            if not navigated:
                self._confirm_btn.props(remove='loading')
                self._confirm_btn.enable()
