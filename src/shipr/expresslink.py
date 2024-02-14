from zeep import Client

# Initialize the client with the URL of your WSDL
settings = Settings(strict=False, xml_huge_tree=True)
client = Client(wsdl=r'C:\Users\giles\prdev\am_dev\shipr\resources\ExpressLink Documentation\ShipService_v14.wsdl', settings=settings)

...



response = client.find(

)
# Access a specific service operation and call it
# response = client.service.YourOperationName(param1='value1', param2='value2')

# Process the response
# print(response)
