from selenium.webdriver.common.by import By

from src.pages.web.base_page import BasePage


class LoginPage(BasePage):
    path = "/"

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username: str, password: str):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        return self

    def error_message(self) -> str:
        return self.text_of(self.ERROR)
