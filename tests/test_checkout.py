"""Checkout flow tests for ProtoCommerce"""
import pytest


class TestCheckout:
    @pytest.mark.smoke
    @pytest.mark.checkout
    def test_checkout_button_visible_in_cart(self, authenticated_shop_page, cart_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        assert cart_page.checkout_btn.is_visible(), "Checkout button should be visible in cart table"

    @pytest.mark.smoke
    @pytest.mark.checkout
    def test_proceed_to_checkout_page(self, authenticated_shop_page, cart_page, checkout_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        cart_page.proceed_to_checkout()
        assert checkout_page.purchase_btn.is_visible(), "Purchase button should be visible on checkout page"

    @pytest.mark.regression
    @pytest.mark.checkout
    def test_country_suggestions_appear(self, authenticated_shop_page, cart_page, checkout_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        cart_page.proceed_to_checkout()
        checkout_page.fill_country("Ind")
        suggestions = checkout_page.country_suggestions
        suggestions.first.wait_for(state="visible", timeout=10000)
        suggestion_count = len(suggestions.all())
        assert suggestion_count > 0, "Country suggestions should appear"

    @pytest.mark.smoke
    @pytest.mark.checkout
    def test_complete_purchase_flow(self, authenticated_shop_page, cart_page, checkout_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        cart_page.proceed_to_checkout()
        msg = checkout_page.complete_purchase("India")
        assert msg is not None, "Purchase should be successful"
        assert "Success" in msg, f"Success message should contain 'Success', got: '{msg}'"

    @pytest.mark.regression
    @pytest.mark.checkout
    def test_purchase_success_message(self, authenticated_shop_page, cart_page, checkout_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        cart_page.proceed_to_checkout()
        checkout_page.fill_country("India")
        checkout_page.select_country_suggestion("India")
        checkout_page.check_terms()
        checkout_page.click_purchase()
        msg = checkout_page.get_success_message()
        assert msg is not None, "Purchase should show a success message"
        assert "Success" in msg, f"Success message should contain 'Success', got: '{msg}'"

    @pytest.mark.regression
    @pytest.mark.checkout
    def test_terms_checkbox_on_checkout(self, authenticated_shop_page, cart_page, checkout_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()
        cart_page.proceed_to_checkout()
        assert checkout_page.terms_checkbox.is_visible(), "Terms checkbox should be visible"
        assert not checkout_page.terms_checkbox.is_checked(), "Terms should be unchecked by default"
        checkout_page.check_terms()
        assert checkout_page.terms_checkbox.is_checked(), "Terms should be checked after clicking"
