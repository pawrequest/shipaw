from __future__ import annotations

from enum import Enum

import pydantic as _p
from fastui import components as c, forms as fastui_forms

from pawdantic import paw_types
from shipr import models as s_mod, shipr_types
from shipr.models import pf_shared
from shipr.ship_ui import states
from shipr.ship_ui.dynamic import BookingForm, BoxesModelForm, get_addresses, get_dates  # noqa F401
from shipr.shipr_types import VALID_PC


class ContactForm(_p.BaseModel):
    business_name: paw_types.truncated_printable_str_type(40)
    email_address: paw_types.truncated_printable_str_type(50)
    mobile_phone: str
    contact_name: paw_types.optional_truncated_printable_str_type(30)

    @classmethod
    def with_default(cls, contact: s_mod.Contact):
        class _ContactSelect(cls):
            business_name: paw_types.default_gen(
                paw_types.truncated_printable_str_type(40), default=contact.business_name
            )
            email_address: paw_types.default_gen(
                paw_types.truncated_printable_str_type(50), default=contact.email_address
            )
            mobile_phone: paw_types.default_gen(str, default=contact.mobile_phone)
            contact_name: paw_types.default_gen(
                paw_types.optional_truncated_printable_str_type(30), default=contact.contact_name
            )

        return _ContactSelect


class AddressForm(_p.BaseModel):
    address_line1: paw_types.truncated_printable_str_type(40)
    address_line2: paw_types.optional_truncated_printable_str_type(50)
    address_line3: paw_types.optional_truncated_printable_str_type(60)
    town: paw_types.truncated_printable_str_type(30)
    postcode: str
    country: str = 'GB'


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
    ship_date: shipr_types.fixed_date_type(7)
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
        for service in pf_shared.ServiceCode
    ]


async def contact_fields(state):
    return [
        c.FormFieldInput(
            name='business_name',
            title='Business Name',
            initial=state.contact.business_name,
        ),

        c.FormFieldInput(
            name='email',
            title='Delivery Email',
            initial=state.contact.email_address,
        ),

        c.FormFieldInput(
            name='phone',
            title='Delivery Mobile Phone',
            initial=state.contact.mobile_phone,
        )
    ]


async def address_fields(state):
    return [
        c.FormFieldInput(
            name='address_line1',
            title='Address Line 1',
            initial=state.address.address_line1,
        ),

        c.FormFieldInput(
            name='address_line2',
            title='Address Line 2',
            initial=state.address.address_line2,
        ),

        c.FormFieldInput(
            name='address_line3',
            title='Address Line 3',
            initial=state.address.address_line3,
        ),

        c.FormFieldInput(
            name='town',
            title='Town',
            initial=state.address.town,
        ),

        c.FormFieldInput(
            name='postcode',
            title='Postcode',
            initial=state.address.postcode,
        ),

        # c.FormFieldInput(
        #     name='country',
        #     title='Country',
        #     initial=state.address.country,
        # )
    ]


async def big_form_fields(state: states.ShipState):
    return [
        c.FormFieldSelect(
            name='date',
            options=get_dates(),
            initial=str(state.ship_date.isoformat()),
            title='date',
            # class_name='col-3',
            display_mode='inline',
        ),
        c.FormFieldSelect(
            name='boxes',
            options=[
                fastui_forms.SelectOption(value=str(i), label=str(i))
                for i in range(1, 11)
            ],
            initial=str(state.boxes),
            title='boxes',
            # class_name='width-50',
            # display_mode='inline',

        ),
        c.FormFieldSelect(
            name='direction',
            title='direction',
            options=[
                fastui_forms.SelectOption(value='in', label='Inbound'),
                fastui_forms.SelectOption(value='out', label='Outbound'),
            ],
            initial='out',
            # class_name='col-2',
            # display_mode='inline',
        ),
        *await contact_fields(state),
        c.FormFieldSelect(
            name='service',
            options=get_services(),
            title='Service',
            initial=state.service.value,
        ),
        *await address_fields(state),
    ]


async def address_f_postcode_select_field(state):
    return c.FormFieldSelect(
        name='address',
        options=get_addresses(state.candidates),
        title='Address From Postcode',
        initial=state.address.model_dump_json(),
        class_name='row'
    )


class PostcodeSelect(_p.BaseModel):
    fetch_address_from_postcode: VALID_PC
