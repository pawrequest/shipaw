import sqlalchemy
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.models.shipment import Shipment
from shipaw.sql_helpers import optional_json_field, required_json_field


class TableModel(SQLModel):
    """Base class for SQLModel tables."""

    id: int | None = Field(default=None, primary_key=True)


class AddressTable(Address, TableModel, table=True):
    __tablename__ = 'address'
    # address_lines: list[str] = required_json_field()
    address_lines: list[str] = Field(..., sa_column=Column(sqlalchemy.JSON))


class ContactTable(Contact, TableModel, table=True):
    __tablename__ = 'contact'


class FullContactTable(FullContact, TableModel, table=True):
    __tablename__ = 'full_contact'
    contact: Contact = required_json_field(Contact)
    address: Address = required_json_field(Address)


class ShipmentTable(Shipment, TableModel, table=True):
    __tablename__ = 'shipment'
    recipient: FullContact = required_json_field(FullContact)
    sender: FullContact | None = optional_json_field(FullContact)
    context: dict = Field(default_factory=dict, sa_column=Column(sqlalchemy.JSON))


class ShipmentRequestTable(ShipmentRequest, TableModel, table=True):
    """SQLModel table for ShipmentRequest"""

    __tablename__ = 'shipment_request'
    shipment: Shipment = required_json_field(Shipment)
