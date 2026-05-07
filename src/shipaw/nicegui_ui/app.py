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

    with ui.header(elevated=True).classes(theme.HEADER):
        ui.icon('local_shipping').classes('q-mr-sm text-h6')
        ui.label('Shipaw Shipper').classes('text-h6 text-weight-bold')
        ui.space()
        for a in notify_dev().warnings:
            ui.badge(a.message[:70], color='orange').classes('q-ml-sm text-caption')
        theme.theme_switcher()

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
        # favicon=Path(r'C:\prdev\amdev\shipaw\src\shipaw\nicegui_ui\favicon.ico'),
        reload=False,
        window_size=(1200, 900),  # implies native
    )


if __name__ in {'__main__', '__mp_main__'}:
    main()
