import os

from fastapi import Query, responses
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pawlogger import configure_loguru
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from shipaw.config import SHIPAW_SETTINGS, ShipawSettings, populate_providers
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.fapi.app_custom import AppState, ShipawApp, ShipawRequest
from shipaw.fapi.routes_api import router as json_router
from shipaw.fapi.routes_html import router as html_router


def create_and_configure_app(settings: ShipawSettings) -> ShipawApp:
    app_ = ShipawApp()
    app_.state = AppState.create()

    # routing
    app_.mount('/static', StaticFiles(directory=str(settings.static_dir)), name='static')
    app_.include_router(json_router, prefix='/api')
    app_.include_router(html_router)

    # logging
    configure_loguru(logger, log_file=settings.log_file, level=settings.log_level)
    logger.add(app_.state.log_stream.sink, level='DEBUG', enqueue=False)

    # init
    populate_providers(settings)
    return app_


app = create_and_configure_app(SHIPAW_SETTINGS)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: ShipawRequest, exc: RequestValidationError):
    errors = exc.errors()
    msg2 = ''
    for err in errors:
        if err_type := err.get('type'):
            msg2 += err_type + ' '
        if loc := err.get('loc'):
            msg2 += f'in {loc} '
        if ctx := err.get('ctx'):
            if reason := ctx.get('reason'):
                msg2 += f': {reason} '
        if input_ := err.get('input'):
            msg2 += f'. Input = {input_} '

    logger.error(msg2)
    alerts = Alerts(alert=[Alert(code=1, message=msg2, type=AlertType.ERROR)])
    return JSONResponse(
        status_code=422,
        content={'detail': jsonable_encoder(exc.errors()), 'alerts': alerts.model_dump(mode='json'), 'message': msg2},
    )


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/', response_class=JSONResponse)
async def base():
    return JSONResponse(content={'status': 'ok'})


@app.get('/open-file', response_class=HTMLResponse)
async def open_file(filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content='<span>Re</span>')
