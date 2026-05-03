from __future__ import annotations

from loguru import logger
from nicegui import ui

from shipaw.config import SHIPAW_SETTINGS
from shipaw.models.address_contact import Contact, Address, FullContact
from shipaw.nicegui_ui import theme
from shipaw.providers.royal_mail.royal_mail_funcs import address_lookup
from shipaw.providers.registry import PROVIDER_REGISTER

AddressCardClasses = 'col q-pa-md ship-card'


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

    def _switched(self, widget):
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
            with ui.card().classes(AddressCardClasses):
                ui.label('Contact').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.contact_in = self._switched(
                    ui.input(label='Contact Name', value=contact.name if contact else '').props(theme.INPUT_PROPS)
                )
                self.business_in = self._switched(
                    ui.input(label='Business Name', value=addr.business_name if addr else '').props(theme.INPUT_PROPS)
                )
                self.email_in = self._switched(
                    ui.input(label='Email', value=contact.email if contact else '').props(
                        f'{theme.INPUT_PROPS} type=email'
                    )
                )
                with ui.row().classes('items-end w-full no-wrap'):
                    self.phone_in = self._switched(
                        ui.input(label='Mobile Phone', value=contact.mobile_phone if contact else '')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                    )
                    if show_use_own_phone:
                        ui.button('Use Own', on_click=self._use_own_phone).props(f'flat dense {theme.BTN_PRIMARY}')

            # Address card
            with ui.card().classes(AddressCardClasses):
                ui.label('Address').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.addr1_in = self._switched(
                    ui.input(label='Address Line 1', value=lines[0] if lines else '').props(theme.INPUT_PROPS)
                )
                self.addr2_in = self._switched(
                    ui.input(label='Address Line 2', value=lines[1] if len(lines) > 1 else '').props(theme.INPUT_PROPS)
                )
                self.addr3_in = self._switched(
                    ui.input(label='Address Line 3', value=lines[2] if len(lines) > 2 else '').props(theme.INPUT_PROPS)
                )
                self.town_in = self._switched(
                    ui.input(label='Town', value=addr.town if addr else '').props(theme.INPUT_PROPS)
                )
                with ui.row().classes('items-end w-full no-wrap q-gutter-xs'):
                    self.postcode_in = self._switched(
                        ui.input(label='Postcode', value=addr.postcode if addr else '')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                    )
                    if rm_available:
                        self.check_btn = self._switched(
                            ui.button('Check Address', icon='search', on_click=self._do_check).props(
                                f'{theme.BTN_PRIMARY} dense'
                            )
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
                # address_lines=[self.addr1_in.value or '.'],
                address_lines=[_.value for _ in (self.addr1_in, self.addr2_in, self.addr3_in) if _.value.strip()]
                or ['.'],
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
                        rm_note = f'Result="{rm_company or "None"}"'
                        result_lines.append(
                            f'⚠  {addr_lbl}\n   Company mismatch:  Search="{entered_company}" — {rm_note}'
                        )
                    else:
                        result_lines.append(f'✓  {addr_lbl}')

                self.addr_result.text = '\n'.join(result_lines)

                if not entered_company or any_company_match:
                    colour = '#1a7a1a'  # green — full match (or no company to check)
                else:
                    colour = '#b85c00'  # amber — address found but company name differs

            self.addr_result.style(f'color: {colour}; white-space: pre-wrap; font-family: monospace;')
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
                name=self.contact_in.value,
                email=self.email_in.value,
                mobile_phone=self.phone_in.value.strip().replace(' ', ''),
            ),
        )
