from __future__ import annotations

from datetime import date, timedelta
from enum import Enum

import pydantic as _p
from fastui import components as c, forms as fastui_forms
from pawdantic import paw_types, paw_strings

from shipaw import Shipment
from shipaw.models import pf_shared, pf_ext
from shipaw.ship_types import FormKind, VALID_PC


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




def service_select_options():
    return [fastui_forms.SelectOption(value=service.value, label=service.name) for service in pf_shared.ServiceCode2]


# def get_services():
#     return [
#         {'value': service.value, 'label': service.display_label}
#         for service in pf_shared.ServiceCode
#     ]


async def contact_form_inputs(state):
    return [
        c.FormFieldInput(
            name='business_name',
            title='Business Name',
            initial=state.contact.business_name,
        ),
        c.FormFieldInput(
            name='contact_name',
            title='Contact Name',
            initial=state.contact.contact_name,
        ),
        c.FormFieldInput(
            name='email',
            title='Delivery Email',
            initial=state.contact.email_address,
            html_type='email',
        ),
        c.FormFieldInput(
            name='phone',
            title='Delivery Mobile Phone',
            initial=state.contact.mobile_phone,
        ),
    ]


async def address_form_inputs(state):
    return [
        c.FormFieldInput(
            name='address_line1',
            title='Address Line 1',
            initial=state.address.address_line1,
            required=True,
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
        #     initial=shipment.address.country,
        # )
    ]


async def shipping_form_inputs(state: Shipment, manual=False):
    return [
        c.FormFieldSelect(
            name='date',
            options=date_select_options(),
            initial=str(state.ship_date.isoformat()),
            title='date',
            # class_name='col-3',
            # display_mode='inline',
        ),
        c.FormFieldSelect(
            name='boxes',
            options=[fastui_forms.SelectOption(value=str(i), label=str(i)) for i in range(1, 11)],
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
                fastui_forms.SelectOption(value='dropoff', label='Inbound DropOff'),
            ],
            initial='out',
            # class_name='col-2',
            # display_mode='inline',
        ),
        c.FormFieldSelect(
            name='service',
            options=service_select_options(),
            title='Service',
            # initial=shipment.service.value,
            initial=state.service,
        ),
        c.FormFieldInput(
            name='special_instructions',
            title='Big "Special Instructions" middle of label',
            initial=state.special_instructions,
        ),
        c.FormFieldInput(
            name='reference',
            title='Small "Reference" bottom corner of label',
            initial=state.reference,
        ),
        *await contact_form_inputs(state),
    ]


async def ship_inputs_select(state: Shipment):
    return [
        *await shipping_form_inputs(state),
        await address_select(state),
    ]


async def ship_inputs_manual(state: Shipment):
    return [
        *await shipping_form_inputs(state),
        *await address_form_inputs(state),
    ]


async def get_form_fields(kind: FormKind, state):
    if kind == 'manual':
        return await ship_inputs_manual(state)
    if kind == 'select':
        return await ship_inputs_select(state)
    raise ValueError(f'Invalid kind {kind!r}')


async def address_select(state):
    return c.FormFieldSelect(
        name='address',
        options=address_select_options(state.candidates),
        title='Select Address',
        required=True,
        initial=state.address.model_dump_json(),
        # class_name='row'
    )


class PostcodeSelect(_p.BaseModel):
    fetch_address_from_postcode: VALID_PC


ADVANCE_BOOKING_RANGE = 28
DATE_RANGE_LIST = [
    date.today() + timedelta(days=i)
    for i in range(ADVANCE_BOOKING_RANGE)
    if (date.today() + timedelta(days=i)).weekday() < 5
]


def date_select_options() -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=str(d.isoformat()),
            label=paw_strings.date_string(d),
        )
        for d in DATE_RANGE_LIST
    ]


def address_select_options(candidates: list[pf_ext.AddressRecipient]) -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=cand.model_dump_json(),
            label=cand.lines_str_oneline,
        )
        for cand in candidates
    ]
