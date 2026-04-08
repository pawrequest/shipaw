from __future__ import annotations

from _collections_abc import Callable
from pathlib import Path

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel, Field
from starlette.datastructures import State
from starlette.requests import Request

from shipaw.config import FapiConfig, ShipawSettings
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.fapi.log_stream import LogStream


def notify_version(state: AppState) -> Alerts:
    alerts = Alerts.empty()
    if state.settings.shipaw.shipper_live:
        live_msg = 'Live Mode - Real Shipments will be booked'
        notification_type = AlertType.WARNING
    else:
        live_msg = 'Test Mode - No Shipments will be booked'
        notification_type = AlertType.NOTIFICATION
    msg = f'Shipaw Version {state.version} is in {live_msg}'
    logger.info(msg)
    alerts += Alert(message=msg, type=notification_type)
    return alerts


def notify_dev() -> Alerts:
    alerts = Alerts.empty()
    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version'
        logger.info(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)
    return alerts


class AppSettings(BaseModel):
    shipaw: ShipawSettings = Field(default_factory=ShipawSettings.from_env)
    log_sink_id: int | None = None


class AppState(State):
    settings: AppSettings
    log_stream: LogStream
    alerts: Alerts
    version: str
    config: FapiConfig
    callback: Callable
    # callback: Callable[[ShipawRequest, ShipmentRequest, ShipmentResponse], Awaitable[None]]

    @classmethod
    def create(cls):
        state = AppState()
        state.log_stream = LogStream(max_history=400, queue_size=200)
        state.settings = AppSettings()
        state.version = get_version()
        state.alerts = get_alerts(state)
        state.config = FapiConfig()

        return state


def get_alerts(state: AppState) -> Alerts:
    alerts = Alerts.empty()
    alerts += notify_dev()
    alerts += notify_version(state=state)
    return alerts


class ShipawApp(FastAPI):
    state: AppState


class ShipawRequest(Request):
    @property
    def app(self) -> ShipawApp:
        return super().app  # type: ignore[return-value]


def get_version():
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version('shipaw')
    except PackageNotFoundError:
        return 'unknown'
