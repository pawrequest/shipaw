from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from agnostic.address import Address as AddressAgnost, Contact as ContactAgnost, FullContact
from agnostic.meta import ConvertableShipment, ProviderInterface, register_provider
from agnostic.responses import ShipmentBookingResponseAgnost
from agnostic.shipment import Shipment as ShipmentAgnost
#
from parcelforce.client import ParcelforceClient
from parcelforce.combadge import CreateShipmentService
from parcelforce.request_response import ShipmentRequest, ShipmentResponse
from parcelforce.address import AddressBase, AddressRecipient, Contact as ContactPF
from parcelforce.services import ParcelforceServiceDict
from parcelforce.shipment import Shipment as ShipmentPF


def address_from_agnostic[addr_type: AddressRecipient](cls: type[addr_type], full_contact: FullContact) -> addr_type:
    return cls(
        address_line1=full_contact.address.address_lines[0],
        address_line2=full_contact.address.address_lines[1] if len(full_contact.address.address_lines) > 1 else None,
        address_line3=full_contact.address.address_lines[2] if len(full_contact.address.address_lines) > 2 else None,
        town=full_contact.address.town,
        postcode=full_contact.address.postcode,
        country=full_contact.address.country,
    )


def contact_from_agnostic[contact_type: ContactPF](cls: type[contact_type], full_contact: FullContact) -> contact_type:
    return cls(
        business_name=full_contact.address.business_name,
        contact_name=full_contact.contact.contact_name,
        email_address=full_contact.contact.email_address,
        mobile_phone=full_contact.contact.mobile_phone,
    )


def full_contact_from_provider(contact: ContactPF, address: AddressBase) -> FullContact:
    return FullContact(
        address=AddressAgnost(
            business_name=contact.business_name,
            address_lines=[
                line for line in [address.address_line1, address.address_line2, address.address_line3] if line
            ],
            town=address.town,
            postcode=address.postcode,
            country=address.country,
        ),
        contact=ContactAgnost(
            contact_name=contact.contact_name,
            email_address=contact.email_address,
            mobile_phone=contact.mobile_phone,
        ),
    )


def split_string_into_chunks(s, chunk_size):
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def ref_dict_from_str(ref_string: str) -> dict[str, str]:
    refs = split_string_into_chunks(ref_string, 24)
    if len(refs) > 5:
        raise ValueError('Reference too long, maximum 120 characters allowed')
    ref_nums = {f'reference_number{i}': ref for i, ref in enumerate(refs, start=1)}
    return ref_nums


def join_refs(refs: dict[str, str]) -> str:
    refs = [refs.get(f'reference_number{i+1}', '') for i in range(len(refs))]
    return ''.join(refs).strip()


class ParcelforceShipment(ShipmentPF, ConvertableShipment):
    @classmethod
    def from_agnostic(
        cls,
        shipment: ShipmentAgnost | dict,
    ) -> Self | dict:
        shipment = ShipmentAgnost.model_validate(shipment)
        refs = ref_dict_from_str(shipment.reference)
        service_code = ParcelforceServiceDict[shipment.service.upper()]
        ship_pf = cls(
            **refs,
            recipient_contact=contact_from_agnostic(ContactPF, shipment.recipient),
            recipient_address=address_from_agnostic(AddressRecipient, shipment.recipient),
            total_number_of_parcels=shipment.boxes,
            shipping_date=shipment.shipping_date,
            service_code=service_code,
        )

        if shipment.sender:
            ship_pf = cls.to_inbound(ship_pf)

        return ship_pf

    def to_agnostic(self) -> ShipmentAgnost:
        return ShipmentAgnost(
            recipient=full_contact_from_provider(self.recipient_contact, self.recipient_address),
            sender=full_contact_from_provider(self.sender_contact, self.sender_address)
            if self.sender_contact and self.sender_address
            else None,
            boxes=self.total_number_of_parcels,
            shipping_date=self.shipping_date,
            direction=self.direction,
        )


@register_provider
@dataclass
class ParcelforceProvider(ProviderInterface):
    name = 'PARCELFORCE'
    service_dict = ParcelforceServiceDict
    shipment_type = ShipmentPF

    @staticmethod
    def book_shipment(shipment: dict | ShipmentAgnost) -> ShipmentBookingResponseAgnost:
        shipment = ShipmentAgnost.model_validate(shipment)
        shipment_pf = ParcelforceShipment.from_agnostic(shipment)
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

    @staticmethod
    def get_label_content(shipment_num: str) -> bytes:
        el_client = ParcelforceClient()
        return el_client.get_label_content(shipment_num)


