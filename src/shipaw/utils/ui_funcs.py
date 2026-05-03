from __future__ import annotations

import re
from datetime import date, datetime
from importlib.resources import files
from pathlib import Path
from typing import Sequence

from shipaw.models.address_contact import Address


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


def get_ui() -> Path:
    res = Path(files('shipaw'))
    res = res / 'ui'
    if not res.exists():
        raise FileNotFoundError(f'UI directory {res} does not exist')
    return res


def make_nice_str(s: str) -> str:
    return s.replace('_', ' ').title()


def str_to_nice_str_dict(items: Sequence[str]) -> dict[str, str]:
    return {i: make_nice_str(i) for i in items}


def address_search_text(address: Address) -> str:
    fields = [address.business_name] + address.address_lines + [address.town, address.postcode]
    return ', '.join(f for f in fields if f)
