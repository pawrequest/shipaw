# from typing import TYPE_CHECKING
#
# from loguru import logger
#
# from shipaw.pf_config import pf_sett
#
# if TYPE_CHECKING:
#     from shipaw.models.pf_shipment import Shipment
#
#
# def label_file_unused(shipment: Shipment):
#     label_dirr = pf_sett().label_dir / shipment.direction
#
#     def pathy(numbered):
#         return (label_dirr / numbered).with_suffix('.pdf')
#
#
#     increment = 0
#     numbered = f'{shipment.pf_label_filestem}{'_{increment}' if increment else ''}'
#     lpath = pathy(label_dirr, numbered)
#     while lpath.exists():
#         lpath = pathy(label_dirr, numbered)
#         incremented += 1
#         logger.warning(f'Label path {lpath} already exists')
#         lpath = shipment.numbered_label_path(incremented)
#
#
# logger.debug(f'Using label path={lpath}')
# return lpath
#
#
# def pf_label_filestem(shipment: Shipment):
#     ln = (
#         (
#             f'Parcelforce {shipment.shipment_type.title()} Label '
#             f'{f'from {shipment.collection_info.collection_contact.business_name} ' if shipment.collection_info else ''}'
#             f'to {shipment.recipient_contact.business_name}'
#             f' on {shipment.shipping_date}'
#         )
#         .replace(' ', '_')
#         .replace('/', '_')
#         .replace(':', '-')
#         .replace(',', '')
#         .replace('.', '_')
#     )
#     return ln
#
#
# def numbered_label_stem(shipment, number: int = 1):
#     return f'{shipment.pf_label_filestem}_{number}'
