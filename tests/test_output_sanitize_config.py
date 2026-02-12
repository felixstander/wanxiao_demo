import unittest
from pathlib import Path

from src.output_sanitize_config import load_output_sanitize_config


class OutputSanitizeConfigTests(unittest.TestCase):
    def test_load_output_sanitize_config(self) -> None:
        root = Path(__file__).resolve().parent.parent
        cfg = load_output_sanitize_config(root / "config" / "output_sanitize.yaml")
        self.assertTrue(cfg.enabled)
        self.assertTrue(any("工作原则" in token for token in cfg.literals))
        self.assertGreaterEqual(len(cfg.regex_patterns), 1)


if __name__ == "__main__":
    unittest.main()
