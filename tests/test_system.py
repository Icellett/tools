from django.test import Client, override_settings


def test_health_returns_ok():
    response = Client().get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
    assert response['X-Request-Id']


@override_settings(APP_VERSION='0.1.0-test')
def test_version_reports_configured_version():
    response = Client().get('/version')
    assert response.status_code == 200
    assert response.json()['version'] == '0.1.0-test'


def test_request_id_is_preserved():
    response = Client().get('/health', HTTP_X_REQUEST_ID='test-123')
    assert response['X-Request-Id'] == 'test-123'
