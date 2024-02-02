def get_map() -> dict:
    return {

    }


def get_endpoint_str(endpoint: str, sandbox=True) -> str:
    base_url = 'https://apc'
    if sandbox:
        base_url += '-training'
    return f'{base_url}.hypaship.com/api/3.0/{endpoint}.json'


def get_class_endpoint(cls: type, sandbox=True) -> str:
    return get_endpoint_str(cls.__name__, sandbox)