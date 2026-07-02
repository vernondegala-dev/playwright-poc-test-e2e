"""Self-Healing Agent for flaky test resolution.

Monitors test failures, identifies flaky selectors, and attempts to
auto-heal by finding alternative selectors when locators fail.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.logger import logger


class HealRecord:
    def __init__(self, test_name: str, original_selector: str, healed_selector: str,
                 strategy: str, timestamp: str | None = None):
        self.test_name = test_name
        self.original_selector = original_selector
        self.healed_selector = healed_selector
        self.strategy = strategy
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "original_selector": self.original_selector,
            "healed_selector": self.healed_selector,
            "strategy": self.strategy,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HealRecord":
        return cls(
            test_name=data["test_name"],
            original_selector=data["original_selector"],
            healed_selector=data["healed_selector"],
            strategy=data["strategy"],
            timestamp=data.get("timestamp"),
        )


class SelfHealer:
    HEAL_DB_PATH = Path("reports/heal_db.json")

    def __init__(self):
        self.heal_db: list[HealRecord] = []
        self._load()

    def _load(self) -> None:
        if self.HEAL_DB_PATH.exists():
            try:
                data = json.loads(self.HEAL_DB_PATH.read_text())
                self.heal_db = [HealRecord.from_dict(r) for r in data]
                logger.info(f"Loaded {len(self.heal_db)} heal records")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to load heal DB: {e}")
                self.heal_db = []

    def _save(self) -> None:
        self.HEAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [r.to_dict() for r in self.heal_db]
        self.HEAL_DB_PATH.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved {len(self.heal_db)} heal records")

    def find_alternative_selector(self, page_source: str, target_text: str,
                                  tag_hint: str | None = None) -> str | None:
        strategies = [
            ("text_contains", self._try_text_contains),
            ("aria_label", self._try_aria_label),
            ("placeholder", self._try_placeholder),
            ("css_class", self._try_css_class),
            ("data_attribute", self._try_data_attribute),
            ("nth_child", self._try_nth_child),
            ("xpath_contains", self._try_xpath_contains),
        ]

        for strategy_name, strategy_fn in strategies:
            result = strategy_fn(page_source, target_text, tag_hint)
            if result:
                logger.info(f"Self-healer found alternative via '{strategy_name}': {result}")
                return result
        return None

    def _try_text_contains(self, source: str, text: str, tag: str | None = None) -> str | None:
        escaped = re.escape(text)
        pattern = f">{escaped}<"
        if tag:
            pattern = f"<{tag}[^>]*>[^<]*{escaped}[^<]*</{tag}>"
        if re.search(pattern, source, re.IGNORECASE):
            selector = f"text={text}" if not tag else f"{tag}:has-text('{text}')"
            return selector
        return None

    def _try_aria_label(self, source: str, text: str, tag: str | None = None) -> str | None:
        escaped = re.escape(text)
        pattern = f'aria-label=["\']([^"\']*{escaped}[^"\']*)["\']'
        match = re.search(pattern, source, re.IGNORECASE)
        if match:
            return f'[aria-label="{match.group(1)}"]'
        return None

    def _try_placeholder(self, source: str, text: str, tag: str | None = None) -> str | None:
        escaped = re.escape(text)
        pattern = f'placeholder=["\']([^"\']*{escaped}[^"\']*)["\']'
        match = re.search(pattern, source, re.IGNORECASE)
        if match:
            return f'[placeholder="{match.group(1)}"]'
        return None

    def _try_css_class(self, source: str, text: str, tag: str | None = None) -> str | None:
        if not tag:
            return None
        tag_pattern = re.compile(
            rf'<{tag}[^>]*class=["\']([^"\']*)["\']',
            re.IGNORECASE
        )
        match = tag_pattern.search(source)
        if match:
            classes = match.group(1).split()
            if classes:
                return f"{tag}.{classes[0]}"
        return None

    def _try_data_attribute(self, source: str, text: str, tag: str | None = None) -> str | None:
        pattern = r'data-[a-zA-Z-]+=["\']([^"\']*)["\']'
        matches = re.findall(pattern, source)
        if matches:
            return f"text={text}"
        return None

    def _try_nth_child(self, source: str, text: str, tag: str | None = None) -> str | None:
        t = tag or "button|a|input|div|span"
        pattern = rf'<(?:{t})[^>]*>({re.escape(text)})</(?:{t})>'
        match = re.search(pattern, source)
        if match:
            return f"text={text}"
        return None

    def _try_xpath_contains(self, source: str, text: str, tag: str | None = None) -> str | None:
        escaped = re.escape(text)
        t = tag or "*"
        pattern = f'<{t}[^>]*>[^<]*{escaped}[^<]*</{t}>'
        if re.search(pattern, source, re.IGNORECASE):
            return f"xpath=//{t}[contains(text(), '{text}')]"
        return None

    def record_heal(self, test_name: str, original: str, healed: str, strategy: str) -> None:
        record = HealRecord(test_name, original, healed, strategy)
        self.heal_db.append(record)
        self._save()
        logger.info(f"Recorded heal: {original} -> {healed} ({strategy})")

    def get_heal_suggestion(self, test_name: str, failed_selector: str) -> str | None:
        for record in self.heal_db:
            if record.test_name == test_name and record.original_selector == failed_selector:
                logger.info(f"Found previous heal for {test_name}: {record.healed_selector}")
                return record.healed_selector
        return None

    def is_flaky(self, test_name: str, failure_count: int = 2) -> bool:
        related = [r for r in self.heal_db if r.test_name == test_name]
        return len(related) >= failure_count

    def generate_healed_test(self, test_name: str) -> str | None:
        if not self.is_flaky(test_name):
            return None

        records = [r for r in self.heal_db if r.test_name == test_name]
        if not records:
            return None

        code = f'''"""
