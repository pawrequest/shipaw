from __future__ import annotations

from sqlalchemy import JSON, TypeDecorator

from shipr.models import extended


class ContactPFJsonType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ""

    def process_result_value(self, value, dialect):
        return extended.Contact.model_validate_json(value) if value else None


class AddressRecipientJsonType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ""

    def process_result_value(self, value, dialect):
        return extended.AddressRecipient.model_validate_json(value) if value else None


#
#
# class ListAddressJsonType(TypeDecorator):
#     impl = JSON
#
#     def process_bind_param(self, value, dialect):
#         return json.dumps([v.model_dump for v in value]) if value is not None else ""
#
#     def process_result_value(self, value, dialect):
#         res = json.loads(value) if value else None
#         return [elt.AddressRecipientPF.model_validate_json(v) for v in res] if res else None


# class BookingStateJson(TypeDecorator):
#     impl = JSON
#
#     def process_bind_param(self, value, dialect):
#         return value.model_dump_json() if value is not None else ""
#
#     def process_result_value(self, value, dialect):
#         return BookingStateIn.model_validate_json(value) if value else None


class AddressChoicePFJsonType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ""

    def process_result_value(self, value, dialect):
        return shipr.models.extended.AddressChoice.model_validate_json(value) if value else None
