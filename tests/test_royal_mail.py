import datetime
from pprint import pprint

import pytest

from royal_mail.royal_mail_click_and_drop.api.labels_api import LabelsApi
from royal_mail.royal_mail_click_and_drop.api.manifests_api import ManifestsApi
from royal_mail.royal_mail_click_and_drop.api.orders_api import OrdersApi
from royal_mail.royal_mail_click_and_drop.api.version_api import VersionApi
from royal_mail.royal_mail_click_and_drop.api_client import ApiClient
from royal_mail.royal_mail_click_and_drop.configuration import Configuration
from royal_mail.royal_mail_click_and_drop.exceptions import ApiException
from royal_mail.royal_mail_click_and_drop.models.billing_details_request import BillingDetailsRequest
from royal_mail.royal_mail_click_and_drop.models.create_order_request import CreateOrderRequest
from royal_mail.royal_mail_click_and_drop.models.create_orders_request import CreateOrdersRequest
from royal_mail.royal_mail_click_and_drop.models.create_orders_response import CreateOrdersResponse
from royal_mail.royal_mail_click_and_drop.models.get_orders_response import GetOrdersResponse
from royal_mail.royal_mail_click_and_drop.models.manifest_orders_response import ManifestOrdersResponse
from royal_mail.royal_mail_click_and_drop.models.recipient_details_request import RecipientDetailsRequest
from royal_mail.royal_mail_click_and_drop.models.shipment_package_request import ShipmentPackageRequest
from royal_mail.royal_mail_click_and_drop.v2.address_request import AddressRequest
from shipaw.royal_mail.royal_mail_click_and_drop.v2.config import royal_mail_settings


@pytest.fixture
def config() -> Configuration:
    configuration = Configuration(host=royal_mail_settings().base_url)
    configuration.api_key['Bearer'] = royal_mail_settings().api_key
    return configuration


def test_get_version(config):
    with ApiClient(config) as rm:
        client = VersionApi(rm)
        try:
            # api_response = inst.get_version_async()
            response = client.get_version_async_with_http_info()
            pprint(response.model_dump(), indent=4)
        except ApiException as e:
            print('ERROR')


def test_converters(sample_full_contact):
    rm_address = AddressRequest.from_generic(sample_full_contact.address)


def recip_address():
    return AddressRequest(
        full_name='Testy Testson',
        company_name='Comp name',
        address_line1='addr line1',
        address_line2='',
        address_line3='',
        city='city',
        county='county',
        postcode='nw64te',
        country_code='GB',
    )


def our_address():
    return AddressRequest(
        full_name='Giles Toman',
        company_name='Amherst',
        address_line1='70 Kingsgate road',
        address_line2='',
        address_line3='',
        city='Kilburn',
        county='London',
        postcode='nw64te',
        country_code='GB',
    )


def recipient_():
    return RecipientDetailsRequest(
        address=recip_address(),
        phone_number='07666666666',
        email_address='sdgsdgsgd@sdgikhjbsdgijbsdigj.com',
    )


def billing_():
    return BillingDetailsRequest(
        address=our_address(),
        phone_number='07878867844',
        email_address='admin@amherst.co.uk',
    )


def packages_():
    return [
        ShipmentPackageRequest(
            weight_in_grams=100,
            package_format_identifier='smallParcel',
        )
    ]


def order_():
    return CreateOrderRequest(
        recipient=recipient_(),
        billing=billing_(),
        order_date=datetime.now(),
        subtotal=0,
        shipping_cost_charged=0,
        total=0,
    )


def orders_request():
    return CreateOrdersRequest(
        items=[order_()],
    )


def do_create_order(config):
    req = orders_request()
    with ApiClient(config) as client:
        c = OrdersApi(client)
        try:
            response = c.create_orders_async(create_orders_request=req)
            pprint(response.model_dump(), indent=4, width=120)
            return response

        except ApiException as e:
            print(e)
            raise


def do_cancel_order(o, config):
    with ApiClient(config) as rm:
        client = OrdersApi(rm)
        try:
            response = client.delete_orders_async(order_identifiers=o)
            pprint(response.model_dump(), indent=4, width=120)
        except ApiException as e:
            print(f'Exception when calling OrdersApi->delete_orders_async: {e}\n')
            raise


def do_list_orders(config):
    with ApiClient(config) as rm:
        client = OrdersApi(rm)
        try:
            response = client.get_orders_async()
            pprint(response.model_dump(), indent=4, width=120)
            return response
        except ApiException as e:
            print(f'Exception when calling OrdersApi->delete_orders_async: {e}\n')
            raise


def do_get_label(order_idents: str, outpath, config):
    with ApiClient(config) as rm:
        client = LabelsApi(rm)
        try:
            response: bytearray = client.get_orders_label_async(
                order_identifiers=order_idents,
                document_type='postageLabel',
                include_returns_label=False,
                include_cn=False,
            )
            with open(outpath, 'wb') as f:
                f.write(response)
        except ApiException as e:
            print(f'Exception when calling LabelsApi->get_orders_label_async: {e}\n')
            # raise
        pprint(str(response), indent=4, width=120)


def do_manifest(config):
    with ApiClient(config) as rm:
        client = ManifestsApi(rm)
        resp: ManifestOrdersResponse = client.manifest_eligible_async()
        mainfest_num = resp.manifest_number
        print(f'Manifest Number: {mainfest_num}')
        return mainfest_num


def test_lots(config, tmp_path):
    # ADD AN ORDER TO THE SYSTEM
    order_response: CreateOrdersResponse = do_create_order(config)
    order_identifier = order_response.created_orders[0].order_identifier

    # manifest orders
    res = do_manifest(config)

    # GET LABELS
    save_to = tmp_path / f'RMCAD label_{order_identifier}.pdf'
    do_get_label(str(order_identifier), save_to, config)

    #  TEARDOWN
    res: GetOrdersResponse = do_list_orders(config)
    order_ident_str = ';'.join([str(_.order_identifier) for _ in res.orders])
    do_cancel_order(order_ident_str, config)

