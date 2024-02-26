from __future__ import annotations

import json
from typing import Any, List, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
TS = TypeVar('TS', bound=Sequence[BaseModel])


def snake_to_pascal(string: str) -> str:
    return ''.join(word.title() for word in string.split('_'))


class BaseRequest(BaseModel):
    @property
    def get_dict(self) -> dict:
        return {
            snake_to_pascal(attr): self.resolve_attribute(getattr(self, attr))
            for attr in vars(self)
        }

    def resolve_attribute(self, value: Any) -> Any:
        if isinstance(value, BaseRequest):
            return value.get_dict[value.__class__.__name__]
        elif isinstance(value, list) and len(value) == 1 and isinstance(value[0], BaseRequest):
            return value[0].get_dict[value[0].__class__.__name__]
        elif isinstance(value, list):
            return [self.resolve_attribute(item) for item in value]
        else:
            return value

    @property
    def get_json(self) -> str:
        return json.dumps(self.get_dict)

    @classmethod
    def get_json_many(cls: type[T], instances: List[T]) -> str:
        return json.dumps(cls.get_dict_many3(instances))

    @classmethod
    def get_dict_many(cls: type[T], instances: List[T]) -> str:
        return json.dumps({
            f'{cls.__name__}s': {
                cls.__name__:
                    instance.get_dict2
                for instance in instances
            }
        }
        )
