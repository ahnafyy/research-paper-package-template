from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when a project contract is missing or invalid."""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigurationError(f"Required file does not exist: {path}")
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ConfigurationError(f"Expected a YAML mapping in {path}")
    return value


def _require_string(mapping: dict[str, Any], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{context}.{key} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class ProjectConfig:
    title: str
    slug: str
    initialized: bool
    random_seed: int

    @classmethod
    def from_file(cls, path: Path) -> ProjectConfig:
        raw = load_yaml(path)
        if raw.get("schema_version") != 1:
            raise ConfigurationError("project.yml schema_version must be 1")
        project = raw.get("project")
        research = raw.get("research")
        if not isinstance(project, dict) or not isinstance(research, dict):
            raise ConfigurationError("project.yml requires project and research mappings")
        random_seed = research.get("random_seed")
        if not isinstance(random_seed, int) or isinstance(random_seed, bool):
            raise ConfigurationError("research.random_seed must be an integer")
        return cls(
            title=_require_string(project, "title", "project"),
            slug=_require_string(project, "slug", "project"),
            initialized=raw.get("initialized") is True,
            random_seed=random_seed,
        )


def contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        upper = value.upper()
        return "TODO" in upper or "OWNER/REPOSITORY" in upper
    if isinstance(value, dict):
        return any(contains_placeholder(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_placeholder(item) for item in value)
    return False
