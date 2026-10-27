from selenium.webdriver.common.by import By

from src.pages.web.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    CHECKOUT = (By.CSS_SELECTOR, "[data-test='checkout']")

    def item_count(self) -> int:
        return len(self.find_all(self.ITEMS))

    def prices_by_name(self) -> dict[str, float]:
        names = [el.text for el in self.find_all(self.ITEM_NAMES)]
        prices = [float(el.text.replace("$", "")) for el in self.find_all(self.ITEM_PRICES)]
        return dict(zip(names, prices))

    def checkout(self):
        self.click(self.CHECKOUT)
