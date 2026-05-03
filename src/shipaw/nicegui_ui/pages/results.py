"""
Step 3 — Order results page.

Shows success (shipment number + label path + open/print buttons) or a failure
card listing the errors.  The only navigation is back to the form.
"""
from __future__ import annotations

import os
from typing import Callable

from nicegui import ui

from shipaw.nicegui_ui import theme
from shipaw.nicegui_ui.logic import ShipmentRequest


class ResultsPage:
    """
    Renders the post-booking results step.

    Parameters
    ----------
    ship_req:  The original request (kept for potential future use).
    response:  The :class:`~shipaw.nicegui_ui.logic.ShipmentResponse`.
    goto_form: Callback to start a new booking.
    """

    def __init__(self, ship_req: ShipmentRequest, response, goto_form: Callable) -> None:
        self._ship_req = ship_req
        self._response = response
        self._goto_form = goto_form
        self._build()

    def _build(self) -> None:
        response = self._response

        if response.alerts and response.alerts.errors:
            self._build_failure(response)
            return

        self._build_success(response)

    # ── Failure ───────────────────────────────────────────────────────────────

    def _build_failure(self, response) -> None:
        with ui.card().classes('w-full q-pa-xl result-fail text-center'):
            ui.icon('error', size='3rem').classes('text-negative')
            ui.label('Booking Failed').classes('text-h5 text-negative q-mt-sm')
            theme.render_alerts_inline(response.alerts)
        with ui.row().classes('w-full justify-center q-mt-md'):
            ui.button('← Try Again', on_click=self._goto_form).props(theme.BTN_PRIMARY)

    # ── Success ───────────────────────────────────────────────────────────────

    def _build_success(self, response) -> None:
        label_path = response.label_path

        with ui.card().classes('w-full q-pa-xl result-success text-center'):
            ui.icon('check_circle', size='3rem').classes('text-positive')
            ui.label('Shipment Confirmed!').classes('text-h5 text-positive q-mt-sm')
            ui.label(f'Shipment Number: {response.shipment_num}').classes('text-h6 q-mt-sm')
            ui.label(f'Label: {label_path}').classes('text-caption text-grey-7 q-mt-xs')

        with ui.row().classes('w-full justify-center q-gutter-lg q-mt-lg'):
            ui.button('Open Label', icon='open_in_new', on_click=lambda: self._open(label_path)).props(theme.BTN_PRIMARY)
            ui.button('Print Label', icon='print', on_click=lambda: self._print(label_path)).props(theme.BTN_PRIMARY)
            # Stage 3 TODO: email label button

        with ui.row().classes('w-full justify-center q-mt-xl'):
            ui.button('← New Booking', on_click=self._goto_form, icon='add').props(f'flat {theme.BTN_PRIMARY}')

    # ── Label actions ─────────────────────────────────────────────────────────

    @staticmethod
    def _open(label_path) -> None:
        try:
            os.startfile(label_path)
            ui.notify('Label opened', type='positive')
        except Exception as exc:
            ui.notify(str(exc), type='negative')

    @staticmethod
    def _print(label_path) -> None:
        try:
            os.startfile(label_path, 'print')
            ui.notify('Label sent to printer', type='positive')
        except Exception as exc:
            ui.notify(str(exc), type='negative')

