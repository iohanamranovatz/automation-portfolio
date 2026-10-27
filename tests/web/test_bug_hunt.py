"""Aceleași scenarii rulate pe toți userii SauceDemo. Orice test picat generează un bug report în reports/bugs/."""
import time

import pytest

from config.settings import settings
from src.pages.web.cart_page import CartPage
from src.pages.web.checkout_page import CheckoutPage
from src.pages.web.inventory_page import InventoryPage
from src.pages.web.login_page import LoginPage
from src.pages.web.product_page import ProductPage
from src.reporting.bug_report import check

pytestmark = [pytest.mark.web, pytest.mark.regression]

USERS = ["standard_user", "problem_user", "error_user", "visual_user", "performance_glitch_user"]
all_users = pytest.mark.parametrize("user", USERS)


@pytest.fixture
def login_as(driver, step):
    def _login(user: str) -> InventoryPage:
        with step(f"Deschide {settings.web_url} și loghează-te cu '{user}' / '{settings.web_password}'"):
            LoginPage(driver).open().login(user, settings.web_password)
        return InventoryPage(driver)
    return _login


@all_users
@pytest.mark.defect(title="[{user}] Produsele afișează imagini duplicate", severity="minor")
def test_product_images_are_unique(login_as, step, user):
    inventory = login_as(user)
    with step("Verifică imaginile tuturor produselor din inventory"):
        sources = inventory.image_sources()
    duplicates = sorted({s.rsplit("/", 1)[-1] for s in sources if sources.count(s) > 1})
    check(not duplicates,
          expected=f"Fiecare din cele {len(sources)} produse are imaginea proprie",
          actual=f"Imagini folosite de mai multe produse: {duplicates}")


@all_users
@pytest.mark.parametrize("order, label, key, reverse", [
    ("lohi", "Price (low to high)", "prices", False),
    ("za", "Name (Z to A)", "names", True),
])
@pytest.mark.defect(title="[{user}] Sortarea '{label}' nu funcționează", severity="major")
def test_sorting(login_as, step, user, order, label, key, reverse):
    inventory = login_as(user)
    with step(f"Alege din dropdown-ul de sortare '{label}'"):
        inventory.sort_by(order)
    alert = inventory.accept_alert_if_present()
    check(alert is None, expected="Produsele se sortează fără erori",
          actual=f"Apare un alert JS: '{alert}'")
    values = inventory.item_names() if key == "names" else inventory.item_prices()
    check(values == sorted(values, reverse=reverse),
          expected=f"Produsele sunt ordonate {label}: {sorted(values, reverse=reverse)}",
          actual=f"Ordinea afișată: {values}")


@all_users
@pytest.mark.defect(title="[{user}] Add to cart / Remove nu funcționează pentru unele produse", severity="critical")
def test_add_and_remove_every_product(login_as, step, user):
    inventory = login_as(user)
    names = inventory.item_names()
    broken = []
    with step("Apasă 'Add to cart' pe fiecare produs, pe rând"):
        for i, name in enumerate(names):
            before = inventory.cart_count()
            inventory.click_item_button(i)
            if inventory.cart_count() != before + 1 or inventory.item_button_text(i) != "Remove":
                broken.append(f"Add: {name}")
    with step("Apasă 'Remove' pe fiecare produs, pe rând"):
        for i, name in enumerate(names):
            if inventory.item_button_text(i) != "Remove":
                continue
            before = inventory.cart_count()
            inventory.click_item_button(i)
            if inventory.cart_count() != before - 1 or inventory.item_button_text(i) != "Add to cart":
                broken.append(f"Remove: {name}")
    check(not broken, expected="Fiecare buton Add/Remove actualizează coșul și își schimbă textul",
          actual="Butoane care nu funcționează:\n" + "\n".join(f"- {b}" for b in broken))


@all_users
@pytest.mark.defect(title="[{user}] Click pe un produs deschide alt produs", severity="major")
def test_product_details_match_clicked_item(driver, login_as, step, user):
    inventory = login_as(user)
    mismatches = []
    for i, name in enumerate(inventory.item_names()):
        with step(f"Click pe numele produsului '{name}'"):
            inventory.open_item(i)
        opened = ProductPage(driver).name()
        if opened != name:
            mismatches.append(f"'{name}' -> s-a deschis '{opened}'")
        driver.back()
    check(not mismatches, expected="Pagina de detalii arată produsul pe care s-a dat click",
          actual="\n".join(f"- {m}" for m in mismatches))


