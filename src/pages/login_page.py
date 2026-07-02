from playwright.sync_api import Page, expect
from src.utils.config import config
from src.utils.logger import logger


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.sign_in_btn = page.locator("#signInBtn")
        self.alert_danger = page.locator(".alert-danger")
        self.radio_admin = page.locator("input[value='admin']")
        self.radio_user = page.locator("input[value='user']")
        self.role_dropdown = page.locator("select.form-control")
        self.terms_checkbox = page.locator("#terms")
        self.okay_btn = page.locator("#okayBtn")
        self.cancel_btn = page.locator("#cancelBtn")
        self.modal = page.locator("#myModal")

    def navigate(self) -> "LoginPage":
        logger.info(f"Navigating to {config.login_url}")
        self.page.goto(config.login_url, wait_until="networkidle")
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        logger.info(f"Logging in with username='{username}'")
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.sign_in_btn.click()
        return self

    def fill_username(self, username: str) -> "LoginPage":
        self.username_input.fill(username)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        self.password_input.fill(password)
        return self

    def click_sign_in(self) -> "LoginPage":
        self.sign_in_btn.click()
        return self

    def select_user_type(self, user_type: str) -> "LoginPage":
        if user_type.lower() == "user":
            self.radio_user.click()
        else:
            self.radio_admin.click()
        return self

    def select_role(self, role: str) -> "LoginPage":
        self.role_dropdown.select_option(role)
        return self

    def check_terms(self) -> "LoginPage":
        self.terms_checkbox.check()
        return self

    def wait_for_modal(self, timeout: int = 5000) -> bool:
        try:
            self.modal.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def accept_modal(self) -> "LoginPage":
        if self.wait_for_modal():
            logger.info("Accepting the 'limited functionality' modal")
            self.okay_btn.click()
        return self

    def cancel_modal(self) -> "LoginPage":
        if self.wait_for_modal():
            self.cancel_btn.click()
            self.page.wait_for_timeout(500)
        return self

    def complete_login(
        self,
        username: str | None = None,
        password: str | None = None,
        user_type: str = "admin",
        role: str = "stud",
        accept_terms: bool = True,
        expect_success: bool = True,
    ) -> "LoginPage":
        u = username or config.credentials["valid"]["username"]
        p = password or config.credentials["valid"]["password"]
        self.fill_username(u)
        self.fill_password(p)
        self.select_user_type(user_type)
        self.select_role(role)
        if accept_terms:
            self.check_terms()

        self.click_sign_in()
        if user_type.lower() == "user":
            self.accept_modal()

        if expect_success:
            self.page.wait_for_url("**/angularpractice/**", timeout=15000)
        else:
            self.page.wait_for_timeout(3000)

        return self

    def get_alert_text(self) -> str | None:
        if self.alert_danger.is_visible():
            return self.alert_danger.text_content()
        return None

    def alert_is_visible(self) -> bool:
        return self.alert_danger.is_visible()

    def is_error_displayed(self) -> bool:
        return self.alert_is_visible()
