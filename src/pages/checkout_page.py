from playwright.sync_api import Page
from src.utils.logger import logger


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.country_input = page.locator("#country")
        self.country_suggestions = page.locator(".suggestions a")
        self.purchase_btn = page.locator("input.btn.btn-success.btn-lg[value='Purchase']")
        self.success_alert = page.locator(".alert-success")
        self.terms_checkbox = page.locator("#checkbox2")
        self.terms_label = page.locator("label[for='checkbox2']")

    def fill_country(self, country: str) -> "CheckoutPage":
        logger.info(f"Filling country: '{country}'")
        self.country_input.press_sequentially(country, delay=100)
        self.page.wait_for_timeout(3000)
        return self

    def select_country_suggestion(self, country: str) -> "CheckoutPage":
        suggestions = self.country_suggestions.all()
        for suggestion in suggestions:
            text = suggestion.text_content() or ""
            if country.lower() in text.lower():
                suggestion.click()
                logger.info(f"Selected country suggestion: '{text}'")
                self.page.wait_for_timeout(1000)
                break
        return self

    def check_terms(self) -> "CheckoutPage":
        logger.info("Checking terms checkbox")
        self.terms_label.click()
        return self

    def click_purchase(self) -> "CheckoutPage":
        logger.info("Clicking Purchase button")
        self.purchase_btn.click()
        self.page.wait_for_timeout(3000)
        return self

    def complete_purchase(self, country: str) -> str | None:
        self.fill_country(country)
        self.select_country_suggestion(country)
        self.check_terms()
        self.click_purchase()
        if self.success_alert.is_visible():
            msg = self.success_alert.text_content()
            logger.info(f"Purchase success: {msg}")
            return msg
        return None

    def get_success_message(self) -> str | None:
        if self.success_alert.is_visible():
            return self.success_alert.text_content()
        return None

    def is_purchase_successful(self) -> bool:
        return self.success_alert.is_visible()
