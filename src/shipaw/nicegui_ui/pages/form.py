"""
Step 1 — Shipping form.

Builds the provider/direction/service dropdowns, contact fields, address
search, and submit button.  Navigation is injected via `on_submit` so this
module has no knowledge of the other pages.
"""

from __future__ import annotations

import datetime as dt
from typing import Callable

from loguru import logger
from nicegui import ui
from nicegui.elements.select import Select

from shipaw.config import SHIPAW_SETTINGS
from shipaw.models.alerts import Alerts
from shipaw.models.requests import ShipmentRequest
from shipaw.models.shipment import Shipment, sample_shipment
from shipaw.nicegui_ui.pages.address import AddressPanel
from shipaw.providers.provider_abc import ShippingProvider
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.nicegui_ui import theme
from shipaw.utils.consts_enums import ShipDirection
from shipaw.utils.ui_funcs import make_nice_str, str_to_nice_str_dict


def provider_names_sorted() -> list[str]:
    dflt = SHIPAW_SETTINGS.default_provider_name
    return sorted(PROVIDER_REGISTER.keys(), key=lambda p: p != dflt)


class FormPage:
    """
    Renders the shipping form and calls *on_submit* with a
    :class:`~shipaw.nicegui_ui.logic.ShipmentRequest` when the user submits.
    """

    def __init__(self, on_submit: Callable[[ShipmentRequest], None], initial: Shipment | None = None) -> None:
        self._current_provider: ShippingProvider | None = None
        initial = initial or sample_shipment()  # todo: remove this default once we have real data flowing through
        self._on_submit_cb = on_submit
        self._build(initial)

    @property
    def current_provider(self) -> ShippingProvider:
        if not self._current_provider or self._current_provider.name != self.provider_select.value:
            self._current_provider = PROVIDER_REGISTER[self.provider_select.value]
        return self._current_provider

    def _build(self, initial) -> None:
        # ── Shipment options ──────────────────────────────────────────────────
        with ui.card().classes(theme.CARD + ' q-mb-md'):
            ui.label('Shipment Options').classes('text-subtitle2 text-weight-bold q-mb-xs')
            with ui.row().classes('w-full items-end q-gutter-sm flex-wrap'):
                self.date_in = (
                    ui.input(label='Date', value=initial.shipping_date.isoformat())
                    .props(f'type=date {theme.INPUT_PROPS}')
                    .classes('col-auto')
                )
                self.boxes_in = (
                    ui.number(label='Boxes', value=initial.boxes, min=1, max=12, precision=0)
                    .props(theme.INPUT_PROPS)
                    .classes('col-auto')
                    .style('width: 90px')
                )
                self.reference_in = (
                    ui.input(label='Reference', value=initial.reference)
                    .props(f'{theme.INPUT_PROPS} maxlength=40')
                    .classes('col')
                )
                self.provider_select = self.provider_selector()
                self.direction_select = self.direction_selector()
                self.service_select = self.service_selector()

        # ── Recipient — shown for outbound only ───────────────────────────────
        with ui.expansion('Recipient', icon='person', value=True).classes(
                'w-full q-mt-sm ship-card'
        ) as self.recipient_expansion:
            self.recipient_panel = AddressPanel(
                initial_contact=initial.recipient.contact,
                initial_address=initial.recipient.address,
                show_use_own_phone=True,
            )

        # ── Sender — shown for inbound / dropoff only ─────────────────────────
        with ui.expansion('Sender', icon='person_add', value=True).classes(
                'w-full q-mt-sm ship-card'
        ) as self.sender_expansion:
            self.sender_panel = AddressPanel()

        # Apply initial visibility based on the default direction
        self._expand_addresses(self.direction_select.value or '')

        # ── Submit ────────────────────────────────────────────────────────────
        with ui.row().classes('w-full justify-center q-mt-lg'):
            self.submit_btn = (
                ui.button('Review Booking →', on_click=self._do_submit, icon='arrow_forward')
                .props(theme.BTN_PRIMARY)
                .classes('text-subtitle1 q-px-xl q-py-sm')
            )

    def provider_selector(self):
        prov_names = provider_names_sorted()
        default_provider_name = prov_names[0]
        prov_options = str_to_nice_str_dict(prov_names)
        selector = (
            ui.select(
                options=prov_options, label='Provider', value=default_provider_name, on_change=self._on_provider_change
            )
            .props(theme.INPUT_PROPS)
            .classes('col')
        )
        return selector

    def service_selector(self) -> Select:
        service_options, value = self._service_options()
        return ui.select(options=service_options, label='Service', value=value).props(theme.INPUT_PROPS).classes('col')

    def direction_selector(self) -> Select:
        valid_directions = list(self.current_provider.available_services.keys())
        default_dir = valid_directions[0]
        direction_options = str_to_nice_str_dict(valid_directions)
        selector = (
            ui.select(options=direction_options, label='Direction', value=default_dir)
            .props(theme.INPUT_PROPS)
            .classes('col')
        )
        selector.on_value_change(self._on_direction_change)
        return selector

    # ── Dropdown cascade ──────────────────────────────────────────────────────

    def _expand_addresses(self, direction: str) -> None:
        """Show the relevant address panel based on direction."""
        view_recip = direction in [ShipDirection.OUTBOUND, ShipDirection.THIRD_PARTY]
        view_sender = direction in [ShipDirection.INBOUND, ShipDirection.DROPOFF, ShipDirection.THIRD_PARTY]
        self.recipient_expansion.set_visibility(view_recip)
        self.sender_expansion.set_visibility(view_sender)

    async def _on_provider_change(self, e) -> None:
        self._current_provider = None  # refresh provider
        self._refresh_directions()
        await self._refresh_services()

    async def _on_direction_change(self, e) -> None:
        self._expand_addresses(e.value or '')
        await self._refresh_services()
        # await self._refresh_services(self.provider_select.value, e.value)

    def _refresh_directions(self):
        directions = self.current_provider.valid_directions
        dir_opts = str_to_nice_str_dict(directions)
        self.direction_select.options = dir_opts
        if self.direction_select.value not in directions:
            self.direction_select.value = directions[0] if directions else None
        self.direction_select.update()

    async def _refresh_services(self) -> None:
        opts, dflt_service = self._service_options()
        self.service_select.options = opts
        self.service_select.value = dflt_service
        self.service_select.update()

    def _service_options(self) -> tuple[dict[str, str], str | None]:
        direction = self.direction_select.value or ''
        available = self.current_provider.available_services.get(direction, [])
        opts = {s.value: make_nice_str(s.name) for s in available}
        return opts, available[0].value if available else None

    async def _do_submit(self) -> None:
        self.submit_btn.props('loading')
        try:
            raw_date = self.date_in.value
            ship_date = dt.date.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date
            shipment = Shipment(
                recipient=self.recipient_panel.to_full_contact() if self.recipient_expansion.visible else None,
                sender=self.sender_panel.to_full_contact() if self.sender_expansion.visible else None,
                boxes=self.boxes_in.value,
                shipping_date=ship_date,
                direction=self.direction_select.value,
                reference=self.reference_in.value,
            )
            ship_req = ShipmentRequest(
                shipment=shipment,
                provider_name=self.provider_select.value,
                service_code=self.service_select.value,
            )
            alerts = Alerts()  # todo:  real alerts
            theme.show_alerts(alerts)
            if not alerts.errors:
                self._on_submit_cb(ship_req)
        except Exception as exc:
            logger.exception(f'Submit error: {exc}')
            ui.notify(str(exc), type='negative', timeout=0)
        finally:
            self.submit_btn.props(remove='loading')
