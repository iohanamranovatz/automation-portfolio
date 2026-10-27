import pytest
import requests
import responses

from src.api.booking_client import BookingClient

pytestmark = [pytest.mark.network, pytest.mark.api, pytest.mark.regression]

BASE = "http://fake-booker"


@pytest.fixture
def client():
    return BookingClient(base_url=BASE, timeout=2)


@responses.activate
def test_connection_refused(client):
    responses.get(f"{BASE}/ping", body=requests.exceptions.ConnectionError("refused"))
    with pytest.raises(requests.exceptions.ConnectionError):
        client.ping()


@responses.activate
def test_timeout(client):
    responses.get(f"{BASE}/booking/1", body=requests.exceptions.ReadTimeout("timeout"))
    with pytest.raises(requests.exceptions.Timeout):
        client.get_booking(1)


@responses.activate
@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_server_errors_are_surfaced(client, status):
    responses.get(f"{BASE}/booking", status=status)
    assert client.get_booking_ids().status_code == status


@responses.activate
def test_malformed_json(client):
    responses.post(f"{BASE}/auth", body="<html>gateway error</html>", status=200)
    with pytest.raises(requests.exceptions.JSONDecodeError):
        client.authenticate("admin", "password123")
