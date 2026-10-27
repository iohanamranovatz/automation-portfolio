from selenium.webdriver.common.by import By

from src.pages.web.base_page import BasePage


class CheckoutPage(BasePage):
    # pasul 1 - informații
    FIRST_NAME = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE = (By.CSS_SELECTOR, "[data-test='continue']")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")
    # pasul 2 - overview
    FINISH = (By.CSS_SELECTOR, "[data-test='finish']")
    # complete
    COMPLETE_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")

    def fill_information(self, first: str, last: str, postal_code: str):
        self.type(self.FIRST_NAME, first)
        self.type(self.LAST_NAME, last)
        self.type(self.POSTAL_CODE, postal_code)

    def entered_information(self) -> dict:
        return {"first": self.value_of(self.FIRST_NAME),
                "last": self.value_of(self.LAST_NAME),
                "postal_code": self.value_of(self.POSTAL_CODE)}

    def continue_(self):
        self.click(self.CONTINUE)

    def finish(self):
        self.click(self.FINISH)

    def is_complete(self) -> bool:
        return self.is_visible(self.COMPLETE_HEADER)

    def error_message(self) -> str | None:
        return self.text_of(self.ERROR) if self.is_visible(self.ERROR) else None
