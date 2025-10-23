from enum import StrEnum
from typing import cast


def enum_as_tups(enum_type: type[StrEnum]) -> list[tuple[str, str]]:
    return [(_.name, cast(str, _.value)) for _ in enum_type]


def enum_as_dict(enum_type: type[StrEnum]) -> dict[str, str]:
    return {k: v for k, v in enum_as_tups(enum_type)}


def enum_lookup(*, enum_type: type[StrEnum], attr_name: str) -> str:
    res = getattr(enum_type, attr_name, None)
    if not res:
        raise ValueError(f'Invalid service name: {attr_name}')
    return res


def enum_reverse_lookup(*, enum_type: type[StrEnum], attr_value: str) -> str:
    res = next(name for name in enum_type.__dict__.values() if name == attr_value)
    if not res:
        raise ValueError(f'Invalid service code: {attr_value}')
    return res
