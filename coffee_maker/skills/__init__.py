"""Coffee Maker Skills Module.

Central registry and loader for Claude skills.

Author: code_developer (implementing PRIORITY 26)
Date: 2025-10-23
"""

__version__ = "1.0.0"

from coffee_maker.skills.registry import SkillRegistry, get_skill

__all__ = ["SkillRegistry", "get_skill"]
