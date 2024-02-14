from zeep import Client

# Initialize the client with the URL of your WSDL
client = Client(wsdl='http://example.com/service?wsdl')

# Access a specific service operation and call it
response = client.service.YourOperationName(param1='value1', param2='value2')

# Process the response
print(response)
