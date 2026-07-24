import json
import logging
import pprint
import sys
from copy import copy
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from loguru import logger
from pydantic import BaseModel

from shipaw.config import SHIPAW_SETTINGS

LOGGING_EXCLUDES = {'label_data': ..., 'response': {'label_data'}, 'label': ...}
DUMP_EXLUDES = {'label_data', 'label', 'qr_code'}
if TYPE_CHECKING:
    pass


def set_deps_log_level():
    for name in ('flaskwebgui',):
        lg = logging.getLogger(name)
        lg.setLevel(logging.WARNING)
        lg.propagate = False


def ndlog_dict(data: dict, ndjson_file: Path | None = None):
    ndjson_file = ndjson_file or SHIPAW_SETTINGS.ndjson_log_file
    with open(ndjson_file, 'a') as jf:
        print(json.dumps(data, separators=(',', ':')), file=jf)


def log_obj_text(obj: BaseModel | dict, message: str = '', *, level: str = 'DEBUG', logger_=logger):
    message = message or obj.__class__.__name__
    model_data = prep_logable_dict(obj)
    msg = f'{message}:\n{pprint.pformat(model_data, indent=2)}'.replace('{', r'{{').replace('}', r'}}')
    logger_.opt(depth=2).log(
        level,
        msg,
    )


def log_obj_json(obj: BaseModel | dict, message: str = '', *, ndjson_file=None):
    ndjson_file = ndjson_file or SHIPAW_SETTINGS.ndjson_log_file
    timestamp = datetime.now().isoformat(timespec='seconds')
    logdict = {
        'data_type': type(obj).__name__,
        'timestamp': timestamp,
        'message': message,
        'obj_data': prep_logable_dict(obj),
    }
    ndlog_dict(logdict, ndjson_file=ndjson_file)


def prep_logable_dict(obj: BaseModel | dict) -> dict[str, Any] | dict:
    o = obj.model_dump(mode='json', exclude=LOGGING_EXCLUDES) if isinstance(obj, BaseModel) else obj
    o = remove_keys_from_dict(o)
    return o


def log_obj(
    obj: BaseModel | dict,
    message: str = '',
    level: str = 'DEBUG',
    logger_=logger,
    ndjson_file=None,
):
    log_obj_text(obj, message, level=level, logger_=logger_)
    log_obj_json(obj, message, ndjson_file=ndjson_file)


def remove_keys_from_dict(data: Any, keys_to_remove: set[str] | None = None) -> Any:
    """
    Recursively removes specified keys from a nested dictionaries.
    """

    keys_to_remove = keys_to_remove or DUMP_EXLUDES
    data = copy(data)

    if isinstance(data, dict):
        for key in list(data.keys()):
            if key in keys_to_remove:
                logger.warning(f'Removing key: {key}')
                del data[key]
            else:
                data[key] = remove_keys_from_dict(data[key], keys_to_remove)
    elif isinstance(data, list):
        data = [remove_keys_from_dict(item, keys_to_remove) for item in data]
    elif isinstance(data, tuple):
        data = tuple(remove_keys_from_dict(item, keys_to_remove) for item in data)
    elif isinstance(data, set):
        data = {remove_keys_from_dict(item, keys_to_remove) for item in data}

    return data


def configure_logging(ndjson_file):
    logger.remove()

    logger.add(
        sys.stderr,
        level='DEBUG',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}',
    )

    logger.add(
        ndjson_file,
        level='DEBUG',
        serialize=True,
        rotation='10 MB',
        retention=10,
    )


def normalize_log_value(value: Any) -> Any:
    if isinstance(value, BaseModel | dict):
        return prep_logable_dict(value)
    if isinstance(value, (list, tuple, set)):
        return [normalize_log_value(v) for v in value]
    return value


def log_event(message: str, *, level: str = 'INFO', event: str | None = None, **fields: Any):
    fields = {k: normalize_log_value(v) for k, v in fields.items()}
    if event is not None:
        fields['event'] = event
    logger.bind(**fields).log(level.upper(), message)
