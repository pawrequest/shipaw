from __future__ import annotations

from typing import Any, Sequence, TypeVar

from pawsupport.convert import snake_to_pascal
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
TS = TypeVar('TS', bound=Sequence[BaseModel])


class BaseRequest(BaseModel):
    @property
    def get_dict(self) -> dict:
        return {
            snake_to_pascal(attr): self.resolve_req(val)
            for attr, val in vars(self).items()
        }

    @classmethod
    def resolve_all(cls, attr: object | Sequence[object]) -> dict | tuple[dict, ...]:
        if isinstance(attr, Sequence):
            return tuple(cls.resolve_one_anon(item) for item in attr)
        else:
            return cls.resolve_one_anon(attr)

    @classmethod
    def resolve_req(cls, req: BaseRequest | Sequence[BaseRequest]) -> dict:
        if isinstance(req, BaseRequest):
            return req.get_dict

        elif isinstance(req, Sequence):
            return cls.resolve_all(req)

        else:
            raise TypeError(f"Expected BaseRequest or Sequence[BaseRequest], got {type(req)}")

    @classmethod
    def resolve_one_anon(cls, req) -> dict:
        if isinstance(req, BaseRequest):
            return req.get_dict
        else:
            return req

    def resolve_req_attribute(self, value: Any) -> Any:
        if isinstance(value, BaseRequest):
            return value.get_dict[value.__class__.__name__]
        elif isinstance(value, list) and len(value) == 1 and isinstance(value[0], BaseRequest):
            return value[0].get_dict[value[0].__class__.__name__]
        elif isinstance(value, list):
            return [self.resolve_attribute(item) for item in value]
        else:
            return value
