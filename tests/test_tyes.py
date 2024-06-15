import pytest

from shipaw.models.pf_msg import Alert, Alerts


@pytest.fixture
def alert():
    alert = Alert(message='sdgfo')
    alert = alert.model_validate(alert)
    assert alert
    return alert


def test_alerts(alert):
    alerts = Alerts(alert=[alert])
    alerts = alerts.model_validate(alerts)
    assert alerts

