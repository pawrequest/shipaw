# import os
#
# import openapi_client
# from openapi_client.rest import ApiException
# from pprint import pprint
#
# BASE_URL = 'https://api.parcel.royalmail.com/api/v1'
#
# # Defining the host is optional and defaults to /api/v1
# # See configuration.py for a list of all supported configuration parameters.
# configuration = openapi_client.Configuration(host='/api/v1')
#
# # Configure API key authorization: Bearer
# configuration.api_key['Bearer'] = os.environ['ROYAL_MAIL']
# configuration.host = BASE_URL
#
# # Enter a context with an instance of the API client
# with openapi_client.ApiClient(configuration) as rm:
#     a = openapi_client.OrdersApi(rm)
#     b = a.get_orders_async()
#     pprint(b)
#     c = openapi_client.OrdersApi(rm)
#     inst = openapi_client.VersionApi(rm)
#     document_type = 'document_type_example'  # str | Document generation mode. When documentType is set to \"postageLabel\" the additional parameters below must be used. These additional parameters will be ignored when documentType is not set to \"postageLabel\"
#
#     try:
#         # api_response = inst.get_version_async()
#         api_response = inst.get_version_async_with_http_info()
#         pprint(api_response)
#     except ApiException as e:
#         print('ERROR')
import datetime
import os
from pprint import pprint

from royal_mail_click_and_drop import (
    AddressRequest,
    ApiException,
    Configuration,
    ApiClient,
    CreateOrderRequest,
    OrdersApi,
    RecipientDetailsRequest,
    VersionApi,
)

BASE_URL = 'https://api.parcel.royalmail.com/api/v1'

# Defining the host is optional and defaults to /api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = Configuration(host='/api/v1')

# Configure API key authorization: Bearer
configuration.api_key['Bearer'] = os.environ['ROYAL_MAIL']
configuration.host = BASE_URL


def get_order_request():
    return CreateOrderRequest(
        recipient=RecipientDetailsRequest(
            address=AddressRequest(
                full_name='Testy Testson',
                company_name='Comp name',
                address_line1='addr line1',
                address_line2='',
                address_line3='',
                city='city',
                county='county',
                postcode='nw64te',
                country_code='GB',
            ),
            phone_number='07666666666',
            email_address='sdgsdgsgd@sdgikhjbsdgijbsdigj.com',
            address_book_reference='addrBookRef',
        ),
        order_date=datetime.datetime.strptime('2025-06-09 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
        subtotal=0,
        shipping_cost_charged=0,
        total=0,
    )


# Enter a context with an instance of the API client
with ApiClient(configuration) as rm:
    ...
    a = OrdersApi(rm)
    b = a.get_orders_async()
    pprint(b)
    c = OrdersApi(rm)
    inst = VersionApi(rm)
    document_type = 'document_type_example'  # str | Document generation mode. When documentType is set to \"postageLabel\" the additional parameters below must be used. These additional parameters will be ignored when documentType is not set to \"postageLabel\"

    try:
        # api_response = inst.get_version_async()
        api_response = inst.get_version_async_with_http_info()
        pprint(api_response)
    except ApiException as e:
        print('ERROR')
