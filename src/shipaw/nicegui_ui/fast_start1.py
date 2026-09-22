from collections.abc import Callable

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

DEV = False  # True for development with hot reload, False for production with no hot reload


def post_startp():
    pass


def maybe_run(
    dev: bool = False,
    host: str = '127.0.0.1',
    port: int = 9080,
    pre_startup_: Callable | None = None,
    after_startup_: Callable | None = None,
):

    if not dev or __name__ != '__main__':
        # Explanation: 2 reasons for running this code:
        # 1. not in dev mode, so there is no __mp_main__, this is already where NiceGUI will run
        # 2. or, in dev mode, and this is the __mp_main__, so we want to run this code
        if __name__ == '__main__':

            def pre_startup():
                logger.debug('startup')
                from pawlogger.config_loguru2 import configure_loguru

                from shipaw.config import get_shipaw_settings, populate_providers

                configure_loguru(logger, log_file=get_shipaw_settings().log_file, level=get_shipaw_settings().log_level)
                populate_providers(get_shipaw_settings())

            pre_startup()
            from nicegui import app, ui  # the normal import

            def build_shipper(initial: Shipment | None = None, on_booking: ShipmentCallbackFn | None = None) -> None:
                """Called once per browser-tab connection."""
                logger.debug(f'build_shipper called with {initial=}')
                logger.debug(f'{__name__=}')

                from nicegui import ui  # the normal import

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

            app.on_startup(after_startup_) if after_startup_ else None

        ui_run(
            host=host,
            port=port,
            title='Shipaw Shipper',
            # favicon=Path(r'C:\prdev\amdev\shipaw\src\shipaw\nicegui_ui\favicon.ico'),
            reload=dev,
            window_size=(1200, 900),  # implies native
        )


maybe_run(dev=DEV)
# if not DEV or __name__ != '__main__':
#     # Explanation: 2 reasons for running this code:
#     # 1. not in dev mode, so there is no __mp_main__, this is already where NiceGUI will run
#     # 2. or, in dev mode, and this is the __mp_main__, so we want to run this code
#
#     pre_startup()
#
#     from nicegui import app, ui  # the normal import
#
#     register_pages()
#
#
# ui_run(reload=DEV)  # DEV mode will reload the server when the code changes

# This means:
# If it is DEV mode, __main__ simply runs ui_run, which will start the server, spawn __mp_main__ and run the code above to start the server
# If it is not DEV mode, __main__ will run the code above, and then run ui_run, which will start the server directly
