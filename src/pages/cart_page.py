from playwright.sync_api import Page
from src.utils.logger import logger


class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_table = page.locator("table.table-hover")
        self.cart_rows = page.locator("table.table-hover tbody tr")
        self.checkout_btn = page.locator("button.btn.btn-success:has-text('Checkout')")
        self.continue_shopping_btn = page.locator("button:has-text('Continue Shopping')")
        self.remove_btns = page.locator("button.btn.btn-danger")
        self.total_value = page.locator("h3 strong")

    def get_cart_item_count(self) -> int:
        rows = self.cart_rows.all()
        product_rows = [r for r in rows if r.locator("td .media").count() > 0]
        return len(product_rows)

    def get_cart_items(self) -> list[dict]:
        items = []
        rows = self.cart_rows.all()
        for row in rows:
            media = row.locator("td .media")
            if media.count() == 0:
                continue
            name = media.locator(".media-heading a").first.text_content() or ""
            price = row.locator("td strong").first.text_content() or ""
            items.append({
                "name": name.strip(),
                "price": price.strip(),
            })
        return items

    def remove_item(self, index: int = 0) -> None:
        btns = self.remove_btns.all()
        if index < len(btns):
            btns[index].click()
            self.page.wait_for_timeout(1000)
            logger.info(f"Removed item at index {index} from cart")

    def proceed_to_checkout(self) -> None:
        logger.info("Proceeding to checkout")
        self.checkout_btn.click()
        self.page.wait_for_timeout(2000)

    def is_cart_empty(self) -> bool:
        return self.get_cart_item_count() == 0
