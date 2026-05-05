from __future__ import annotations

from loguru import logger
from nicegui import ui
from nicegui.observables import ObservableDict

from shipaw.config import SHIPAW_SETTINGS
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.nicegui_ui import theme
from shipaw.providers.royal_mail.royal_mail_funcs import address_lookup
from shipaw.providers.registry import PROVIDER_REGISTER
from shipaw.utils.ui_funcs import address_search_text

AddressCardClasses = 'col q-pa-md ship-card'


class AddressPanel:
    def __init__(
        self,
        *,
        full_contact_obs: ObservableDict,
        show_use_own_phone: bool = False,
    ) -> None:
        self.full_contact = full_contact_obs
        self._build(show_use_own_phone)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self, show_use_own_phone: bool) -> None:
        rm_available = 'ROYAL_MAIL' in PROVIDER_REGISTER

        with ui.row().classes(theme.ROW):
            # Contact card
            with ui.card().classes(AddressCardClasses) as self.card_ctx:
                ui.label('Contact').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.contact_in = (
                    ui.input(label='Contact Name')
                    .props(theme.INPUT_PROPS)
                    .bind_value(self.full_contact, ('contact', 'name'))
                )
                self.business_in = (
                    ui.input(label='Business Name')
                    .props(theme.INPUT_PROPS)
                    .bind_value(self.full_contact, ('address', 'business_name'))
                )
                self.email_in = (
                    ui.input(label='Email')
                    .props(f'{theme.INPUT_PROPS} type=email')
                    .bind_value(self.full_contact, ('contact', 'email'))
                )

                with ui.row().classes('items-end w-full no-wrap'):
                    self.phone_in = (
                        ui.input(label='Mobile Phone')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                        .bind_value(self.full_contact, ('contact', 'mobile_phone'))
                    )
                    if show_use_own_phone:
                        ui.button('Use Own', on_click=self._use_own_phone).props(f'flat dense {theme.BTN_PRIMARY}')

            # Address card
            with ui.card().classes(AddressCardClasses):
                ui.label('Address').classes('text-subtitle2 text-weight-bold q-mb-xs')
                self.addr1_in = (
                    ui.input(label='Address Line 1')
                    .props(theme.INPUT_PROPS)
                    .bind_value(self.full_contact, ('address', 'address_line1'))
                )
                self.addr2_in = (
                    ui.input(label='Address Line 2')
                    .props(theme.INPUT_PROPS)
                    .bind_value(self.full_contact, ('address', 'address_line2'))
                )
                self.addr3_in = (
                    ui.input(label='Address Line 3')
                    .props(theme.INPUT_PROPS)
                    .bind_value(self.full_contact, ('address', 'address_line3'))
                )
                self.town_in = (
                    ui.input(label='Town').props(theme.INPUT_PROPS).bind_value(self.full_contact, ('address', 'town'))
                )

                with ui.row().classes('items-end w-full no-wrap q-gutter-xs'):
                    self.postcode_in = (
                        ui.input(label='Postcode')
                        .props(theme.INPUT_PROPS)
                        .classes('col')
                        .bind_value(self.full_contact, ('address', 'postcode'))
                    )
                    if rm_available:
                        self.check_btn = ui.button('Check Address', icon='search', on_click=self._do_check).props(
                            f'{theme.BTN_PRIMARY} dense'
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
            address = self.full_contact['address']
            hits = await address_lookup(search_string=address_search_text(address), postcode=address.postcode)
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
            address=Address.model_validate(self.full_contact['address']),
            contact=Contact.model_validate(self.full_contact['contact']),
        )
