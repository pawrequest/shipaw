from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger

from shipr.models.booking_state import BaseUIState
from shipr.models import el_msg


class BookedState(BaseUIState):
    request: el_msg.CreateShipmentRequest
    response: el_msg.CreateShipmentResponse
    label_path: Optional[Path] = None
    printed: bool = False

    def shipment_num(self):
        try:
            return self.response.completed_shipment_info.completed_shipments.completed_shipment[
                0].shipment_number
        except Exception as e:
            logger.error(f"Error getting shipment number for hire_id {self.hire_id}: {e}")

    def alerts(self):
        return self.state.response.alerts.alert

    def update_query(self) -> dict[str, str]:
        ret = {"update": self.model_dump_json(exclude_none=True)}
        return ret


__all__ = ['BookedState']
