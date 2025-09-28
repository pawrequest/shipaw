import webbrowser

from shipaw.fapi.responses import ShipawTemplateResponse


def test_app(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_form_route_json(test_client, sample_shipment):
    body = sample_shipment.model_dump(mode='json')
    response = test_client.post('/api/ship_form', json=body)
    cont = response.json()
    respy = ShipawTemplateResponse(**cont)
    assert respy.template_path == 'form_shape.html'
    assert 'shipment' in respy.context
    assert response.status_code == 200


def test_form_route_html(test_client, sample_shipment, tmp_path):
    body = sample_shipment.model_dump(mode='json')
    response = test_client.post('/ship_form', json=body)
    assert response.status_code == 200
    html = response.text
    # Save to file for manual inspection
    test_file = tmp_path / 'test_output.html'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html)

    webbrowser.open(str(test_file.resolve()))
    # Optionally, add assertions for expected content
    assert '<form' in html