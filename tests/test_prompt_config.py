import unittest
from pathlib import Path

from src.prompt_config import PromptConfig


class PromptConfigTests(unittest.TestCase):
    def test_render_main_prompt(self) -> None:
        root = Path(__file__).resolve().parent.parent
        cfg = PromptConfig(root)
        text = cfg.render_prompt(
            "main_system",
            {
                "long_term_path": "/memories/MEMORY.md",
                "today_path": "/memories/daily/2026-02-12.md",
                "yesterday_path": "/memories/daily/2026-02-11.md",
            },
        )
        self.assertIn("代理人万能销售助手", text)
        self.assertIn("INDENTITY", cfg._config["prompts"]["main_system"]["files"][1])
        self.assertIn("/memories/daily/2026-02-11.md", text)

    def test_model_name_default(self) -> None:
        root = Path(__file__).resolve().parent.parent
        cfg = PromptConfig(root)
        name = cfg.get_model_name("memory_agent")
        self.assertTrue(isinstance(name, str) and len(name) > 0)


if __name__ == "__main__":
    unittest.main()
