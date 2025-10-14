"""Configuration for ACE framework.

This module provides configuration management for the ACE framework components.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from coffee_maker.utils.file_io import read_json_file


@dataclass
class ACEConfig:
    """ACE framework configuration."""

    enabled: bool = False
    trace_dir: Path = Path("docs/generator/traces")
    delta_dir: Path = Path("docs/reflector/deltas")
    playbook_dir: Path = Path("docs/curator/playbooks")
    auto_reflect: bool = False
    auto_curate: bool = False
    reflect_batch_size: int = 5
    similarity_threshold: float = 0.85
    pruning_rate: float = 0.10
    min_helpful_count: int = 2
    max_bullets: int = 150
    embedding_model: str = "text-embedding-ada-002"

    @classmethod
    def from_env(cls) -> "ACEConfig":
        """Load config from environment variables.

        Environment variables:
            ACE_ENABLED: Enable ACE framework (default: false)
            ACE_TRACE_DIR: Directory for execution traces
            ACE_DELTA_DIR: Directory for delta items
            ACE_PLAYBOOK_DIR: Directory for playbooks
            ACE_AUTO_REFLECT: Automatically run reflector (default: false)
            ACE_AUTO_CURATE: Automatically run curator (default: false)
            ACE_REFLECT_BATCH_SIZE: Batch size for reflection (default: 5)
            ACE_SIMILARITY_THRESHOLD: Semantic similarity threshold (default: 0.85)
            ACE_PRUNING_RATE: Percentage of bullets to prune (default: 0.10)
            ACE_MIN_HELPFUL_COUNT: Minimum helpful count to avoid pruning (default: 2)
            ACE_MAX_BULLETS: Maximum playbook size (default: 150)
            ACE_EMBEDDING_MODEL: Embedding model (default: text-embedding-ada-002)

        Returns:
            ACEConfig instance with values from environment
        """
        return cls(
            enabled=os.getenv("ACE_ENABLED", "false").lower() == "true",
            trace_dir=Path(os.getenv("ACE_TRACE_DIR", "docs/generator/traces")),
            delta_dir=Path(os.getenv("ACE_DELTA_DIR", "docs/reflector/deltas")),
            playbook_dir=Path(os.getenv("ACE_PLAYBOOK_DIR", "docs/curator/playbooks")),
            auto_reflect=os.getenv("ACE_AUTO_REFLECT", "false").lower() == "true",
            auto_curate=os.getenv("ACE_AUTO_CURATE", "false").lower() == "true",
            reflect_batch_size=int(os.getenv("ACE_REFLECT_BATCH_SIZE", "5")),
            similarity_threshold=float(os.getenv("ACE_SIMILARITY_THRESHOLD", "0.85")),
            pruning_rate=float(os.getenv("ACE_PRUNING_RATE", "0.10")),
            min_helpful_count=int(os.getenv("ACE_MIN_HELPFUL_COUNT", "2")),
            max_bullets=int(os.getenv("ACE_MAX_BULLETS", "150")),
            embedding_model=os.getenv("ACE_EMBEDDING_MODEL", "text-embedding-ada-002"),
        )

    @classmethod
    def from_file(cls, path: Path) -> "ACEConfig":
        """Load config from JSON file.

        Args:
            path: Path to JSON configuration file

        Returns:
            ACEConfig instance with values from file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is malformed
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        data = read_json_file(path)

        return cls(
            enabled=data.get("enabled", False),
            trace_dir=Path(data.get("trace_dir", "docs/generator/traces")),
            delta_dir=Path(data.get("delta_dir", "docs/reflector/deltas")),
            playbook_dir=Path(data.get("playbook_dir", "docs/curator/playbooks")),
            auto_reflect=data.get("auto_reflect", False),
            auto_curate=data.get("auto_curate", False),
            reflect_batch_size=data.get("reflect_batch_size", 5),
            similarity_threshold=data.get("similarity_threshold", 0.85),
            pruning_rate=data.get("pruning_rate", 0.10),
            min_helpful_count=data.get("min_helpful_count", 2),
            max_bullets=data.get("max_bullets", 150),
            embedding_model=data.get("embedding_model", "text-embedding-ada-002"),
        )

    def ensure_directories(self):
        """Create all necessary directories if they don't exist."""
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.delta_dir.mkdir(parents=True, exist_ok=True)
        self.playbook_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config
        """
        return {
            "enabled": self.enabled,
            "trace_dir": str(self.trace_dir),
            "delta_dir": str(self.delta_dir),
            "playbook_dir": str(self.playbook_dir),
            "auto_reflect": self.auto_reflect,
            "auto_curate": self.auto_curate,
            "reflect_batch_size": self.reflect_batch_size,
            "similarity_threshold": self.similarity_threshold,
            "pruning_rate": self.pruning_rate,
            "min_helpful_count": self.min_helpful_count,
            "max_bullets": self.max_bullets,
            "embedding_model": self.embedding_model,
        }


def get_default_config() -> ACEConfig:
    """Get default ACE configuration.

    First tries to load from .claude/ace_config.json, then environment variables,
    finally falls back to defaults.

    Returns:
        ACEConfig instance
    """
    config_path = Path(".claude/ace_config.json")

    if config_path.exists():
        try:
            return ACEConfig.from_file(config_path)
        except Exception:
            # Fall through to environment variables
            pass

    return ACEConfig.from_env()