#
#     #
#     # @staticmethod
#     # def provider_shipment(
#     #     shipment: ShipmentAgnost | dict,
#     #     mode: ConvertMode = 'python',
#     # ) -> ShipmentPF | dict:
#     #     shipment = ShipmentAgnost.model_validate(shipment)
#     #     refs = ParcelforceProvider.get_refs(shipment)
#     #     ref_nums = {'reference_number' + i: ref for ref, i in enumerate(refs)}
#     #     service_code = ParcelforceProvider.service_dict[shipment.service.upper()]  # type: ignore (literals)
#     #     ship_pf = ShipmentPF(
#     #         **ref_nums,
#     #         recipient_contact=parcelforce_contact(shipment.recipient.contact),
#     #         recipient_address=parcelforce_address(shipment.recipient.address),
#     #         total_number_of_parcels=shipment.boxes,
#     #         shipping_date=shipment.shipping_date,
#     #         service_code=service_code,
#     #     )
#     #
#     #     if shipment.sender:
#     #         contact = ContactPF.from_generic(shipment.sender.contact, business_name=shipment.sender.address.business_name)
#     #         sender_address = AddressRecipient.from_generic(shipment.sender.address)
#     #         if shipment.direction == ShipDirection.INBOUND:
#     #             ship_pf.shipment_type = ShipmentType.COLLECTION
#     #             ship_pf.print_own_label = True
#     #             ship_pf.collection_info = CollectionInfo(
#     #                 collection_contact=ContactCollection(**contact.model_dump(exclude={'notifications'})),
#     #                 collection_address=sender_address,
#     #                 collection_time=DateTimeRange.null_times_from_date(ship_pf.shipping_date),
#     #             )
#     #         elif shipment.direction == ShipDirection.DROPOFF:
#     #             ship_pf.sender_contact = ContactSender(
#     #                 **contact.model_dump(),
#     #             )
#     #             ship_pf.sender_address = sender_address
#     #         else:
#     #             raise ValueError('Sender info can only be provided for INBOUND or DROPOFF shipments')
#     #
#     #     return pydantic_export(ship_pf, mode)
#
#     # @staticmethod
#     # def generic_full_contact(
#     #     contact: ContactPF, address: AddressRecipient, mode: ConvertMode = 'python'
#     # ) -> FullContact | dict:
#     #     return pydantic_export(
#     #         FullContact(
#     #             contact=Contact(
#     #                 contact_name=contact.contact_name,
#     #                 mobile_phone=contact.mobile_phone,
#     #                 email_address=contact.email_address,
#     #                 business_name=contact.business_name,
#     #             ),
#     #             address=Address(
#     #                 postcode=address.postcode,
#     #                 address_lines=[
#     #                     line for line in [address.address_line1, address.address_line2, address.address_line3] if line
#     #                 ],
#     #                 town=address.town,
#     #             ),
#     #         ),
#     #         mode,
#     #     )
#
#     # @staticmethod
#     # def get_refs(shipment):
#     #     refs = split_string_into_chunks(shipment.reference, 24)
#     #     if len(refs) > 5:
#     #         raise ValueError('Reference too long, maximum 120 characters allowed')
#     #     ref_nums = {'reference_number' + i: ref for ref, i in enumerate(refs)}
#     #     return ref_nums
#
#     # @staticmethod
#     # def generic_shipment(shipment: ShipmentPF, mode: ConvertMode = 'python') -> dict | ShipmentAgnost:
#     #     shipment = ShipmentPF.model_validate(shipment)
#     #     refs = [v for k, v in shipment.model_dump().items() if k.startswith('reference_number') and v]
#     #     res = ShipmentAgnost(
#     #         recipient=ParcelforceProvider.generic_full_contact(
#     #             shipment.recipient_contact, shipment.recipient_address, mode='python'
#     #         ),
#     #         boxes=shipment.total_number_of_parcels,
#     #         shipping_date=shipment.shipping_date,
#     #         direction=get_ship_direction(shipment.model_dump()),
#     #         reference=''.join(refs) if refs else '',
#     #         service=ParcelforceProvider.service_dict.reverse_lookup(shipment.service_code),  # type: ignore (literals)
#     #     )
#     #     return pydantic_export(res, mode)
#
#     # @staticmethod
#     # def handle_response(request: ShipmentRequestAgnost, response: ShipmentBookingResponseAgnost):
#     #     log_booked_shipment(request, response)
