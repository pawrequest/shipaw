from typing import Optional

import sqlmodel as sqm

from shipr.models import extended


class AddressRecipientDB(extended.AddressRecipient, sqm.SQLModel, table=True):
    id: Optional[int] = sqm.Field(default=None, primary_key=True)
