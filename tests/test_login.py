"""Login page tests for rahulshettyacademy.com/loginpagePractise/"""
import pytest
from src.utils.config import config
from src.utils.logger import logger


class TestLogin:
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_page_loads(self, login_page, page):
        login_page.navigate()
        assert page.title() == "LoginPage Practise | Rahul Shetty Academy"
        assert login_page.sign_in_btn.is_visible()
        assert login_page.username_input.is_visible()
        assert login_page.password_input.is_visible()

    @pytest.mark.smoke
    @pytest.mark.login
    def test_valid_login_redirects_to_shop(self, login_page, page):
        login_page.navigate()
        login_page.complete_login()
        assert "/shop" in page.url or "angularpractice" in page.url, \
            f"Expected shop URL, got: {page.url}"

    @pytest.mark.regression
    @pytest.mark.login
    def test_invalid_login_shows_error(self, login_page):
        login_page.navigate()
        creds = config.credentials["invalid"]
        login_page.complete_login(
            username=creds["username"],
            password=creds["password"],
            expect_success=False,
        )
        assert login_page.is_error_displayed(), "Error alert should be displayed for invalid credentials"

    @pytest.mark.regression
    @pytest.mark.login
    def test_empty_credentials_shows_error(self, login_page):
        login_page.navigate()
        login_page.login("", "")
        assert login_page.is_error_displayed(), "Error alert should be displayed for empty credentials"

    @pytest.mark.regression
    @pytest.mark.login
    def test_old_password_shows_upgrade_message(self, login_page):
        login_page.navigate()
        creds = config.credentials["old_password"]
        login_page.complete_login(
            username=creds["username"],
            password=creds["password"],
            expect_success=False,
        )
        alert = login_page.get_alert_text()
        assert alert is not None, "Alert should be displayed"
        assert "Old password" in alert or "no longer valid" in alert, \
            f"Expected old password message, got: {alert}"

    @pytest.mark.regression
    @pytest.mark.login
    def test_user_type_radio_admin_default(self, login_page):
        login_page.navigate()
        assert login_page.radio_admin.is_checked(), "Admin radio should be checked by default"

    @pytest.mark.regression
    @pytest.mark.login
    def test_user_type_radio_user_triggers_modal(self, login_page):
        login_page.navigate()
        login_page.select_user_type("user")
        assert login_page.wait_for_modal(), "Modal should appear when selecting User radio"

    @pytest.mark.smoke
    @pytest.mark.login
    def test_modal_accept_keeps_user_selected(self, login_page):
        login_page.navigate()
        login_page.select_user_type("user")
        login_page.accept_modal()
        assert login_page.radio_user.is_checked(), "User radio should remain checked after accepting modal"

    @pytest.mark.regression
    @pytest.mark.login
    def test_modal_cancel_reverts_to_admin(self, login_page):
        login_page.navigate()
        login_page.select_user_type("user")
        login_page.cancel_modal()
        assert login_page.radio_admin.is_checked(), "Admin radio should be selected after cancel"

    @pytest.mark.regression
    @pytest.mark.login
    def test_role_dropdown_options(self, login_page):
        login_page.navigate()
        options = login_page.role_dropdown.locator("option").all()
        option_texts = [opt.text_content() for opt in options]
        assert "Student" in option_texts
        assert "Teacher" in option_texts
        assert "Consultant" in option_texts

    @pytest.mark.regression
    @pytest.mark.login
    def test_terms_checkbox_functionality(self, login_page):
        login_page.navigate()
        assert not login_page.terms_checkbox.is_checked(), "Terms checkbox should be unchecked by default"
        login_page.check_terms()
        assert login_page.terms_checkbox.is_checked(), "Terms checkbox should be checked after clicking"

    @pytest.mark.smoke
    @pytest.mark.login
    def test_sign_in_button_text(self, login_page):
        login_page.navigate()
        assert login_page.sign_in_btn.input_value() == "Sign In"

    @pytest.mark.regression
    @pytest.mark.login
    def test_login_with_different_roles(self, login_page, page):
        login_page.navigate()
        login_page.complete_login(role="teach")
        assert "/shop" in page.url or "angularpractice" in page.url