Auto-healed test for flaky test: {test_name}
Generated by SelfHealer on {datetime.now().isoformat()}
"""
import pytest
from src.agent.self_healer import SelfHealer
from src.utils.logger import logger


@pytest.mark.flaky
@pytest.mark.agent_generated
def test_healed_{test_name.replace("test_", "")}(page, login_page, request):
    """Self-healed version of {test_name}"""
    healer = SelfHealer()
    _heal_records = {json.dumps([r.to_dict() for r in records], indent=2)}

    logger.info(f"Running self-healed version of {test_name}")
    logger.info(f"Heal records: {{_heal_records}}")

    try:
        login_page.navigate()
        login_page.complete_login()
        assert "/shop" in page.url or "angularpractice" in page.url
        logger.info(f"Self-healed test passed for {{test_name}}")
    except Exception as e:
        logger.error(f"Self-healed test also failed: {{e}}")
        raise
'''
        return code

    def analyze_failure(self, test_name: str, error_msg: str, page_source: str | None = None) -> dict[str, Any]:
        analysis = {
            "test_name": test_name,
            "error": error_msg,
            "possible_selectors": [],
            "heal_suggestions": [],
            "is_flaky": self.is_flaky(test_name),
        }

        if not page_source:
            return analysis

        selector_patterns = [
            (r"locator\(['\"]([^'\"]+)['\"]\)", "Playwright locator"),
            (r"page\.query_selector\(['\"]([^'\"]+)['\"]\)", "query_selector"),
            (r"click\(['\"]([^'\"]+)['\"]\)", "click selector"),
        ]

        for pattern, label in selector_patterns:
            for match in re.finditer(pattern, error_msg):
                analysis["possible_selectors"].append(match.group(1))

        error_lower = error_msg.lower()
        text_hints = re.findall(r"'([^']+)'", error_msg)
        for hint in text_hints:
            if len(hint) > 3 and hint not in ("True", "False", "None"):
                alt = self.find_alternative_selector(page_source, hint)
                if alt:
                    analysis["heal_suggestions"].append(alt)

        return analysis


healer = SelfHealer()
