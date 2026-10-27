from datetime import date

import pytest

from src.builder.booking_builder import BookingBuilder
from src.reporting.bug_report import check

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_health_check(api):
    assert api.ping().status_code == 201


@pytest.mark.smoke
def test_create_booking_returns_same_data(auth_api, step):
    payload = BookingBuilder().with_name("Ana", "Pop").with_price(300).build()
    with step(f"POST /booking cu {payload}"):
        resp = auth_api.create_booking(payload)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["bookingid"], int)
    assert body["booking"] == payload
    auth_api.delete_booking(body["bookingid"])


@pytest.mark.regression
def test_get_booking_by_id(api, booking):
    booking_id, payload = booking
    resp = api.get_booking(booking_id)
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.regression
def test_filter_bookings_by_name(api, booking):
    booking_id, payload = booking
    resp = api.get_booking_ids(firstname=payload["firstname"], lastname=payload["lastname"])
    assert resp.status_code == 200
    assert {"bookingid": booking_id} in resp.json()


@pytest.mark.regression
def test_full_update_booking(auth_api, booking):
    booking_id, _ = booking
    new_payload = BookingBuilder().with_price(999).with_deposit(False).build()
    resp = auth_api.update_booking(booking_id, new_payload)
    assert resp.status_code == 200
    assert resp.json() == new_payload


@pytest.mark.regression
def test_partial_update_booking(auth_api, booking):
    booking_id, payload = booking
    resp = auth_api.partial_update_booking(booking_id, {"firstname": "Maria"})
    assert resp.status_code == 200
    assert resp.json()["firstname"] == "Maria"
    assert resp.json()["lastname"] == payload["lastname"]


@pytest.mark.regression
def test_delete_booking(auth_api):
    booking_id = auth_api.create_booking(BookingBuilder().build()).json()["bookingid"]
    assert auth_api.delete_booking(booking_id).status_code == 201
    assert auth_api.get_booking(booking_id).status_code == 404


# ---------- negative ----------
@pytest.mark.regression
def test_update_without_token_is_forbidden(api, booking):
    booking_id, _ = booking
    resp = api.update_booking(booking_id, BookingBuilder().build())
    assert resp.status_code == 403


@pytest.mark.regression
def test_get_nonexistent_booking(api):
    assert api.get_booking(999_999_999).status_code == 404


# ---------- bug hunting: pică pe bug-urile lăsate intenționat în Restful Booker ----------
@pytest.mark.regression
@pytest.mark.defect(title="POST /auth cu parolă greșită întoarce 200 în loc de 401", severity="minor")
def test_auth_with_bad_credentials_returns_401(api, step):
    with step("POST /auth cu username='admin', password='wrong'"):
        resp = api.create_token("admin", "wrong")
    check(resp.status_code == 401, expected="Status 401 Unauthorized",
          actual=f"Status {resp.status_code}, body: {resp.text}")


@pytest.mark.regression
@pytest.mark.parametrize("field", ["firstname", "lastname", "totalprice", "bookingdates"])
@pytest.mark.defect(title="POST /booking fără câmpul '{field}' nu întoarce 400", severity="major")
def test_create_booking_missing_field_returns_400(auth_api, step, field):
    payload = BookingBuilder().without_field(field).build()
    with step(f"POST /booking fără câmpul obligatoriu '{field}': {payload}"):
        resp = auth_api.create_booking(payload)
    check(resp.status_code == 400, expected="Status 400 Bad Request cu mesaj de validare",
          actual=f"Status {resp.status_code}, body: {resp.text[:300]}")


@pytest.mark.regression
@pytest.mark.defect(title="POST /booking acceptă checkout înainte de checkin", severity="major")
def test_create_booking_rejects_checkout_before_checkin(auth_api, step):
    payload = BookingBuilder().with_dates(date(2030, 5, 10), date(2030, 5, 1)).build()
    with step("POST /booking cu checkin=2030-05-10 și checkout=2030-05-01"):
        resp = auth_api.create_booking(payload)
    if resp.status_code == 200:
        auth_api.delete_booking(resp.json()["bookingid"])
    check(resp.status_code == 400, expected="Status 400: checkout nu poate fi înainte de checkin",
          actual=f"Status {resp.status_code}, booking creat: {resp.text[:300]}")


@pytest.mark.regression
@pytest.mark.defect(title="POST /booking acceptă preț negativ", severity="major")
def test_create_booking_rejects_negative_price(auth_api, step):
    payload = BookingBuilder().with_price(-100).build()
    with step("POST /booking cu totalprice=-100"):
        resp = auth_api.create_booking(payload)
    if resp.status_code == 200:
        auth_api.delete_booking(resp.json()["bookingid"])
    check(resp.status_code == 400, expected="Status 400: prețul nu poate fi negativ",
          actual=f"Status {resp.status_code}, booking creat: {resp.text[:300]}")
