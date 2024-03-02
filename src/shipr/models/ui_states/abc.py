import base64
import json
import typing as _ty

import sqlmodel as sqm

class BaseUIState(sqm.SQLModel):
    def update(self, **kwargs) -> _ty.Self:
        """return a new BookingStateUpdate with the values of other merged into self."""
        updated = self.model_copy(update=kwargs)
        return updated

    def update_get_query64(self, **kwargs) -> dict[str, str]:
        """returns {'update': updated json}"""
        updated = self.model_validate(self.model_copy(update=kwargs))
        for f in updated.model_fields_set:
            setattr(self, f, getattr(updated, f))
        return updated.base64_query('update')
        # return {"update": updated.model_dump_json()}

    def base64_query(self, query_key="state") -> dict[str, str]:
        return {f'{query_key}_64': self.state_64()}

    def updated_64(self, **kwargs) -> str:
        updated = self.model_copy(update=kwargs)
        return updated.state_64()

    def state_64(self):
        state_ = self.model_dump_json()
        return base64.urlsafe_b64encode(state_.encode()).decode()

    def update_from_64(self, state_64: str) -> _ty.Self:
        state_ = base64.urlsafe_b64decode(state_64).decode()
        state = json.loads(state_)
        for k, v in state.items():
            setattr(self, k, v)
        return self

    @classmethod
    def from_64(cls, state_64: str) -> _ty.Self:
        state_ = base64.urlsafe_b64decode(state_64).decode()
        return cls.model_validate_json(state_)

