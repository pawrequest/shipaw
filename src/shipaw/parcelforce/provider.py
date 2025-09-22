from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from shipaw.agnostic.address import Address, Contact, FullContact
from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.requests import ProviderName
from shipaw.agnostic.responses import ShipmentBookingResponseAgnost
from shipaw.agnostic.services import ServiceDict
from shipaw.agnostic.ship_types import ConvertMode, ShipDirection, ShipmentType, get_ship_direction, pydantic_export
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.parcelforce.client import ParcelforceClient
from shipaw.parcelforce.combadge import CreateShipmentService
from shipaw.parcelforce.request_response import ShipmentRequest, ShipmentResponse
from shipaw.parcelforce.services import ParcelforceServiceDict
from shipaw.parcelforce.shared import DateTimeRange
from shipaw.parcelforce.shipment import (
    Shipment as ShipmentPF,
    parcelforce_address,
    parcelforce_contact,
)
from shipaw.parcelforce.top import CollectionInfo
from shipaw.parcelforce.address import AddressRecipient, Contact as ContactPF, ContactCollection, ContactSender


def split_string_into_chunks(s, chunk_size):
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


@dataclass
class ParcelforceProvider(ShippingProvider):
    name: ClassVar[ProviderName] = 'PARCELFORCE'
    service_dict: ClassVar[ServiceDict] = ParcelforceServiceDict
    shipment_type: ClassVar[type[ShipmentPF]] = ShipmentPF

    @staticmethod
    def provider_contact_only(contact: Contact, mode: ConvertMode = 'python') -> ContactPF | dict:
        obj = ContactPF(
            business_name=contact.business_name,
            mobile_phone=contact.mobile_phone,
            email_address=contact.email_address,
            contact_name=contact.contact_name,
        )
        return pydantic_export(obj, mode)

    @staticmethod
    def provider_contact(
        full_contact: FullContact,
        mode: ConvertMode = 'python',
    ) -> ContactPF | dict:
        return ParcelforceProvider.provider_contact_only(full_contact.contact, mode)

    @staticmethod
    def provider_address_only(address: Address, mode: ConvertMode = 'python') -> AddressRecipient | dict:
        obj = AddressRecipient(
            address_line1=address.address_lines[0],
            address_line2=address.address_lines[1] if len(address.address_lines) > 1 else None,
            address_line3=address.address_lines[2] if len(address.address_lines) > 2 else None,
            town=address.town,
            postcode=address.postcode,
        )
        return pydantic_export(obj, mode)

    @staticmethod
    def generic_address_only(address: AddressRecipient, mode: ConvertMode = 'python') -> Address | dict:
        obj = Address(
            address_lines=[
                line for line in [address.address_line1, address.address_line2, address.address_line3] if line
            ],
            town=address.town,
            postcode=address.postcode,
        )
        return pydantic_export(obj, mode)

    @staticmethod
    def provider_address(
        full_contact: FullContact,
        mode: ConvertMode = 'python',
    ) -> AddressRecipient | dict:
        return ParcelforceProvider.provider_address_only(full_contact.address, mode)

    @staticmethod
    def provider_shipment(
        shipment: ShipmentAgnost | dict,
        mode: ConvertMode = 'python',
    ) -> ShipmentPF | dict:
        shipment = ShipmentAgnost.model_validate(shipment)
        refs = ParcelforceProvider.get_refs(shipment)
        ref_nums = {'reference_number' + i: ref for ref, i in enumerate(refs)}
        service_code = ParcelforceProvider.service_dict[shipment.service.upper()]  # type: ignore (literals)
        ship_pf = ShipmentPF(
            **ref_nums,
            recipient_contact=parcelforce_contact(shipment.recipient.contact),
            recipient_address=parcelforce_address(shipment.recipient.address),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=service_code,
        )

        if shipment.sender:
            contact = ParcelforceProvider.provider_contact_only(shipment.sender.contact, mode='pydantic')
            sender_address = parcelforce_address(shipment.sender.address)
            if shipment.direction == ShipDirection.INBOUND:
                ship_pf.shipment_type = ShipmentType.COLLECTION
                ship_pf.print_own_label = True
                ship_pf.collection_info = CollectionInfo(
                    collection_contact=ContactCollection(**contact.model_dump(exclude={'notifications'})),
                    collection_address=sender_address,
                    collection_time=DateTimeRange.null_times_from_date(ship_pf.shipping_date),
                )
            elif shipment.direction == ShipDirection.DROPOFF:
                ship_pf.sender_contact = ContactSender(
                    **contact.model_dump(),
                )
                ship_pf.sender_address = sender_address
            else:
                raise ValueError('Sender info can only be provided for INBOUND or DROPOFF shipments')

        return pydantic_export(ship_pf, mode)

    @staticmethod
    def generic_full_contact(
        contact: ContactPF, address: AddressRecipient, mode: ConvertMode = 'python'
    ) -> FullContact | dict:
        return pydantic_export(
            FullContact(
                contact=Contact(
                    contact_name=contact.contact_name,
                    mobile_phone=contact.mobile_phone,
                    email_address=contact.email_address,
                    business_name=contact.business_name,
                ),
                address=Address(
                    postcode=address.postcode,
                    address_lines=[
                        line for line in [address.address_line1, address.address_line2, address.address_line3] if line
                    ],
                    town=address.town,
                ),
            ),
            mode,
        )

    @staticmethod
    def get_refs(shipment):
        refs = split_string_into_chunks(shipment.reference, 24)
        if len(refs) > 5:
            raise ValueError('Reference too long, maximum 120 characters allowed')
        ref_nums = {'reference_number' + i: ref for ref, i in enumerate(refs)}
        return ref_nums

    @staticmethod
    def generic_shipment(shipment: ShipmentPF, mode: ConvertMode = 'python') -> dict | ShipmentAgnost:
        shipment = ShipmentPF.model_validate(shipment)
        refs = [v for k, v in shipment.model_dump().items() if k.startswith('reference_number') and v]
        res = ShipmentAgnost(
            recipient=ParcelforceProvider.generic_full_contact(
                shipment.recipient_contact, shipment.recipient_address, mode='python'
            ),
            boxes=shipment.total_number_of_parcels,
            shipping_date=shipment.shipping_date,
            direction=get_ship_direction(shipment.model_dump()),
            reference=''.join(refs) if refs else '',
            service=ParcelforceProvider.service_dict.reverse_lookup(shipment.service_code),  # type: ignore (literals)
        )
        return pydantic_export(res, mode)

    @staticmethod
    def book_shipment(shipment: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        shipment = ShipmentAgnost.model_validate(shipment)
        shipment_pf = ParcelforceProvider.provider_shipment(shipment, mode='python')
        shipment_request_pf = ShipmentRequest(requested_shipment=shipment_pf)
        el_client = ParcelforceClient()
        authorized_shipment = shipment_request_pf.authenticated(el_client.settings.auth())
        back = el_client.backend(CreateShipmentService)
        resp: ShipmentResponse = back.createshipment(request=authorized_shipment.model_dump(by_alias=True))
        resp.handle_errors()
        resp_agnost = ShipmentBookingResponseAgnost(
            shipment=shipment,
            shipment_num=resp.shipment_num,
            tracking_link=resp.tracking_link(),
            data=resp.model_dump(),
            status=resp.status,
            success=resp.success,
            label_data=el_client.get_label_content(resp.shipment_num),
        )

        return resp_agnost

    # @staticmethod
    # def handle_response(request: ShipmentRequestAgnost, response: ShipmentBookingResponseAgnost):
    #     log_booked_shipment(request, response)

    @staticmethod
    def get_label_content(shipment_num: str) -> bytes:
        el_client = ParcelforceClient()
        return el_client.get_label_content(shipment_num)
