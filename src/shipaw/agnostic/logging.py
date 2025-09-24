import json

from loguru import logger

from amherst.config import amherst_settings


def log_shipment_json(data: dict, ndjson_file=amherst_settings().ndjson_file):
    with open(ndjson_file, 'a') as jf:
        print(json.dumps(data, separators=(',', ':')), file=jf)


def log_booked_shipment(request, response):
    from shipaw.agnostic.conversation import ShipmentConversation

    conversation = ShipmentConversation(request=request, response=response)
    if hasattr(response, 'shipment_num') and response.shipment_num:
        logger.info(
            f'BOOKED {request.shipment.direction.title()} shipment# {response.shipment_num} for {','.join(request.shipment.remote_full_contact.address.address_lines)}'
        )
    else:
        logger.warning('Something Wrong with booking, no shipment number returned?')
    log_shipment_json(conversation.model_dump(mode='json', exclude={'response': {'label_data'}}))


