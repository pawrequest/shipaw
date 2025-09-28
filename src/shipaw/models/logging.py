import json
import pprint
from typing import TYPE_CHECKING, Sequence

from loguru import logger
from pydantic import BaseModel

from shipaw.config import shipaw_settings

if TYPE_CHECKING:
    from shipaw.fapi.requests import ShipmentRequest
    from shipaw.fapi.responses import ShipmentBookingResponse


def log_shipment_json(data: dict, ndjson_file=shipaw_settings().ndjson_log_file):
    with open(ndjson_file, 'a') as jf:
        print(json.dumps(data, separators=(',', ':')), file=jf)


def log_obj(obj: BaseModel, message: str = None):
    message = message or obj.__class__.__name__
    logger.debug(message + ':\n' + pprint.pformat(obj.model_dump(mode='json', exclude={'label_data'}), indent=2))


def log_booked_shipment(request: 'ShipmentRequest', response: 'ShipmentBookingResponse'):
    from shipaw.models.conversation import ShipmentConversation

    conversation = ShipmentConversation(request=request, response=response)
    log_obj(conversation)
    log_shipment_json(conversation.model_dump(mode='json', exclude={'response': {'label_data'}}))


def log_objs(objs: Sequence[BaseModel], message: str = None):
    if message:
        logger.debug(message + ':\n')
    for obj in objs:
        log_obj(obj)
