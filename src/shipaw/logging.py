import json
import pprint
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from collections.abc import Sequence

from loguru import logger
from pydantic import BaseModel

from shipaw.config import ShipawSettings

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentResponse


def ndlog_dict(data: dict, ndjson_file: Path | None = None):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    with open(ndjson_file, 'a') as jf:
        print(json.dumps(data, separators=(',', ':')), file=jf)


def log_obj_text(obj: BaseModel, message: str = '', *, level: str = 'DEBUG', logger_=logger):
    message = message or obj.__class__.__name__
    model_data = obj.model_dump(mode='json', exclude={'label_data': ..., 'response': {'label_data'}})
    msg = f'{message}:\n{pprint.pformat(model_data, indent=2)}'.replace('{', r'{{').replace('}', r'}}')
    logger_.opt(depth=2).log(
        level,
        msg,
    )


def log_obj_json(obj: BaseModel, message: str = '', *, ndjson_file=None):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    timestamp = datetime.now().isoformat(timespec='seconds')
    logdict = {
        'data_type': type(obj).__name__,
        'timestamp': timestamp,
        'message': message,
        'obj_data': obj.model_dump(mode='json', exclude={'label_data': ..., 'response': {'label_data'}}),
    }
    ndlog_dict(logdict, ndjson_file=ndjson_file)


def log_obj(
    obj: BaseModel,
    message: str = None,
    level: str = 'DEBUG',
    logger_=logger,
    ndjson_file=None,
):
    ndjson_file = ndjson_file or ShipawSettings.from_env().ndjson_log_file
    log_obj_text(obj, message, level=level, logger_=logger_)
    log_obj_json(obj, message, ndjson_file=ndjson_file)


def log_booked_shipment(request: 'ShipmentRequest', response: 'ShipmentResponse'):
    from shipaw.fapi.shipment_booking import ShipmentBooking

    conversation = ShipmentBooking(request=request, response=response)
    ndlog_dict(conversation.model_dump(mode='json', exclude={'response': {'label_data'}}))


def log_objs(objs: Sequence[BaseModel], message: str = None):
    if message:
        logger.debug(message + ':\n')
    for obj in objs:
        log_obj_text(obj)
