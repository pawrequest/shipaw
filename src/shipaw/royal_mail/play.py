import os

import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

BASE_URL = 'https://api.parcel.royalmail.com/api/v1'

# Defining the host is optional and defaults to /api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(host='/api/v1')

# Configure API key authorization: Bearer
configuration.api_key['Bearer'] = os.environ['ROYAL_MAIL']
configuration.host = BASE_URL

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:

    inst = openapi_client.VersionApi(api_client)
    document_type = 'document_type_example'  # str | Document generation mode. When documentType is set to \"postageLabel\" the additional parameters below must be used. These additional parameters will be ignored when documentType is not set to \"postageLabel\"

    try:
        # Return a single PDF file with generated label and/or associated document(s)
        # api_response = inst.get_version_async()
        api_response = inst.get_version_async_with_http_info()
        pprint(api_response)
    except ApiException as e:
        print("ERROR")
