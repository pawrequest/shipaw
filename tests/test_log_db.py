from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from shipaw.logging_sql import FullContactTable, ShipmentRequestTable


def test_setup(sample_settings, sample_sql_home_contact, sample_full_home_contact, all_sample_shipment_requests):
    engine = create_engine(sample_settings.log_db_path)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # cnt = ContactTable.model_validate(sample_full_home_contact.contact.model_dump(), from_attributes=True)
        # cnt = sample_sql_home_contact
        cnt = FullContactTable(**sample_full_home_contact.model_dump())
        shpreq = ShipmentRequestTable(**all_sample_shipment_requests.model_dump())
        session.add(cnt)
        session.add(shpreq)
        session.commit()

    # with Session(engine) as session:
    #     result = session.exec(select(ContactTable)).first()
    #     assert result is not None
    #     assert result.contact_name == sample_full_home_contact.contact.contact_name
