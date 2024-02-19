from typing import Literal, Protocol, Union

import zeep
from pydantic import BaseModel, Field, RootModel
from pytest import raises
from typing_extensions import Annotated
from combadge.core.interfaces import SupportsService
from combadge.core.response import ErrorResponse, SuccessfulResponse
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name
from combadge.support.zeep.backends.sync import ZeepBackend


# 1️⃣ Declare the request model:
class NumberToWordsRequest(BaseModel, populate_by_name=True):
    number: Annotated[int, Field(alias="ubiNum")]


# 2️⃣ Declare the response model:
class NumberToWordsResponse(RootModel, SuccessfulResponse):
    root: str


# 3️⃣ Optionally, declare the error response models:
class NumberTooLargeResponse(RootModel, ErrorResponse):
    root: Literal["number too large"]


# 4️⃣ Declare the interface:
class SupportsNumberConversion(SupportsService, Protocol):
    @operation_name("NumberToWords")
    def number_to_words(
            self,
            request: Annotated[NumberToWordsRequest, Payload(by_alias=True)],
    ) -> Union[NumberTooLargeResponse, NumberToWordsResponse]:
        ...


def test_new():
    wsdl_test = r'C:\Users\RYZEN\prdev\workbench\shipr\resources\NumberConversion.wsdl'
    client = zeep.Client(wsdl=wsdl_test)
    service = ZeepBackend(client.service)[SupportsNumberConversion]

    response = service.number_to_words(NumberToWordsRequest(number=42))
    assert response.unwrap().root == "forty two "

    response = service.number_to_words(NumberToWordsRequest(number=-1))
    with raises(NumberTooLargeResponse.Error):
        response.raise_for_result()
    ...
