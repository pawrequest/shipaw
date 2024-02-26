from __future__ import annotations

import os
from abc import ABC
from typing import List, Optional

from loguru import logger
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic.alias_generators import to_pascal

from .enums import AlertType


class BasePFType(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
        # extra='allow',
    )

    # @model_validator(mode='after')
    # def has_extra(self, v):
    #     try:
    #         if self.model_extra:
    #             logger.warning(f'Extra fields found in {self.__class__.__name__}: {v}')
    #     except Exception as e:
    #         pass
    #     return self


class Notifications(BasePFType):
    notification_type: List[str] = Field(default_factory=list)
#


class Authentication(BasePFType):
    user_name: str
    password: str

    @classmethod
    def from_env(cls):
        username = os.getenv('PF_EXPR_SAND_USR')
        password = os.getenv('PF_EXPR_SAND_PWD')
        return cls(user_name=username, password=password)


class Alert(BasePFType):
    code: int = Field(...)
    message: str = Field(...)
    type: AlertType = Field(...)


class Alerts(BasePFType):
    alert: List[Alert] = Field(..., description='')


class BaseRequest(BasePFType):
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

    @field_validator('alerts')
    def check_alerts(cls, v):
        if v:
            for alt in v.alert:
                if alt.type == 'WARNING':
                    logger.warning(f'ExpressLink Warning: {alt.message}')
                elif alt.type == 'ERROR':
                    logger.error(f'ExpressLink Error: {alt.message}')
                else:
                    logger.info(f'ExpressLink {alt.type}: {alt.message}')
        return v
