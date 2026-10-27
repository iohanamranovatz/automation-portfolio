from selenium.webdriver.common.by import By

from src.pages.web.base_page import BasePage


class ProductPage(BasePage):
    NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")

    def name(self) -> str:
        return self.text_of(self.NAME)
