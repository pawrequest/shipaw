from zeep import Client


def test_zeep_client(zeep_client):
    assert isinstance(zeep_client, Client)
    ...
