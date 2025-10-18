"""
Code Analysis Skills

5 high-performance skills for deep codebase analysis:
- code_forensics: Pattern detection, complexity analysis, duplication
- security_audit: Vulnerability scanning, dependency analysis
- dependency_tracer: Dependency relationships, impact analysis
- functional_search: Find code by functional area (uses code index)
- code_explainer: Explain code in accessible terms

All skills execute in <200ms for fast, deterministic results.
"""

from coffee_maker.skills.code_analysis.code_explainer import CodeExplainer
from coffee_maker.skills.code_analysis.code_forensics import CodeForensics
from coffee_maker.skills.code_analysis.dependency_tracer import DependencyTracer
from coffee_maker.skills.code_analysis.functional_search import FunctionalSearch
from coffee_maker.skills.code_analysis.security_audit import SecurityAudit

__all__ = [
    "CodeForensics",
    "SecurityAudit",
    "DependencyTracer",
    "FunctionalSearch",
    "CodeExplainer",
]
