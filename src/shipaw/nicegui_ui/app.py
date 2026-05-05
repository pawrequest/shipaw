"""
NiceGUI standalone frontend for Shipaw.
Completely independent of shipaw.fapi — the fapi module is not required.

Run:
    python -m shipaw.nicegui_ui.app
or via the script entry point:
    shipaw-ng

Stages:
    Stage 1 ✓  Shipping form → order summary → order results
    Stage 2    Live log panel  (ui.log sidebar with loguru sink)
    Stage 3    Email label button (Outlook integration)
    Stage 4    Post-booking callback hook
"""

from __future__ import annotations

from loguru import logger
from nicegui import ui

from shipaw.config import SHIPAW_SETTINGS, populate_providers
from shipaw.models.requests import ShipmentRequest
from shipaw.models.shipment import Shipment
from shipaw.nicegui_ui import theme

# from shipaw.nicegui_ui.logic import ShipmentRequest, notify_dev
from shipaw.nicegui_ui.pages.form import FormPage
from shipaw.nicegui_ui.pages.results import ResultsPage
from shipaw.nicegui_ui.pages.summary import SummaryPage
from shipaw.utils.backend import notify_dev
from shipaw.utils.callbacks import ShipmentCallbackFn


def build_shipper(initial: Shipment | None = None, on_booking: ShipmentCallbackFn | None = None) -> None:
    """Called once per browser-tab connection."""
    theme.apply_page_styles()

    with ui.header(elevated=True).classes('bg-blue-grey-8 text-white row items-center q-py-sm q-px-md'):
        ui.icon('local_shipping').classes('q-mr-sm text-h6')
        ui.label('Shipaw Shipper').classes('text-h6')
        ui.space()
        for a in notify_dev().warnings:
            ui.badge(a.message[:70], color='orange').classes('q-ml-sm text-caption')

    content = ui.column().classes('w-full q-pa-md').style('max-width: 1100px; margin: 0 auto;')

    # ── Step navigation ───────────────────────────────────────────────────────

    def goto_form() -> None:
        content.clear()
        with content:
            FormPage(on_submit=goto_summary, initial_shipment=initial)

    def goto_summary(ship_req: ShipmentRequest) -> None:
        content.clear()
        with content:
            SummaryPage(ship_req, goto_form=goto_form, goto_results=goto_results, on_booking=on_booking)

    def goto_results(ship_req: ShipmentRequest, response) -> None:
        content.clear()
        with content:
            ResultsPage(ship_req, response, goto_form=goto_form)

    goto_form()


@ui.page('/')
def index() -> None:
    build_shipper()


@ui.page('/shipping_form')
def ship_form(shipment: Shipment) -> None:
    build_shipper(initial=shipment)


def main(host: str = '127.0.0.1', port: int = 9080) -> None:
    """Initialise providers and start the NiceGUI server."""
    from pawlogger import configure_loguru

    configure_loguru(logger, log_file=SHIPAW_SETTINGS.log_file, level=SHIPAW_SETTINGS.log_level)
    populate_providers(SHIPAW_SETTINGS)
    ui.run(
        host=host,
        port=port,
        title='Shipaw Shipper',
        favicon='🚢',
        reload=False,
        native=True,
        window_size=(1200, 900),
    )


if __name__ in {'__main__', '__mp_main__'}:
    main()
