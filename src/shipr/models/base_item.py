import abc
import datetime as dt
import typing as _t
from . import pf_ext, pf_shared, pf_top


class BaseItem(pf_shared.BasePFType, abc.ABC):
    cmc_table_name: str |None = None
    record: dict[str, str] | None = None
    boxes: int | None = None
    ship_date: dt.date | None = None
    name: str | None = None
    input_address: pf_ext.AddressRecipient | None = None
    contact: pf_top.Contact | None = None


    # # @pyd.computed_field
    # @property
    # def boxes(self) -> int:
    #     return 1
    #
    # # @pyd.computed_field
    # @property
    # def ship_date(self) -> dt.date:
    #     """uses cmc cannonical format yyyymmdd"""
    #     return dt.date.today()
    #
    # # @pyd.computed_field
    # @property
    # def name(self) -> str:
    #     return 'name'
    #
    # # @pyd.computed_field
    # @property
    # def input_address(self) -> pf_ext.AddressRecipient:
    #     return pf_ext.AddressRecipient(
    #         address_line1='1',
    #         address_line2='2',
    #         town='town',
    #         postcode='postcode',
    #     )
    #
    # # @pyd.computed_field
    # @property
    # def contact(self) -> pf_top.Contact:
    #     return pf_top.Contact(
    #         business_name='business_name',
    #         email_address='email_address',
    #         mobile_phone='mobile_phone',
    #         contact_name='contact_name',
    #     )
