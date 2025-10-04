# import datetime
# from pprint import pprint
#
# import pytest
#
# from royal_mail_click_and_drop import LabelGenerationRequest
# from royal_mail_click_and_drop.api.labels_api import LabelsApi
# from royal_mail_click_and_drop.api.manifests_api import ManifestsApi
# from royal_mail_click_and_drop.api.orders_api import OrdersApi
# from royal_mail_click_and_drop.api.version_api import VersionApi
# from royal_mail_click_and_drop.api_client import ApiClient
# from royal_mail_click_and_drop.config import royal_mail_settings
# from royal_mail_click_and_drop.configuration import Configuration
# from royal_mail_click_and_drop.exceptions import ApiException
# from royal_mail_click_and_drop.models.create_orders_request import CreateOrderRequest, CreateOrdersRequest
# from royal_mail_click_and_drop.models.create_orders_response import CreateOrdersResponse
# from royal_mail_click_and_drop.models.get_orders_response import GetOrdersResponse
# from royal_mail_click_and_drop.models.manifest_orders_response import ManifestOrdersResponse
# from royal_mail_click_and_drop.models.shipment_package_request import ShipmentPackageRequest
# from shipaw.config import shipaw_settings
# from shipaw.providers_wip.royal_mail_provider import (
#     full_contact_from_rm,
#     rm_address_from_agnostic_fc,
#     rm_contact_from_agnostic_fc,
# )
#
#
# @pytest.fixture
# def config() -> Configuration:
#     return royal_mail_settings().configuration()
#
#
# def test_get_version(config):
#     with ApiClient(config) as rm:
#         client = VersionApi(rm)
#         try:
#             # api_response = inst.get_version_async()
#             response = client.get_version_async_with_http_info()
#             pprint(response.model_dump(), indent=4)
#         except ApiException as e:
#             print('ERROR')
#
#
# @pytest.fixture
# def rm_address(sample_full_contact):
#     return rm_address_from_agnostic_fc(sample_full_contact)
#
#
# @pytest.fixture
# def rm_contact(sample_full_contact):
#     return rm_contact_from_agnostic_fc(sample_full_contact)
#
#
# def test_converters(sample_full_contact, rm_contact):
#     gener = full_contact_from_rm(rm_contact)
#     assert gener == sample_full_contact
#
#
# @pytest.fixture
# def our_address():
#     return rm_address_from_agnostic_fc(shipaw_settings().full_contact)
#
#
# def packages_():
#     return [
#         ShipmentPackageRequest(
#             weight_in_grams=100,
#             package_format_identifier='smallParcel',
#         )
#     ]
#
#
# def order_(recipient):
#     return CreateOrderRequest(
#         recipient=recipient,
#         # billing=billing_(),
#         order_date=datetime.datetime.now(),
#         subtotal=0,
#         shipping_cost_charged=0,
#         total=0,
#     )
#
#
# @pytest.fixture()
# def rm_shipmemt(sample_shipment, rm_contact):
#     return CreateOrdersRequest(
#         items=[
#             CreateOrderRequest(
#                 order_reference=sample_shipment.reference,
#                 recipient=rm_contact,
#                 order_date=datetime.datetime.now(),
#                 packages=packages_(),
#                 label=LabelGenerationRequest(include_label_in_response=True),
#             )
#         ],
#     )
#
#
# def book_shipment(config, rm_contact, rm_shipmemt):
#     with ApiClient(config) as client:
#         c = OrdersApi(client)
#         response = c.create_orders_async(create_orders_request=rm_shipmemt)
#         return response
#
#
# def cancel_shipment(order_ident: str, config):
#     with ApiClient(config) as rm:
#         client = OrdersApi(rm)
#         try:
#             response = client.delete_orders_async(order_identifiers=order_ident)
#             pprint(response.model_dump(), indent=4, width=120)
#         except ApiException as e:
#             print(f'Exception when calling OrdersApi->delete_orders_async: {e}\n')
#             raise
#
#
# def fetch_orders(config):
#     with ApiClient(config) as rm:
#         client = OrdersApi(rm)
#         try:
#             response: GetOrdersResponse = client.get_orders_async()
#             pprint(response.model_dump(), indent=4, width=120)
#             return response
#         except ApiException as e:
#             print(f'Exception when calling OrdersApi->delete_orders_async: {e}\n')
#             raise
#
#
# def do_get_label(order_idents: str, outpath, config):
#     with ApiClient(config) as rm:
#         client = LabelsApi(rm)
#         try:
#             response: bytearray = client.get_orders_label_async(
#                 order_identifiers=order_idents,
#                 document_type='postageLabel',
#                 include_returns_label=False,
#                 include_cn=False,
#             )
#             with open(outpath, 'wb') as f:
#                 f.write(response)
#         except ApiException as e:
#             print(f'Exception when calling LabelsApi->get_orders_label_async: {e}\n')
#             # raise
#         pprint(str(response), indent=4, width=120)
#
#
# def do_manifest(config):
#     with ApiClient(config) as rm:
#         client = ManifestsApi(rm)
#         resp: ManifestOrdersResponse = client.manifest_eligible_async()
#         mainfest_num = resp.manifest_number
#         print(f'Manifest Number: {mainfest_num}')
#         return mainfest_num
#
#
# def test_lots(config, tmp_path, rm_contact, rm_shipmemt):
#     # ADD A REAL ORDER TO THE REAL SYSTEM!!!
#     # order_response: CreateOrdersResponse = book_shipment(config, rm_contact, rm_shipmemt.model_dump(by_alias=True, mode='json'))
#     # order_identifier = order_response.created_orders[0].order_identifier
#
#     # manifest orders
#     res = do_manifest(config)
#
#     # GET LABELS
#     # save_to = tmp_path / f'RMCAD label_{order_identifier}.pdf'
#     # do_get_label(str(order_identifier), save_to, config)
#
#     #  TEARDOWN
#     res: GetOrdersResponse = fetch_orders(config)
#     cancel_shipment(res.order_ident_string, config)
#
