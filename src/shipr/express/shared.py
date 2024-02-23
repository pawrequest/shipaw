from __future__ import annotations

from typing import List

from loguru import logger
from pydantic import BaseModel, ConfigDict, AliasGenerator, model_validator, Field
from pydantic.alias_generators import to_pascal


class BasePFType(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        use_enum_values=True,
        populate_by_name=True,
        extra='allow',
    )

    @model_validator(mode='after')
    def has_extra(self, v):
        try:
            if self.model_extra:
                logger.warning(f'Extra fields found in {self.__class__.__name__}: {v}')
        except Exception as e:
            pass
        return self


class Notifications(BasePFType):
    notification_type: List[str] = Field(..., description='')
