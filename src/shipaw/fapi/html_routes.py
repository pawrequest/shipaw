import os
from functools import wraps
from typing import cast

from fastapi import APIRouter, Body, HTTPException
from fastapi.params import Depends, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse

from shipaw.config import shipaw_settings
from shipaw.fapi.responses import ShipawTemplateResponse
from shipaw.fapi.form_data import shipment_request_from_form, shipment_request_from_json
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment, sample_shipment
from shipaw.fapi.json_routes import (
    ship_form as ship_form_json,
    order_summary as order_review_json,
    order_results as order_confirm_json,
)

router = APIRouter()


@router.get('/open-file', response_class=HTMLResponse)
async def open_file(filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content=f'<span>Re</span>')


@router.post('/print-file', response_class=HTMLResponse)
async def print_file(filepath: str = Query(...)):
    os.startfile(filepath, 'print')
    return HTMLResponse(content=f'<span>Re</span>')


def html_from_json(json_endpoint):
    @wraps(json_endpoint)
    async def wrapper(request: Request, *args, **kwargs):
        resp = await json_endpoint(request, *args, **kwargs)
        if not isinstance(resp, ShipawTemplateResponse):
            raise HTTPException(status_code=500, detail='Internal Server Error - Expected ShipawTemplateResponse')

        return shipaw_settings().templates.TemplateResponse(
            request=request, name=resp.template_path, context=resp.context
        )

    return wrapper


@router.post('/shipping_form', response_class=HTMLResponse)
@html_from_json
async def shipping_form(request: Request, shipment: Shipment = Body(...)) -> HTMLResponse:
    res = await ship_form_json(request, shipment)
    return cast(HTMLResponse, res)


@router.post('/order_summary', response_class=HTMLResponse)
@html_from_json
async def order_summary(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_from_form),
) -> HTMLResponse:
    return cast(HTMLResponse, await order_review_json(request, shipment_request))


@router.post('/order_results', response_class=HTMLResponse)
@html_from_json
async def order_results(
    request: Request,
    shipment_request: ShipmentRequest = Depends(shipment_request_from_json),
) -> HTMLResponse:
    res = await order_confirm_json(request, shipment_request)
    return cast(HTMLResponse, res)


@router.get('/test', response_class=HTMLResponse)
@html_from_json
async def ship(request: Request) -> HTMLResponse:
    shipment = sample_shipment()
    res = await ship_form_json(request, shipment)
    return cast(HTMLResponse, res)


#
# @router.get('/ship_form_test', response_class=HTMLResponse)
# async def ship_form_test(request: Request) -> HTMLResponse:
#     shipment = sample_shipment()
#     resp: ShipawTemplateResponse = await ship_form_json(request, shipment)
#     return shipaw_settings().templates.TemplateResponse(request=request, name=resp.template_path, context=resp.context)


#
#
# @router.post('/ship_form', response_class=HTMLResponse)
# @html_from_json
# async def ship_form(request: Request, shipment: Shipment = Body(...)) -> HTMLResponse:
#     resp: ShipawTemplateResponse = await ship_form_json(request, shipment)
#     return shipaw_settings().templates.TemplateResponse(request=request, name=resp.template_path, context=resp.context)
