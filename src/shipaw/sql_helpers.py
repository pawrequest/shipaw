from collections.abc import Callable

import sqlalchemy
from pydantic import BaseModel
from sqlmodel import Column, Field

JSONTypes = str | list[str] | dict[str, str] | tuple[str, ...] | None
JSONTypesPydantic = BaseModel | list[BaseModel] | dict[str | int, BaseModel] | tuple[BaseModel, ...] | None


class PydanticJSONColumn(sqlalchemy.TypeDecorator):
    impl = sqlalchemy.JSON

    def __init__(self, model_class: type[BaseModel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class

    def process_bind_param(self, value: JSONTypesPydantic, dialect) -> JSONTypes:
        if value is None:
            return None
        elif isinstance(value, list):
            return [item.model_dump_json(round_trip=True) if isinstance(item, BaseModel) else item for item in value]
        elif isinstance(value, dict):
            return {
                key: item.model_dump_json(round_trip=True) if isinstance(item, BaseModel) else item
                for key, item in value.items()
            }
        elif isinstance(value, tuple):
            return tuple(
                item.model_dump_json(round_trip=True) if isinstance(item, BaseModel) else item for item in value
            )
        elif isinstance(value, BaseModel):
            return value.model_dump_json(round_trip=True)
        return None
        # elif isinstance(value, date):
        #     logger.debug(f'Processing date {value}')
        #     return value.isoformat()

    def process_result_value(self, value: JSONTypes, dialect) -> JSONTypesPydantic:
        if value is None:
            return None
        elif isinstance(value, list):
            return [self.model_class.model_validate_json(item) for item in value]
        elif isinstance(value, dict):
            return {key: self.model_class.model_validate_json(item) for key, item in value.items()}
        elif isinstance(value, tuple):
            return tuple(self.model_class.model_validate_json(item) for item in value)
        return self.model_class.model_validate_json(value)


def pydantic_json_column(model_class: type[BaseModel]):
    return Column(PydanticJSONColumn(model_class))


def required_json_field(model_class: type[BaseModel]):
    return Field(..., sa_column=pydantic_json_column(model_class))


def optional_json_field(model_class: type[BaseModel]):
    return Field(None, sa_column=pydantic_json_column(model_class))


def default_json_field(model_class: type[BaseModel], default_factory: Callable[[], JSONTypesPydantic]):
    return Field(default_factory=default_factory, sa_column=pydantic_json_column(model_class))
