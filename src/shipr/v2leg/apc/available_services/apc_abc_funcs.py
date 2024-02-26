from __future__ import annotations

from typing import Sequence, TypeVar

from pawsupport.convert import snake_to_pascal

from shipr.apc.available_services.apc_abc_v2 import BaseRequest

T = TypeVar('T', bound=BaseRequest)
TS = TypeVar('TS', bound=Sequence[BaseRequest])


def resolve_seq(req: T | TS) -> dict:
    if not isinstance(req, Sequence):
        req = [req]
    return {
        resolve_anon(item)
        for item in req
    }


def resolve_anon(req) -> tuple[str, dict]:
    if isinstance(req, BaseRequest):
        return get_dict_and_name(req)


def resolve_req(req: T) -> dict:
    return {
        f'{req.__class__.__name__}':
            req.get_dict
    }

def resolve_req_cls(req: BaseRequest | Sequence[BaseRequest]) -> dict:
    if isinstance(req, BaseRequest):
        return req.get_dict

    elif isinstance(req, Sequence):
        return cls.resolve_all(req)

    else:
        raise TypeError(f"Expected BaseRequest or Sequence[BaseRequest], got {type(req)}")

def get_req_dict(item: BaseRequest) -> dict:
    return {
        snake_to_pascal(attr): item.resolve_req(getattr(item, attr))
        for attr in vars(item)
    }


def get_dict_and_name(item: BaseRequest) -> tuple[str, dict]:
    return item.__class__.__name__, get_req_dict(item)

#####

# def resolve_attrs(base_request: T) -> dict:
#     return {
#         f'{T.__name__}':
#             get_dict(base_request)
#     }
