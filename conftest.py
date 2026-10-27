import platform

import allure
import pytest
from selenium import webdriver

from config.settings import settings
from src.api.booking_client import BookingClient
from src.builder.booking_builder import BookingBuilder
from src.reporting import bug_report
from src.reporting.bug_report import BugFound, BugReport, StepRecorder

STEPS_KEY = pytest.StashKey[StepRecorder]()
IGNORED_CONSOLE = ("backtrace.io",)  


# ---------- BUG REPORTS ----------
def pytest_configure(config):
    # doar procesul principal curăță folderul (cu xdist, workerii au "workerinput")
    if not hasattr(config, "workerinput"):
        bug_report.reset_reports_dir()


def pytest_sessionfinish(session):
    if not hasattr(session.config, "workerinput"):
        bug_report.write_index()


@pytest.fixture
def step(request):
    recorder = StepRecorder()
    request.node.stash[STEPS_KEY] = recorder
    return recorder


def _browser_evidence(drv):
    """Screenshot, URL, erori din consolă. Nu trebuie să strice raportul dacă browserul e într-o stare ciudată."""
    png, url, console = None, None, []
    try:
        drv.switch_to.alert.accept()
    except Exception:
        pass
    try:
        png = drv.get_screenshot_as_png()
        url = drv.current_url
        console = [e["message"] for e in drv.get_log("browser")
                   if e["level"] == "SEVERE" and not any(s in e["message"] for s in IGNORED_CONSOLE)]
    except Exception:
        pass
    return png, url, console


def _environment(item, drv) -> dict:
    env = {"OS": f"{platform.system()} {platform.release()}", "Base URL": settings.web_url}
    if drv:
        caps = drv.capabilities
        env["Browser"] = f"{caps.get('browserName')} {caps.get('browserVersion')}"
        env["Headless"] = settings.headless
    if hasattr(item, "callspec"):
        env.update({f"Param `{k}`": v for k, v in item.callspec.params.items()})
    return env


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    drv = item.funcargs.get("driver")
    png, url, console = _browser_evidence(drv) if drv else (None, None, [])
    if png:
        allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)

    marker = item.get_closest_marker("defect")
    meta = marker.kwargs if marker else {}
    params = item.callspec.params if hasattr(item, "callspec") else {}
    title = meta.get("title", (item.function.__doc__ or item.name).strip().splitlines()[0])

    exc = call.excinfo.value
    if isinstance(exc, BugFound):
        expected, actual = exc.expected, exc.actual
    else:
        expected = meta.get("expected", "Testul trece fără erori")
        actual = call.excinfo.exconly()

    bug = BugReport(
        id=bug_report.bug_id(item.nodeid),
        title=title.format(**params),
        severity=meta.get("severity", "major"),
        test=item.nodeid,
        steps=item.stash[STEPS_KEY].steps if STEPS_KEY in item.stash else [],
        expected=expected,
        actual=actual,
        environment=_environment(item, drv),
        url=url,
        console_errors=console,
    )
    path = bug_report.save(bug, png)
    allure.attach(bug.to_markdown(), name=f"Bug report {bug.id}", attachment_type=allure.attachment_type.TEXT)
    report.sections.append(("Bug report", f"{bug.id} -> {path}"))


# ---------- WEB ----------
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})  # pentru erorile din consolă
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


# ---------- API ----------
@pytest.fixture(scope="session")
def api():
    return BookingClient()


@pytest.fixture(scope="session")
def auth_api():
    client = BookingClient()
    client.authenticate(settings.api_user, settings.api_password)
    return client


@pytest.fixture
def booking(auth_api):
    """Creează un booking pentru test și îl șterge după (cleanup)."""
    payload = BookingBuilder().build()
    resp = auth_api.create_booking(payload)
    assert resp.status_code == 200
    booking_id = resp.json()["bookingid"]
    yield booking_id, payload
    auth_api.delete_booking(booking_id)
