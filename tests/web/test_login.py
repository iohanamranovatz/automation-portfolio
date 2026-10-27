import pytest

from config.settings import settings
from src.pages.web.inventory_page import InventoryPage
from src.pages.web.login_page import LoginPage

pytestmark = pytest.mark.web


@pytest.fixture
def logged_in(driver):
    LoginPage(driver).open().login(settings.web_user, settings.web_password)
    return InventoryPage(driver)


@pytest.mark.smoke
def test_valid_login(logged_in):
    assert logged_in.is_loaded()
    assert logged_in.item_count() == 6


@pytest.mark.regression
@pytest.mark.parametrize("user, password, expected", [
    ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out."),
    ("standard_user", "wrong", "Username and password do not match"),
    ("", "secret_sauce", "Username is required"),
    ("standard_user", "", "Password is required"),
])
def test_invalid_login(driver, user, password, expected):
    page = LoginPage(driver).open()
    page.login(user, password)
    assert expected in page.error_message()


@pytest.mark.smoke
def test_add_items_to_cart(logged_in):
    logged_in.add_first_n_to_cart(3)
    assert logged_in.cart_count() == 3


@pytest.mark.regression
def test_inventory_requires_login(driver):
    InventoryPage(driver).open()
    assert "You can only access '/inventory.html' when you are logged in" in LoginPage(driver).error_message()
