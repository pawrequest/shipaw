import webbrowser

from shipaw.fapi.responses import ShipawTemplateResponse


def test_app(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_form_route_json(test_client, sample_shipment):
    body = sample_shipment.model_dump(mode='json')
    response = test_client.post('/api/shipping_form', json=body)
    assert response.status_code == 200
    resp_json = response.json()
    respy = ShipawTemplateResponse(**resp_json)
    assert respy.template.template_path == 'shipping_form_container.html'
    assert 'shipment' in respy.template.context
    assert not respy.alerts.errors


def test_form_route_html(test_client, sample_shipment, tmp_path):
    body = sample_shipment.model_dump(mode='json')
    response = test_client.post('/shipping_form', json=body)
    assert response.status_code == 200
    html = response.text
    assert '<form' in html