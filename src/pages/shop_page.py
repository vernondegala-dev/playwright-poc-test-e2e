from playwright.sync_api import Page
from src.utils.config import config
from src.utils.logger import logger


class ShopPage:
    def __init__(self, page: Page):
        self.page = page
        self.nav_home = page.locator("a.nav-link[href='/angularpractice']")
        self.nav_shop = page.locator("a.nav-link[href='/angularpractice/shop']")
        self.checkout_link = page.locator("a.btn.btn-primary:has-text('Checkout')")
        self.product_cards = page.locator("app-card")
        self.product_titles = page.locator("app-card .card-title")
        self.add_buttons = page.locator("app-card .card-footer .btn.btn-info")

    def navigate(self) -> "ShopPage":
        logger.info(f"Navigating to shop: {config.shop_url}")
        self.page.goto(config.shop_url, wait_until="networkidle")
        self.page.wait_for_selector("app-card", timeout=10000)
        return self

    def add_product_to_cart(self, product_name: str) -> bool:
        logger.info(f"Adding product to cart: '{product_name.strip()}'")
        cards = self.product_cards.all()
        for card in cards:
            title = card.locator(".card-title").text_content()
            if title and product_name.strip().lower() in title.strip().lower():
                card.locator(".card-footer .btn.btn-info").click()
                logger.info(f"Added '{title.strip()}' to cart")
                return True
        logger.warning(f"Product '{product_name}' not found")
        return False

    def add_all_products_to_cart(self) -> int:
        buttons = self.add_buttons.all()
        for btn in buttons:
            btn.click()
            self.page.wait_for_timeout(500)
        count = len(buttons)
        logger.info(f"Added {count} products to cart")
        return count

    def get_product_count(self) -> int:
        return len(self.product_cards.all())

    def get_product_names(self) -> list[str]:
        titles = self.product_titles.all()
        return [(t.text_content() or "").strip() for t in titles]

    def go_to_cart(self) -> None:
        logger.info("Navigating to cart via Checkout link")
        self.checkout_link.click()
        self.page.wait_for_load_state("networkidle")

    def is_shop_loaded(self) -> bool:
        return "/shop" in self.page.url
