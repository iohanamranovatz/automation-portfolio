from datetime import date, timedelta
from faker import Faker

fake = Faker()

class BookingBuilder:
    def __init__(self):
        checkin = date.today() + timedelta(days=fake.random_int(1, 30))
        self._data = {
            "firstname": fake.first_name(),
            "lastname": fake.last_name(),
            "totalprice": fake.random_int(50, 2000),
            "depositpaid": fake.boolean(),
            "bookingdates": {
                "checkin": checkin.isoformat(),
                "checkout": (checkin + timedelta(days=fake.random_int(1, 14))).isoformat(),
            },
            "additionalneeds": fake.random_element(["Breakfast", "Lunch", "Late checkout"]),
        }

    def with_name(self, first, last):
        self._data["firstname"], self._data["lastname"] = first, last
        return self

    def with_price(self, price):
        self._data["totalprice"] = price
        return self

    def with_dates(self, checkin: date, checkout: date):
        self._data["bookingdates"] = {"checkin": checkin.isoformat(),
                                      "checkout": checkout.isoformat()}
        return self

    def with_deposit(self, paid=True):
        self._data["depositpaid"] = paid
        return self

    def without_field(self, field):        
        # pentru teste negative
        self._data.pop(field, None)
        return self

    def build(self) -> dict:
        return dict(self._data)