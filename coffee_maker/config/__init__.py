"""Configuration management for Coffee Maker Agent.

This package provides centralized configuration management for:
- API keys (Anthropic, OpenAI, Gemini, GitHub)
- Environment variable validation
- Configuration defaults and schemas

Main entry points:
- ConfigManager: Centralized configuration access
"""

from coffee_maker.config.manager import ConfigManager

__all__ = ["ConfigManager"]
