from __future__ import annotations

from abc import ABC, abstractmethod

from fastui import AnyComponent
from fastui import components as c

from pawdantic.pawui.states import BaseUIState


class ManagerPage(c.Page, ABC):
    manager: BaseUIState

    @classmethod
    async def from_booking(cls, booking) -> list[AnyComponent]:
        page = cls(booking=booking)
        return await page.get_page()

    @abstractmethod
    async def get_page(self) -> list[c.AnyComponent]:
        raise NotImplementedError