from amherst.models.am_record import AmherstRecord

from_db = {
    'cmc_table_name': 'Customer',
    'name': 'Test',
    'customer': 'Test',
    'send_date': '2024-04-23',
    'delivery_contact': 'Test',
    'delivery_business': 'Test',
    'telephone': '07999 999999',
    'email': 'asdfrs@sasd.com',
    'address_str': '12 sime affdresss',
    'postcode': 'ME8 8SP',
    'send_method': '',
    'invoice': None,
    'missing_kit_str': None,
    'boxes': 1,
}

def test_amherst_record():
    rec = AmherstRecord(**from_db)
    ...
