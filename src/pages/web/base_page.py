from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings


class BasePage:
    path = "/"

    def __init__(self, driver, timeout: float = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(settings.web_url.rstrip("/") + self.path)
        return self

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text: str):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def text_of(self, locator) -> str:
        return self.find(locator).text

    def value_of(self, locator) -> str:
        return self.find(locator).get_attribute("value")

    def is_visible(self, locator) -> bool:
        return any(el.is_displayed() for el in self.find_all(locator))

    def accept_alert_if_present(self, timeout: float = 1) -> str | None:
        """Închide un alert JS neașteptat și întoarce textul lui (sau None dacă nu a apărut)."""
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        except TimeoutException:
            return None
        text = alert.text
        alert.accept()
        return text
