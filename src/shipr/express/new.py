from __future__ import annotations

from abc import ABC
from typing import Protocol, Callable, Awaitable

from shipr.express.shared import BaseRequest, BaseResponse
#
#
# class BaseMessenger(ABC):
#     name: str
#     request_type: type[BaseRequest]
#     response_type: type[BaseResponse]
#
#     def get_service_protocol(self) -> type[Protocol]:
#         # Define the service method signature dynamically
#         method_name = self.name.lower()  # Converting the name to lowercase for the method name
#
#         # Define the service method using Annotated and Callable
#         service_method = Callable[[self.request_type], Awaitable[self.response_type]]
#
#         # Create the new service protocol with the dynamically defined method
#         service_protocol = type(
#             f"{self.name}ServiceProtocol",
#             (Protocol,),
#             {method_name: service_method}
#         )
#
#         return service_protocol
