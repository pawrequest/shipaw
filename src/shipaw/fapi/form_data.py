from __future__ import annotations

import json
from datetime import date, time

from fastapi import Depends, Form, HTTPException
from loguru import logger

# from pawdantic.paw_types import VALID_POSTCODE
from pydantic import EmailStr

from shipaw.models.address import Address, Contact, FullContact
from shipaw.config import SHIPAW_SETTINGS
from shipaw.fapi.requests import ShipmentRequest
from shipaw.utils.consts_enums import PackageFormat, ShipDirection, VALID_POSTCODE
from shipaw.models.shipment import Shipment
from shipaw.providers.provider_abc import ProviderName, ShippingProvider
from shipaw.providers.registry import PROVIDER_REGISTER


async def full_contact_form(
    address_line1: str = Form(...),
    address_line2: str = Form(''),
    address_line3: str = Form(''),
    town: str = Form(...),
    postcode: VALID_POSTCODE = Form(...),
    contact_name: str = Form(...),
    email_address: EmailStr = Form(...),
    business_name: str = Form(...),
    mobile_phone: str = Form(...),
) -> FullContact:
    return FullContact(
        address=Address(
            address_lines=[address_line1, address_line2, address_line3],
            town=town,
            postcode=postcode,
            business_name=business_name,
        ),
        contact=Contact(
            contact_name=contact_name,
            email_address=email_address,
            mobile_phone=mobile_phone.strip().replace(' ', ''),
        ),
    )


async def shipment_from_form(
    full_contact: FullContact = Depends(full_contact_form),
    shipping_date: date = Form(...),
    boxes: int = Form(...),
    direction: ShipDirection = Form(...),
    reference: str = Form(...),
    context_json: str = Form(...),
    collect_ready: int = Form(9),
    collect_closed: int = Form(17),
    own_label: bool = Form(True),
    package_format: PackageFormat = Form(PackageFormat.PARCEL),
    weight_kg: int = Form(10),
) -> Shipment:
    collect_ready = time(hour=collect_ready)
    collect_closed = time(hour=collect_closed)
    context = json.loads(context_json)
    logger.debug('Creating Shipment Request from form')

    if direction == ShipDirection.OUTBOUND:
        sender = None
        recipient = full_contact
        own_label = None
    elif direction in {ShipDirection.INBOUND, ShipDirection.DROPOFF}:
        sender = full_contact
        recipient = SHIPAW_SETTINGS.full_contact
        own_label = own_label
    else:
        raise ValueError(f'Unknown direction: {direction}')

    shipment = Shipment(
        recipient=recipient,
        sender=sender,
        boxes=boxes,
        shipping_date=shipping_date,
        direction=direction,
        reference=reference,
        context=context,
        collect_ready=collect_ready,
        collect_closed=collect_closed,
        own_label=own_label,
        package_format=package_format,
        weight_kg=weight_kg,
    )
    return shipment


async def provider_from_form(provider_name: str = Form(...)):
    provider = PROVIDER_REGISTER.get(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail='Provider not found')
    return provider


async def shipment_request_form(
    provider: ShippingProvider = Depends(provider_from_form),
    shipment: Shipment = Depends(shipment_from_form),
    provider_name: ProviderName = Form(...),
    service: str = Form(...),
) -> ShipmentRequest:
    serv = provider.service_codes_type(service)
    return ShipmentRequest(shipment=shipment, provider_name=provider_name, service_code=serv)


async def shipment_form_json(shipment_json: str = Form(...)) -> Shipment:
    shipy = Shipment.model_validate_json(shipment_json)
    return shipy


async def shipment_request_form_json(shipment_request_json: str = Form(...)) -> ShipmentRequest:
    shipy = ShipmentRequest.model_validate_json(shipment_request_json)
    return shipy


async def context_form_json(context_json: str = Form(...)) -> dict:
    context = json.loads(context_json)
    return context
