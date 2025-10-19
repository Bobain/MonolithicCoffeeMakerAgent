"""
Architecture Skills Module

Provides architectural analysis and design assistance skills:
- architecture_reuse_checker: Detect pattern reuse opportunities
"""

from coffee_maker.skills.architecture.architecture_reuse_checker import (
    ArchitecturalComponent,
    ArchitectureReuseChecker,
    ReuseAnalysisResult,
    ReuseOpportunity,
    check_architecture_reuse,
)

__all__ = [
    "ArchitecturalComponent",
    "ArchitectureReuseChecker",
    "ReuseAnalysisResult",
    "ReuseOpportunity",
    "check_architecture_reuse",
]