@all_users
@pytest.mark.defect(title="[{user}] Prețul din coș diferă de prețul din inventory", severity="critical")
def test_cart_prices_match_inventory(driver, login_as, step, user):
    inventory = login_as(user)
    listed = dict(zip(inventory.item_names(), inventory.item_prices()))
    with step("Adaugă primele 3 produse în coș"):
        inventory.add_first_n_to_cart(3)
    with step("Deschide coșul"):
        inventory.go_to_cart()
    in_cart = CartPage(driver).prices_by_name()
    diffs = [f"{n}: inventory ${listed.get(n)} vs coș ${p}" for n, p in in_cart.items() if listed.get(n) != p]
    check(not diffs, expected="Prețurile din coș sunt identice cu cele din inventory",
          actual="\n".join(f"- {d}" for d in diffs))


@all_users
@pytest.mark.defect(title="[{user}] Formularul de checkout nu păstrează datele introduse", severity="critical")
def test_checkout_form_keeps_entered_values(driver, login_as, step, user):
    inventory = login_as(user)
    with step("Adaugă un produs în coș și deschide coșul"):
        inventory.add_first_n_to_cart(1)
        inventory.go_to_cart()
    with step("Apasă 'Checkout'"):
        CartPage(driver).checkout()
    entered = {"first": "Ana", "last": "Popescu", "postal_code": "400001"}
    checkout = CheckoutPage(driver)
    with step(f"Completează First Name='{entered['first']}', Last Name='{entered['last']}', "
              f"Postal Code='{entered['postal_code']}'"):
        checkout.fill_information(**entered)
    actual = checkout.entered_information()
    check(actual == entered, expected=f"Câmpurile conțin {entered}", actual=f"Câmpurile conțin {actual}")


@all_users
@pytest.mark.defect(title="[{user}] Comanda nu poate fi finalizată", severity="critical")
def test_complete_purchase(driver, login_as, step, user):
    inventory = login_as(user)
    with step("Adaugă un produs în coș și deschide coșul"):
        inventory.add_first_n_to_cart(1)
        inventory.go_to_cart()
    with step("Apasă 'Checkout'"):
        CartPage(driver).checkout()
    checkout = CheckoutPage(driver)
    with step("Completează datele de livrare și apasă 'Continue'"):
        checkout.fill_information("Ana", "Popescu", "400001")
        checkout.continue_()
    error = checkout.error_message()
    check(error is None, expected="Se ajunge la pasul 'Checkout: Overview'",
          actual=f"Rămâne pe formular cu eroarea: '{error}'")
    with step("Apasă 'Finish'"):
        checkout.finish()
    check(checkout.is_complete(), expected="Apare mesajul 'Thank you for your order!'",
          actual=f"Comanda nu se finalizează, pagina rămâne la {driver.current_url}")


@pytest.mark.defect(title="Checkout-ul este permis cu coșul gol", severity="major")
def test_checkout_blocked_with_empty_cart(driver, login_as, step):
    inventory = login_as("standard_user")
    with step("Deschide coșul fără să adaugi produse"):
        inventory.go_to_cart()
    with step("Apasă 'Checkout'"):
        CartPage(driver).checkout()
    check("checkout-step-one" not in driver.current_url,
          expected="Butonul 'Checkout' e dezactivat sau apare un mesaj că coșul e gol",
          actual=f"Utilizatorul ajunge în formularul de checkout ({driver.current_url}) cu 0 produse")


@pytest.mark.defect(title="Reset App State nu resetează butoanele 'Remove'", severity="minor")
def test_reset_app_state(login_as, step):
    inventory = login_as("standard_user")
    with step("Adaugă 2 produse în coș"):
        inventory.add_first_n_to_cart(2)
    with step("Deschide meniul și apasă 'Reset App State'"):
        inventory.reset_app_state()
    buttons = [inventory.item_button_text(i) for i in range(inventory.item_count())]
    check(inventory.cart_count() == 0 and "Remove" not in buttons,
          expected="Coșul e gol și toate butoanele sunt 'Add to cart'",
          actual=f"Coș: {inventory.cart_count()} produse; butoane: {buttons}")


LOGIN_SLA_SECONDS = 2


@all_users
@pytest.mark.defect(title="[{user}] Login-ul durează peste " + str(LOGIN_SLA_SECONDS) + "s", severity="major")
def test_login_performance(driver, login_as, step, user):
    start = time.perf_counter()
    inventory = login_as(user)
    inventory.is_loaded()
    duration = time.perf_counter() - start
    check(duration < LOGIN_SLA_SECONDS, expected=f"Inventory se încarcă în sub {LOGIN_SLA_SECONDS}s",
          actual=f"Inventory s-a încărcat în {duration:.1f}s")
