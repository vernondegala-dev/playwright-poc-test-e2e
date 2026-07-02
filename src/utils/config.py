import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TestConfig:
    base_url: str = os.getenv("BASE_URL", "https://rahulshettyacademy.com")
    login_path: str = os.getenv("LOGIN_PATH", "/loginpagePractise/")
    shop_path: str = os.getenv("SHOP_PATH", "/angularpractice/shop")
    angular_base: str = os.getenv("ANGULAR_BASE", "https://rahulshettyacademy.com/angularpractice")

    username: str = os.getenv("TEST_USERNAME", "rahulshettyacademy")
    password: str = os.getenv("TEST_PASSWORD", "Learning@830$3mK2")

    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"
    browser: str = os.getenv("BROWSER", "chromium")
    slow_mo: int = int(os.getenv("SLOW_MO", "0"))
    viewport_width: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    viewport_height: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))
    timeout: int = int(os.getenv("PLAYWRIGHT_TIMEOUT", "30000"))
    retries: int = int(os.getenv("TEST_RETRIES", "2"))

    screenshot_dir: str = os.getenv("SCREENSHOT_DIR", "screenshots")
    report_dir: str = os.getenv("REPORT_DIR", "reports")

    grid_url: Optional[str] = os.getenv("SELENIUM_GRID_URL") or os.getenv("PLAYWRIGHT_GRID_URL")

    env: str = os.getenv("TEST_ENV", "production")

    credentials: dict = field(default_factory=lambda: {
        "valid": {
            "username": os.getenv("TEST_USERNAME", "rahulshettyacademy"),
            "password": os.getenv("TEST_PASSWORD", "Learning@830$3mK2"),
        },
        "invalid": {
            "username": "wronguser",
            "password": "wrongpass",
        },
        "old_password": {
            "username": "rahulshettyacademy",
            "password": "learning",
        },
    })

    @property
    def login_url(self) -> str:
        return f"{self.base_url}{self.login_path}"

    @property
    def shop_url(self) -> str:
        return f"{self.base_url}{self.shop_path}"

    def browser_args(self) -> list[str]:
        args = ["--no-sandbox", "--disable-dev-shm-usage"]
        if self.headless:
            args.append("--headless=new")
        return args


config = TestConfig()
