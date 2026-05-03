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

from shipaw.config import SHIPAW_SETTINGS
from shipaw.models.address import Address, Contact, FullContact
from shipaw.models.shipment import sample_shipment
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.nicegui_ui import theme
from shipaw.nicegui_ui.logic import (
    ShipmentRequest,
    address_lookup,
    build_shipment,
    make_nice_str,
    maybe_alert_apc,
)



# ── Provider / direction / service option helpers ─────────────────────────────


def _provider_options() -> tuple[dict[str, str], str | None]:
    """Return ({value: label}, default_value) for provider select."""
    dflt = SHIPAW_SETTINGS.default_provider_name
    keys = sorted(PROVIDER_REGISTER.keys(), key=lambda p: p != dflt)
    opts = {p: make_nice_str(p) for p in keys}
    return opts, next(iter(opts), None)


def _direction_options(provider_name: str) -> tuple[dict[str, str], str | None]:
    provider = PROVIDER_REGISTER.get(provider_name)
    if not provider:
        return {}, None
    opts = {d.value: make_nice_str(d.value) for d in provider.valid_directions}
    return opts, next(iter(opts), None)


def _service_options(provider_name: str, direction: str) -> tuple[dict[str, str], str | None]:
    provider = PROVIDER_REGISTER.get(provider_name)
    if not provider:
        return {}, None
    dflt = provider.default_service
    available = sorted(
        provider.valid_direction_services.get(direction, []),
        key=lambda s: s.value != dflt,
    )
    opts = {s.value: make_nice_str(s.name) for s in available}
    return opts, next(iter(opts), None)


# ── Reusable contact + address panel ─────────────────────────────────────────


