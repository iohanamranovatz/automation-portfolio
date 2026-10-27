import requests

from config.settings import settings


class BookingClient:
   
    def __init__(self, base_url: str = settings.api_url, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json",
                                     "Accept": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    #endpoint to check if the api is up
    def ping(self):
        return self.session.get(self._url("/ping"), timeout=self.timeout)

    def create_token(self, username: str, password: str):
        return self.session.post(self._url("/auth"), timeout=self.timeout,
                                 json={"username": username, "password": password})

    def authenticate(self, username: str, password: str) -> str:
        token = self.create_token(username, password).json().get("token")
        if not token:
            raise RuntimeError("Failed authentification, check  API_USER / API_PASSWORD")
        self.session.cookies.set("token", token)
        return token

    #CRUD
    def get_booking_ids(self, **filters):
        return self.session.get(self._url("/booking"), params=filters, timeout=self.timeout)

    def get_booking(self, booking_id: int):
        return self.session.get(self._url(f"/booking/{booking_id}"), timeout=self.timeout)

    def create_booking(self, payload: dict):
        return self.session.post(self._url("/booking"), json=payload, timeout=self.timeout)

    def update_booking(self, booking_id: int, payload: dict):
        return self.session.put(self._url(f"/booking/{booking_id}"), json=payload, timeout=self.timeout)

    def partial_update_booking(self, booking_id: int, payload: dict):
        return self.session.patch(self._url(f"/booking/{booking_id}"), json=payload, timeout=self.timeout)

    def delete_booking(self, booking_id: int):
        return self.session.delete(self._url(f"/booking/{booking_id}"), timeout=self.timeout)
