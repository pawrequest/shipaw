from __future__ import annotations

from enum import Enum

import pydantic as _p
from fastui import components as c, forms as fastui_forms
from pawdantic import paw_types

from shipaw import ship_types
from shipaw.models import pf_shared
from shipaw.ship_ui import states
# from shipaw.ship_ui.dynamic import BookingForm, BoxesModelForm, get_addresses, get_dates  # F401
# todo check the noqa unused imports were not needed?
from shipaw.ship_ui.dynamic import get_dates
from shipaw.ship_types import VALID_PC


class ContactForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: paw_types.truncated_printable_str_type(50)
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)


class AddressForm(_p.BaseModel):
    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'


#

class ContactAndAddressForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: str
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'


class DirectionEnum(str, Enum):
    INBOUND = 'INBOUND'
    out = 'out'


class FullForm(_p.BaseModel):
    ship_date: ship_types.fixed_date_type(7)
    # ship_date: adate
    boxes: int
    direction: DirectionEnum = DirectionEnum.out

    business_name: paw_types.truncated_printable_str_type(40)
    email_address: str
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'


def get_services():
    return [
        fastui_forms.SelectOption(value=service.value, label=service.name)
        for service in pf_shared.ServiceCode2
    ]


# def get_services():
#     return [
#         {'value': service.value, 'label': service.display_label}
#         for service in pf_shared.ServiceCode
#     ]


async def contact_fields():
    return [
        c.FormFieldInput(
            name='business_name',
            title='Business Name',
        ),

        c.FormFieldInput(
            name='contact_name',
            title='Contact Name',
        ),

        c.FormFieldInput(
            name='email',
            title='Delivery Email',
            html_type='email',
        ),

        c.FormFieldInput(
            name='phone',
            title='Delivery Mobile Phone',
        )
    ]


async def address_fields():
    return [
        c.FormFieldInput(
            name='address_line1',
            title='Address Line 1',
            required=True,
        ),

        c.FormFieldInput(
            name='address_line2',
            title='Address Line 2',
        ),

        c.FormFieldInput(
            name='address_line3',
            title='Address Line 3',
        ),

        c.FormFieldInput(
            name='town',
            title='Town',
        ),

        c.FormFieldInput(
            name='postcode',
            title='Postcode',
        ),

        # c.FormFieldInput(
        #     name='country',
        #     title='Country',
        #     initial=state.address.country,
        # )
    ]


async def ship_fields():
    return [
        c.FormFieldSelect(
            name='date',
            options=get_dates(),
            title='date',
        ),
        c.FormFieldSelect(
            name='boxes',
            options=[
                fastui_forms.SelectOption(value=str(i), label=str(i))
                for i in range(1, 11)
            ],
            title='boxes',
        ),
        c.FormFieldSelect(
            name='direction',
            title='direction',
            options=[
                fastui_forms.SelectOption(value='in', label='Inbound'),
                fastui_forms.SelectOption(value='out', label='Outbound'),
            ],
            initial='out',
        ),
        c.FormFieldSelect(
            name='service',
            options=get_services(),
            title='Service',
            initial=pf_shared.ServiceCode2.EXPRESS24,
        ),
        c.FormFieldInput(
            name='special_instructions',
            title='Big "Special Instructions" middle of label',
        ),
        c.FormFieldInput(
            name='reference',
            title='Small "Reference" bottom corner of label',
        ),
    ]


async def ship_fields_partial(state: states.ShipStatePartial = None):
    if state:
        initial = state.model_dump()
    return [
        *await ship_fields(),
        *await contact_fields(),
        *await address_fields(),
    ]