class AddressPanel:
    """
    A pair of NiceGUI cards — Contact (left) and Address (right) — with
    an address-check button that confirms whether the entered address exists
    in the Royal Mail database and displays the matched record(s) as text.

    Parameters
    ----------
    initial_contact:    Pre-fill contact fields (optional).
    initial_address:    Pre-fill address fields (optional).
    show_use_own_phone: Add a "Use Own" shortcut button next to phone field.
    bind_switch:        If given, all widgets are bound to this switch's
                        ``value`` so they are disabled when the switch is off.
    """

    def __init__(
        self,
        *,
        initial_contact: Contact | None = None,
        initial_address: Address | None = None,
        show_use_own_phone: bool = False,
        bind_switch: ui.switch | None = None,
    ) -> None:
        self._bind = bind_switch
        self._build(initial_contact, initial_address, show_use_own_phone)

    # ── Binding helper ────────────────────────────────────────────────────────

    def _w(self, widget):
        """Optionally bind widget enabled-state to the panel's switch."""
        if self._bind is not None:
            widget.bind_enabled_from(self._bind, 'value')
        return widget

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self, contact: Contact | None, addr: Address | None, show_use_own_phone: bool) -> None:
        lines = addr.address_lines if addr else []
        rm_available = 'ROYAL_MAIL' in PROVIDER_REGISTER

        with ui.row().classes(theme.ROW):
            # Contact card
            with ui.card().classes('col q-pa-md ship-card'):
                ui.label('Contact').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.contact_in = self._w(
                    ui.input(label='Contact Name', value=contact.contact_name if contact else '')
                    .props(theme.INPUT_PROPS)
                )
                self.business_in = self._w(
                    ui.input(label='Business Name', value=addr.business_name if addr else '')
                    .props(theme.INPUT_PROPS)
                )
                self.email_in = self._w(
                    ui.input(label='Email', value=contact.email_address if contact else '')
                    .props(f'{theme.INPUT_PROPS} type=email')
                )
                with ui.row().classes('items-end w-full no-wrap'):
                    self.phone_in = self._w(
                        ui.input(label='Mobile Phone', value=contact.mobile_phone if contact else '')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                    )
                    if show_use_own_phone:
                        ui.button('Use Own', on_click=self._use_own_phone).props(f'flat dense {theme.BTN_PRIMARY}')

            # Address card
            with ui.card().classes('col q-pa-md ship-card'):
                ui.label('Address').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.addr1_in = self._w(
                    ui.input(label='Address Line 1', value=lines[0] if lines else '').props(theme.INPUT_PROPS)
                )
                self.addr2_in = self._w(
                    ui.input(label='Address Line 2', value=lines[1] if len(lines) > 1 else '').props(theme.INPUT_PROPS)
                )
                self.addr3_in = self._w(
                    ui.input(label='Address Line 3', value=lines[2] if len(lines) > 2 else '').props(theme.INPUT_PROPS)
                )
                self.town_in = self._w(
                    ui.input(label='Town', value=addr.town if addr else '').props(theme.INPUT_PROPS)
                )
                with ui.row().classes('items-end w-full no-wrap q-gutter-xs'):
                    self.postcode_in = self._w(
                        ui.input(label='Postcode', value=addr.postcode if addr else '')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                    )
                    if rm_available:
                        self.check_btn = self._w(
                            ui.button('Check Address', icon='search', on_click=self._do_check)
                            .props(f'{theme.BTN_PRIMARY} dense')
                        )
                    else:
                        self.check_btn = None

                # Read-only result display — only created when RM is available
                if rm_available:
                    self.addr_result = (
                        ui.label('')
                        .classes('w-full text-caption q-mt-xs')
                        .style('white-space: pre-wrap; font-family: monospace;')
                    )
                    self.addr_result.set_visibility(False)
                else:
                    self.addr_result = None

    # ── Address check ─────────────────────────────────────────────────────────

    async def _do_check(self) -> None:
        if self.check_btn is None or self.addr_result is None:
            return  # Royal Mail not available
        from shipaw.utils.funcs import compare_texts

        self.check_btn.props('loading')
        self.addr_result.set_visibility(False)
        try:
            # business_name omitted — causes misses when it doesn't match RM records exactly
            probe = Address(
                business_name='',
                address_lines=[self.addr1_in.value or '.'],
                town=self.town_in.value or '.',
                postcode=self.postcode_in.value or '',
            )
            hits = await address_lookup(probe)
            entered_company = self.business_in.value.strip()

            if not hits:
                self.addr_result.text = '✗  No matching address found — please check postcode and address line'
                colour = '#a00'
            else:
                result_lines = []
                any_company_match = False

                for rec in hits:
                    addr_lbl = (getattr(rec, 'label', None) or '').replace('\n', ', ')
                    rm_company = (getattr(rec, 'company', '') or '').strip()
                    company_match = entered_company and compare_texts(entered_company, rm_company)

                    if company_match:
                        any_company_match = True
                        result_lines.append(f'✓  {addr_lbl}')
                    elif entered_company:
                        rm_note = f'Result="{rm_company or 'None'}"'
                        result_lines.append(f'⚠  {addr_lbl}\n   Company mismatch:  Search="{entered_company}" — {rm_note}')
                    else:
                        result_lines.append(f'✓  {addr_lbl}')

                self.addr_result.text = '\n'.join(result_lines)

                if not entered_company or any_company_match:
                    colour = '#1a7a1a'   # green — full match (or no company to check)
                else:
                    colour = '#b85c00'   # amber — address found but company name differs

            self.addr_result.style(
                f'color: {colour}; white-space: pre-wrap; font-family: monospace;'
            )
            self.addr_result.set_visibility(True)

        except Exception as exc:
            logger.exception(f'Address check error: {exc}')
            ui.notify(str(exc), type='negative')
        finally:
            self.check_btn.props(remove='loading')

    # ── Contact helper ────────────────────────────────────────────────────────

    def _use_own_phone(self) -> None:
        self.phone_in.value = SHIPAW_SETTINGS.mobile_phone
        self.phone_in.update()

    # ── Data extraction ───────────────────────────────────────────────────────

    def to_full_contact(self) -> FullContact:
        """Build a :class:`FullContact` from the current widget values."""
        return FullContact(
            address=Address(
                business_name=self.business_in.value,
                address_lines=[
                    self.addr1_in.value,
                    self.addr2_in.value or '',
                    self.addr3_in.value or '',
                ],
                town=self.town_in.value,
                postcode=self.postcode_in.value,
            ),
            contact=Contact(
                contact_name=self.contact_in.value,
                email_address=self.email_in.value,
                mobile_phone=self.phone_in.value.strip().replace(' ', ''),
            ),
        )


# ── Form page ─────────────────────────────────────────────────────────────────


