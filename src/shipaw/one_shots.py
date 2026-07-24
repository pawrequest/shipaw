import json

from shipaw.shipaw_logging import log_obj_text


def checklog():
    with open('checklog.ndjson', 'r') as f:
        data = json.load(f)
    log_obj_text(data)
    ...


if __name__ == '__main__':
    checklog()
