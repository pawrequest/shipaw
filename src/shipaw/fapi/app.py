import contextlib
import os

from fastapi import FastAPI, Query, responses
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pawlogger import configure_loguru
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from shipaw.fapi.alerts import Alert, AlertType, Alerts
from shipaw.fapi.routes_api import router as json_router
from shipaw.fapi.routes_html import router as html_router
from shipaw.config import SHIPAW_SETTINGS, populate_providers
from shipaw.fapi.log_stream import LogStream

@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        app_.state.log_stream = LogStream(max_history=400, queue_size=200)
        app_.shipaw_settings = SHIPAW_SETTINGS
        log_file = SHIPAW_SETTINGS.log_file
        configure_loguru(logger, log_file=log_file, level=SHIPAW_SETTINGS.log_level)
        logger.add(app_.state.log_stream.sink, level='DEBUG', enqueue=False)
        populate_providers(SHIPAW_SETTINGS)
        yield

    finally:
        # pythoncom.CoUninitialize()

        ...


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(SHIPAW_SETTINGS.static_dir)), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(html_router)
app.ship_live = SHIPAW_SETTINGS.shipper_live
app.alerts = Alerts.empty()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
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
