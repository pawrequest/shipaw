from shipaw.providers.registry import PROVIDER_REGISTER


def test_address_search():
    provider = PROVIDER_REGISTER.get('ROYAL_MAIL')
    res = await provider.address_search(search_text)
    return JSONResponse(res.dict())
