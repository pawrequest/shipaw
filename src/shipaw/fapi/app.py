import contextlib

from fastapi import FastAPI, responses
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from shipaw.fapi.routes_html import router as html_router
from shipaw.fapi.routes_api import router as json_router
from shipaw.config import shipaw_settings
from shipaw.fapi.alerts import AlertType, Alert, Alerts
from shipaw.models.logging import log_obj


@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        # set_pf_env()
        # pythoncom.CoInitialize()
        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = ELClient()
        #     populate_db_from_cmc(session, pf_shipper)
        yield

    finally:
        # pythoncom.CoUninitialize()

        ...


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(shipaw_settings().static_dir)), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(html_router)
app.ship_live = shipaw_settings().shipper_live
app.alerts = Alerts.empty()


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg2 = ''
    for err in errors:
        if type := err.get('type'):
            msg2 += type + ' '
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
        status_code=422, content={'detail': jsonable_encoder(exc.errors()), 'alerts': alerts.model_dump(mode='json'), 'message': msg2}
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



