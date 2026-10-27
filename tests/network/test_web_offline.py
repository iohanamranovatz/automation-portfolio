import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import settings
from src.pages.web.inventory_page import InventoryPage
from src.pages.web.login_page import LoginPage

pytestmark = [pytest.mark.network, pytest.mark.web, pytest.mark.regression]


def test_page_does_not_load_offline(driver):
    driver.set_network_conditions(offline=True, latency=0,
                                  download_throughput=0, upload_throughput=0)
    with pytest.raises(WebDriverException, match="ERR_INTERNET_DISCONNECTED"):
        LoginPage(driver).open()


def test_login_works_on_slow_3g(driver):
    driver.set_network_conditions(offline=False, latency=400,
                                  download_throughput=50 * 1024, upload_throughput=20 * 1024)
    page = LoginPage(driver, timeout=60).open()
    page.login(settings.web_user, settings.web_password)
    assert "inventory.html" in driver.current_url


def test_going_offline_after_login(driver):
    LoginPage(driver).open().login(settings.web_user, settings.web_password)
    driver.set_network_conditions(offline=True, latency=0,
                                  download_throughput=0, upload_throughput=0)
    # refresh() nu aruncă excepție: Chrome afișează pagina lui de eroare, deci verificăm conținutul
    driver.refresh()
    assert "ERR_INTERNET_DISCONNECTED" in driver.page_source
    assert not InventoryPage(driver).find_all(InventoryPage.ITEMS)
