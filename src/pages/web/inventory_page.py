from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from src.pages.web.base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ITEM_IMAGES = (By.CSS_SELECTOR, "[data-test='inventory-item'] img")
    ITEM_BUTTONS = (By.CSS_SELECTOR, "[data-test='inventory-item'] button")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button[data-test^='add-to-cart']")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    SORT = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    RESET_LINK = (By.ID, "reset_sidebar_link")

    def is_loaded(self) -> bool:
        return self.text_of(self.TITLE) == "Products"

    def item_count(self) -> int:
        self.find(self.ITEMS)
        return len(self.find_all(self.ITEMS))

    def item_names(self) -> list[str]:
        return [el.text for el in self.find_all(self.ITEM_NAMES)]

    def item_prices(self) -> list[float]:
        return [float(el.text.replace("$", "")) for el in self.find_all(self.ITEM_PRICES)]

    def image_sources(self) -> list[str]:
        return [el.get_attribute("src") for el in self.find_all(self.ITEM_IMAGES)]

    def add_first_n_to_cart(self, n: int):
        for _ in range(n):
            # după click butonul devine "Remove", așa că luăm mereu primul "Add" rămas
            self.find_all(self.ADD_TO_CART_BUTTONS)[0].click()

    def click_item_button(self, index: int):
        self.find_all(self.ITEM_BUTTONS)[index].click()

    def item_button_text(self, index: int) -> str:
        return self.find_all(self.ITEM_BUTTONS)[index].text

    def open_item(self, index: int):
        self.find_all(self.ITEM_NAMES)[index].click()

    def cart_count(self) -> int:
        return int(self.text_of(self.CART_BADGE)) if self.is_visible(self.CART_BADGE) else 0

    def sort_by(self, value: str):
        # valori: "az", "za", "lohi", "hilo"
        Select(self.find(self.SORT)).select_by_value(value)

    def go_to_cart(self):
        self.click(self.CART_LINK)

    def reset_app_state(self):
        self.click(self.MENU_BUTTON)
        self.click(self.RESET_LINK)
