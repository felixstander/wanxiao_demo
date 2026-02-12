from pathlib import Path
from typing import Any

import yaml


class PromptConfig:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.config_path = project_root / "config" / "prompts.yaml"
        self._config = self._load_yaml(self.config_path)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"prompt config not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("prompt config must be a mapping")
        return data

    def get_model_name(self, key: str) -> str:
        models = self._config.get("models", {})
        if not isinstance(models, dict) or key not in models:
            raise KeyError(f"model config '{key}' missing")

        item = models[key]
        if not isinstance(item, dict):
            raise ValueError(f"model config '{key}' must be a mapping")

        env_name = item.get("env")
        default = item.get("default")
        if not isinstance(env_name, str) or not isinstance(default, str):
            raise ValueError(f"model config '{key}' requires env/default")

        from os import getenv

        return getenv(env_name, default)

    def render_prompt(self, key: str, variables: dict[str, str] | None = None) -> str:
        prompts = self._config.get("prompts", {})
        if not isinstance(prompts, dict) or key not in prompts:
            raise KeyError(f"prompt '{key}' missing")

        item = prompts[key]
        if not isinstance(item, dict):
            raise ValueError(f"prompt '{key}' config must be a mapping")

        file_path = item.get("file")
        files = item.get("files")

        templates: list[str] = []
        if isinstance(file_path, str):
            templates.append((self.project_root / file_path).read_text(encoding="utf-8"))
        elif isinstance(files, list) and all(isinstance(x, str) for x in files):
            for p in files:
                templates.append((self.project_root / p).read_text(encoding="utf-8"))
        else:
            raise ValueError(f"prompt '{key}' requires file or files")

        template = "\n\n".join(s.strip() for s in templates if s.strip())
        if variables:
            return template.format(**variables)
        return template
