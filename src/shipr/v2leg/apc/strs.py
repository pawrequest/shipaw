from dataclasses import dataclass
from enum import StrEnum

ENDPOINTS = {
    'live': {
        'service_availability': 'https://apc.hypaship.com/api/3.0/ServiceAvailability.json',
        'orders': 'https://apc.hypaship.com/api/3.0/Orders.json'
    },
    'training': {
        'service_availability': 'https://apc-training.hypaship.com/api/3.0/ServiceAvailability.json',
        'orders': 'https://apc-training.hypaship.com/api/3.0/Orders.json'
    }
}


def get_endpoint(endpoint: ENDPOINTS, sandbox=True) -> str:
    stringy = 'https://apc'
    if sandbox:
        stringy += '-training'
    stringy += '.hypaship.com/api/3.0/'
    stringy += endpoint
    stringy += '.json'
    return stringy


@dataclass
class SandboxEndPoints:
    SERVICE_AVAILABILITY = get_endpoint(endpoint='ServiceAvailability')
    ORDERS = get_endpoint(endpoint='Orders')


class EndPoints(StrEnum):
    SERVICE_AVAILABILITY = 'ServiceAvailability'
    ORDERS = 'Orders'
