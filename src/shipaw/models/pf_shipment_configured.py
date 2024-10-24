# from __future__ import annotations

from loguru import logger
from pydantic import ValidationError

from shipaw.models import pf_shared
from shipaw.models.pf_models import AddressCollection, AddressSender
from shipaw.models.pf_shipment_blank import Shipment
from shipaw.models.pf_top import CollectionInfo, ContactCollection, ContactSender
from shipaw.pf_config import pf_sett
from shipaw.ship_types import ShipmentType


class ShipmentConfigured(Shipment):
    contract_number: str = pf_sett().pf_contract_num_1
    department_id: int = pf_sett().department_id


class ShipmentAwayCollectionConfigured(ShipmentConfigured):
    shipment_type: ShipmentType = ShipmentType.COLLECTION
    print_own_label: bool = True
    collection_info: CollectionInfo

    @property
    def notifications_str(self) -> str:
        return self.recipient_contact.notifications_str + self.collection_info.collection_contact.notifications_str


class ShipmentAwayDropoffConfigured(ShipmentConfigured):
    sender_contact: ContactSender
    sender_address: AddressSender


def to_collection(shipment: ShipmentConfigured, own_label=True) -> ShipmentAwayCollectionConfigured:
    try:
        return ShipmentAwayCollectionConfigured.model_validate(
            shipment.model_copy(
                update={
                    'shipment_type': ShipmentType.COLLECTION,
                    'print_own_label': own_label,
                    'collection_info': CollectionInfo(
                        collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
                        collection_contact=ContactCollection.model_validate(
                            shipment.recipient_contact.model_dump(exclude={'notifications'})
                        ),
                        collection_time=pf_shared.DateTimeRange.null_times_from_date(shipment.shipping_date),
                    ),
                    'recipient_contact': pf_sett().home_contact,
                    'recipient_address': pf_sett().home_address,
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Collection: {e}')
        raise e


def to_dropoff(shipment: ShipmentConfigured) -> ShipmentAwayDropoffConfigured:
    try:
        return ShipmentAwayDropoffConfigured.model_validate(
            shipment.model_copy(
                update={
                    'recipient_contact': pf_sett().home_contact,
                    'recipient_address': pf_sett().home_address,
                    'sender_contact': ContactSender(**shipment.recipient_contact.model_dump(exclude={'notifications'})),
                    'sender_address': AddressSender(**shipment.recipient_address.model_dump(exclude_none=True)),
                }
            ), from_attributes=True
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Dropoff: {e}')
        raise e
