from shipaw.agnostic.services import ServiceDict, Services


ParcelforceServices = Services(
    NEXT_DAY='SND',
    NEXT_DAY_12='S12',
    NEXT_DAY_9='09',
)

ParcelforceServiceDict = {
    'NEXT_DAY': 'SND',
    'NEXT_DAY_12': 'S12',
    'NEXT_DAY_9': '09',
}