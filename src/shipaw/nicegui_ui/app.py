from loguru import logger
from nicegui.ui_run import run as ui_run  # just importing the function to run the server

from shipaw.models.requests import ShipmentRequest
from shipaw.models.shipment import Shipment
from shipaw.nicegui_ui import theme
from shipaw.nicegui_ui.pages.form import FormPage
from shipaw.nicegui_ui.pages.results import ResultsPage
from shipaw.nicegui_ui.pages.summary import SummaryPage
from shipaw.utils.backend import notify_dev
from shipaw.utils.callbacks import ShipmentCallbackFn

INIT = False


def pre_startup():
    logger.debug('startup')
    from pawlogger.config_loguru2 import configure_loguru

    from shipaw.config import get_shipaw_settings, populate_providers

    configure_loguru(logger, log_file=get_shipaw_settings().log_file, level=get_shipaw_settings().log_level)
    populate_providers(get_shipaw_settings())


def setup():
    global INIT
    if INIT:
        return
    pre_startup()
    from nicegui import ui  # only once

    def build_shipper(initial: Shipment | None = None, on_booking: ShipmentCallbackFn | None = None) -> None:
        """Called once per browser-tab connection."""
        logger.debug(f'build_shipper called with {initial=}')
        logger.debug(f'{__name__=}')

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
    def ship_form(shipment: Shipment | None = None) -> None:
        build_shipper(initial=shipment)

    INIT = True
    # app.on_startup(post_startp) if post_startp else None


def run_ui():
    ui_run(
        host='127.0.0.1',
        port=9080,
        title='Shipaw Shipper',
        reload=False,
        window_size=(1200, 900),  # implies native
    )


if __name__ == '__main__':
    setup()

if __name__ in {'__main__', '__mp_main__'}:
    run_ui()
