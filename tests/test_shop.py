"""Shopping page tests for ProtoCommerce shop"""
import pytest
from src.utils.logger import logger


class TestShop:
    @pytest.mark.smoke
    @pytest.mark.shop
    def test_shop_page_loads_after_login(self, authenticated_shop_page):
        assert authenticated_shop_page.is_shop_loaded(), "Shop page should load after login"

    @pytest.mark.smoke
    @pytest.mark.shop
    def test_products_are_displayed(self, authenticated_shop_page):
        count = authenticated_shop_page.get_product_count()
        logger.info(f"Found {count} products on shop page")
        assert count > 0, "At least one product should be displayed"

    @pytest.mark.regression
    @pytest.mark.shop
    def test_product_names_are_visible(self, authenticated_shop_page):
        names = authenticated_shop_page.get_product_names()
        assert len(names) > 0, "Product names should be visible"
        for name in names:
            assert name and name.strip(), f"Product name should not be empty, got: '{name}'"

    @pytest.mark.smoke
    @pytest.mark.shop
    def test_add_single_product_to_cart(self, authenticated_shop_page, cart_page):
        authenticated_shop_page.navigate()
        name = authenticated_shop_page.get_product_names()[0]
        added = authenticated_shop_page.add_product_to_cart(name)
        assert added, f"Should be able to add '{name}' to cart"

        authenticated_shop_page.go_to_cart()
        assert cart_page.get_cart_item_count() >= 1, "Cart should have at least 1 item"

    @pytest.mark.regression
    @pytest.mark.shop
    def test_add_all_products_to_cart(self, authenticated_shop_page, cart_page):
        authenticated_shop_page.navigate()
        count = authenticated_shop_page.add_all_products_to_cart()
        assert count > 0, "Should add at least one product"

        authenticated_shop_page.go_to_cart()
        cart_count = cart_page.get_cart_item_count()
        assert cart_count == count, f"Cart should have {count} items, has {cart_count}"

    @pytest.mark.regression
    @pytest.mark.shop
    def test_cart_item_details_displayed(self, authenticated_shop_page, cart_page):
        authenticated_shop_page.navigate()
        authenticated_shop_page.add_product_to_cart(authenticated_shop_page.get_product_names()[0])
        authenticated_shop_page.go_to_cart()

        items = cart_page.get_cart_items()
        assert len(items) > 0, "Cart should have items"
        assert items[0]["name"], "Item should have a name"
        assert items[0]["price"], "Item should have a price"

    @pytest.mark.regression
    @pytest.mark.shop
    def test_navigation_bar_elements(self, authenticated_shop_page):
        assert authenticated_shop_page.nav_home.is_visible()
        assert authenticated_shop_page.nav_shop.is_visible()
        assert authenticated_shop_page.checkout_link.is_visible()