class FormPage:
    """
    Renders the shipping form and calls *on_submit* with a
    :class:`~shipaw.nicegui_ui.logic.ShipmentRequest` when the user submits.
    """

    def __init__(self, on_submit: Callable[[ShipmentRequest], None]) -> None:
        self._on_submit_cb = on_submit
        initial = sample_shipment()
        self._build(initial)

    def _build(self, initial) -> None:
        prov_opts, default_prov = _provider_options()
        dir_opts, default_dir = _direction_options(default_prov) if default_prov else ({}, None)
        svc_opts, default_svc = _service_options(default_prov, default_dir) if default_dir else ({}, None)

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
                self.ref_in = (
                    ui.input(label='Reference', value=initial.reference)
                    .props(f'{theme.INPUT_PROPS} maxlength=40')
                    .classes('col')
                )
                self.provider_sel = (
                    ui.select(options=prov_opts, label='Provider', value=default_prov)
                    .props(theme.INPUT_PROPS)
                    .classes('col')
                )
                self.dir_sel = (
                    ui.select(options=dir_opts, label='Direction', value=default_dir)
                    .props(theme.INPUT_PROPS)
                    .classes('col')
                )
                self.svc_sel = (
                    ui.select(options=svc_opts, label='Service', value=default_svc)
                    .props(theme.INPUT_PROPS)
                    .classes('col')
                )

        self.provider_sel.on_value_change(self._on_provider_change)
        self.dir_sel.on_value_change(self._on_direction_change)

        # ── Recipient ─────────────────────────────────────────────────────────
        ui.label('Recipient').classes('text-subtitle1 text-weight-bold q-mt-sm q-mb-xs')
        self.recipient = AddressPanel(
            initial_contact=initial.recipient.contact,
            initial_address=initial.recipient.address,
            show_use_own_phone=True,
        )

        # ── Sender override (collapsed by default) ────────────────────────────
        with ui.expansion('Sender override (optional)', icon='person_add').classes('w-full q-mt-sm ship-card'):
            self.sender_switch = ui.switch('Use custom sender', value=False)
            ui.label('Enable to override the default sender from settings.').classes('text-caption text-grey-6 q-mb-xs')
            self.sender = AddressPanel(bind_switch=self.sender_switch)

        # ── Submit ────────────────────────────────────────────────────────────
        with ui.row().classes('w-full justify-center q-mt-lg'):
            self.submit_btn = (
                ui.button('Review Booking →', on_click=self._do_submit, icon='arrow_forward')
                .props(theme.BTN_PRIMARY)
                .classes('text-subtitle1 q-px-xl q-py-sm')
            )

    # ── Dropdown cascade ──────────────────────────────────────────────────────

    async def _on_provider_change(self, e) -> None:
        dir_opts, default_dir = _direction_options(e.value)
        self.dir_sel.options = dir_opts
        self.dir_sel.value = default_dir
        self.dir_sel.update()
        await self._refresh_services(e.value, default_dir)

    async def _on_direction_change(self, e) -> None:
        await self._refresh_services(self.provider_sel.value, e.value)

    async def _refresh_services(self, prov: str, dirn: str | None) -> None:
        if not dirn:
            return
        svc_opts, default_svc = _service_options(prov, dirn)
        self.svc_sel.options = svc_opts
        self.svc_sel.value = default_svc
        self.svc_sel.update()

    # ── Submit ────────────────────────────────────────────────────────────────

    async def _do_submit(self) -> None:
        self.submit_btn.props('loading')
        try:
            raw_date = self.date_in.value
            ship_date = dt.date.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date
            custom_sender_fc = self.sender.to_full_contact() if self.sender_switch.value else None
            shipment = build_shipment(
                remote_fc=self.recipient.to_full_contact(),
                reference=self.ref_in.value,
                boxes=self.boxes_in.value,
                shipping_date=ship_date,
                direction=self.dir_sel.value,
                custom_sender_fc=custom_sender_fc,
            )
            ship_req = ShipmentRequest(
                shipment=shipment,
                provider_name=self.provider_sel.value,
                service_code=self.svc_sel.value,
            )
            alerts = await maybe_alert_apc(ship_req)
            theme.show_alerts(alerts)
            if not alerts.errors:
                self._on_submit_cb(ship_req)
        except Exception as exc:
            logger.exception(f'Submit error: {exc}')
            ui.notify(str(exc), type='negative', timeout=0)
        finally:
            self.submit_btn.props(remove='loading')

