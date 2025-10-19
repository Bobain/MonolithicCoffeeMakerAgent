"""Configuration for Acceleration Dashboard."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DashboardConfig:
    """Configuration for the acceleration dashboard."""

    page_title: str = "Development Acceleration Insights"
    page_icon: str = "🚀"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"

    # Data sources
    project_root: Path = Path(__file__).parent.parent.parent
    roadmap_path: Path = project_root / "docs" / "roadmap" / "ROADMAP.md"
    git_repo_path: Path = project_root
    langfuse_db_path: Path = project_root / "llm_metrics.db"
    orchestrator_db_path: Path = project_root / ".claude" / "agents" / "data" / "orchestrator.db"
    notification_db_path: Path = project_root / "notifications.db"

    # Refresh intervals
    auto_refresh_seconds: int = 30
    curator_refresh_seconds: int = 300  # 5 minutes

    # Cache TTL
    cache_ttl: int = 60  # 1 minute

    def validate(self) -> None:
        """Validate configuration paths exist."""
        if not self.roadmap_path.exists():
            raise FileNotFoundError(f"ROADMAP not found: {self.roadmap_path}")
        if not self.git_repo_path.exists():
            raise FileNotFoundError(f"Git repo not found: {self.git_repo_path}")


def get_config() -> DashboardConfig:
    """Get dashboard configuration."""
    return DashboardConfig()
