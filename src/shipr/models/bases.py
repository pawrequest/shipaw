from __future__ import annotations

from abc import ABC
from functools import partial
from typing import Optional, Sequence, TYPE_CHECKING

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal, to_snake

if TYPE_CHECKING:
    from shipr.models.remixed import Authentication, Alerts


def obj_dict(objs: BasePFType | Sequence[BasePFType], **kwargs) -> dict:
    if isinstance(objs, BasePFType):
        objs = [objs]
    return {obj.__class__.__name__: obj.model_dump(**kwargs) for obj in objs}


alias_dict = partial(obj_dict, by_alias=True, exclude_none=True)


class BasePFType(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
        extra='allow',
    )


class BaseRequest(BasePFType, ABC):
    authentication: Optional[Authentication] = Field(None)

    def req_dict(self):
        return self.model_dump(by_alias=True, exclude_none=True)

    @property
    def authorised(self):
        return self.authentication is not None

    def authorise(self, auth: Authentication):
        self.authentication = auth

    def auth_request_dict(self) -> dict:
        if not self.authorised:
            raise ValueError('Authentication is required')
        all_obs = [self.authentication, *self.objs]
        return self.alias_dict(all_obs)


class BaseResponse(BasePFType, ABC):
    alerts: Optional[Alerts] = Field(None)
