from dataclasses import dataclass
from pathlib import Path
from typing import Pattern
import re

import yaml


@dataclass
class OutputSanitizeConfig:
    enabled: bool
    literals: list[str]
    regex_patterns: list[Pattern[str]]


def load_output_sanitize_config(path: Path) -> OutputSanitizeConfig:
    if not path.exists():
        return OutputSanitizeConfig(enabled=True, literals=[], regex_patterns=[])

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("output sanitize config must be a mapping")

    enabled = bool(data.get("enabled", True))

    raw_literals = data.get("literals", [])
    literals = [x for x in raw_literals if isinstance(x, str) and x.strip()]

    raw_regex = data.get("regex", [])
    regex_patterns: list[Pattern[str]] = []
    for pattern in raw_regex:
        if isinstance(pattern, str) and pattern.strip():
            regex_patterns.append(re.compile(pattern))

    return OutputSanitizeConfig(
        enabled=enabled,
        literals=literals,
        regex_patterns=regex_patterns,
    )
