from __future__ import annotations

from pydantic import BaseModel, ConfigDict, AliasGenerator
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
