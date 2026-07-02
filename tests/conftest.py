import json
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Page

from src.pages.login_page import LoginPage
from src.pages.shop_page import ShopPage
from src.pages.cart_page import CartPage
from src.pages.checkout_page import CheckoutPage
from src.utils.config import config as app_config
from src.utils.logger import logger


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--headless", action="store_true", default=app_config.headless,
                     help="Run in headless mode")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config):
    Path(app_config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    Path(app_config.report_dir).mkdir(parents=True, exist_ok=True)
    logger.info("Test framework initialized")


@pytest.fixture(scope="function")
def page(browser, request) -> Page:
    context = browser.new_context(
        viewport={"width": app_config.viewport_width, "height": app_config.viewport_height},
        ignore_https_errors=True,
    )
    context.set_default_timeout(app_config.timeout)
    p = context.new_page()
    yield p
    context.close()


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture(scope="function")
def shop_page(page: Page) -> ShopPage:
    return ShopPage(page)


@pytest.fixture(scope="function")
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture(scope="function")
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture(scope="function")
def authenticated_page(login_page: LoginPage, page: Page):
    login_page.navigate()
    login_page.complete_login()
    return page


@pytest.fixture(scope="function")
def authenticated_shop_page(authenticated_page, shop_page: ShopPage) -> ShopPage:
    shop_page.navigate()
    return shop_page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = Path(app_config.screenshot_dir) / f"failure_{item.name}_{timestamp}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.error(f"Screenshot saved: {screenshot_path}")

            html_path = Path(app_config.screenshot_dir) / f"failure_{item.name}_{timestamp}.html"
            page.content()
            with open(html_path, "w") as f:
                f.write(page.content())
            logger.error(f"Page source saved: {html_path}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    logger.info(f"Test session finished with exit status: {exitstatus}")
    summary = {
        "timestamp": datetime.now().isoformat(),
        "exit_status": exitstatus,
        "total": getattr(session, "testscollected", 0),
        "failed": 0,
    }
    summary_path = Path(app_config.report_dir) / "session_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
