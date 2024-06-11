from __future__ import annotations

from datetime import date, timedelta
from enum import Enum

import pydantic as _p
from fastui import components as c, forms as fastui_forms
from pawdantic import paw_strings, paw_types

from shipaw import Shipment
from shipaw.models import pf_models, pf_shared
from shipaw.ship_types import FormKind, VALID_POSTCODE


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


async def contact_form_inputs(shipment: Shipment):
    return [
        c.FormFieldInput(
            name='business_name',
            title='Business Name',
            initial=shipment.contact.business_name,
        ),
        c.FormFieldInput(
            name='contact_name',
            title='Contact Name',
            initial=shipment.contact.contact_name,
        ),
        c.FormFieldInput(
            name='phone',
            title='Delivery Mobile Phone',
            initial=shipment.contact.mobile_phone,
        ),
        c.FormFieldInput(
            name='email',
            title='Delivery Email',
            initial=shipment.contact.email_address,
            html_type='email',
        ),
    ]


async def manual_address_inputs(shipment: Shipment) -> list[c.FormFieldInput]:
    return [
        c.FormFieldInput(
            name='address_line1',
            title='Address Line 1',
            initial=shipment.address.address_line1,
            required=True,
        ),
        c.FormFieldInput(
            name='address_line2',
            title='Address Line 2',
            initial=shipment.address.address_line2,
        ),
        c.FormFieldInput(
            name='address_line3',
            title='Address Line 3',
            initial=shipment.address.address_line3,
        ),
        c.FormFieldInput(
            name='town',
            title='Town',
            initial=shipment.address.town,
        ),
        c.FormFieldInput(
            name='postcode',
            title='Postcode',
            initial=shipment.address.postcode,
        ),
        # c.FormFieldInput(
        #     name='country',
        #     title='Country',
        #     initial=shipment.address.country,
        # )
    ]


async def standard_shipping_inputs(shipment: Shipment):
    return [
        *await contact_form_inputs(shipment),
        c.FormFieldSelect(
            name='date',
            options=date_select_options(),
            initial=str(shipment.ship_date.isoformat()),
            title='date',
        ),
        c.FormFieldSelect(
            name='boxes',
            options=[fastui_forms.SelectOption(value=str(i), label=str(i)) for i in range(1, 11)],
            initial=str(shipment.boxes),
            title='boxes',
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
        ),
        c.FormFieldSelect(
            name='service',
            options=service_select_options(),
            title='Service',
            initial=shipment.service,
        ),
        c.FormFieldInput(
            name='special_instructions',
            title='Big "Special Instructions" middle of label',
            initial=shipment.special_instructions1,
        ),
        c.FormFieldInput(
            name='reference',
            title='Small "Reference" bottom corner of label',
            initial=shipment.reference_number1,
        ),
    ]


async def get_form_fields(kind: FormKind, shipment: Shipment, candidates):
    match kind:
        case 'manual':
            inputs = await manual_address_inputs(shipment)
        case 'select':
            inputs = await select_address_inputs(shipment, candidates)
        case _:
            raise ValueError(f'Invalid kind {kind!r}')
    return inputs + await standard_shipping_inputs(shipment)


async def select_address_inputs(shipment: Shipment, candidates):
    return [
        c.FormFieldSelect(
            name='address',
            options=address_select_options(candidates),
            title=f'Select Address from {shipment.address.postcode}',
            required=True,
            initial=shipment.address.model_dump_json(),
        )
    ]


class PostcodeSelect(_p.BaseModel):
    fetch_address_from_postcode: VALID_POSTCODE


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


def address_select_options(candidates: list[pf_models.AddressRecipient]) -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=cand.model_dump_json(),
            label=cand.lines_str_oneline,
        )
        for cand in candidates
    ]
