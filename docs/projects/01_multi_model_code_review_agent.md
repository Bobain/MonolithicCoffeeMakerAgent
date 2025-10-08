# Projet 1: Multi-Model Code Review Agent

## 🎯 Vue d'ensemble

### Résumé
Un agent de code review intelligent qui utilise **plusieurs LLMs simultanément** pour obtenir des perspectives complémentaires, puis synthétise leurs retours en un rapport unifié de haute qualité.

### Objectifs
- Obtenir des reviews de code multi-perspectives (bugs, architecture, performance, sécurité)
- Comparer les forces/faiblesses de différents LLMs
- Générer des rapports HTML interactifs
- Intégration Git hooks pour automatisation
- Mesurer la qualité et le coût des reviews

### Bénéfices
- **Qualité supérieure** - Capture des issues que chaque modèle trouve mieux
- **Consensus & divergences** - Identifie les problèmes critiques (tous modèles d'accord)
- **Apprentissage** - Comprendre les forces de chaque modèle
- **ROI mesurable** - Coût vs bugs prévenus

---

## 🏗️ Architecture

### Structure du module

```
coffee_maker/code_review/
├── __init__.py
├── multi_model_reviewer.py       # Agent principal
├── perspectives/
│   ├── __init__.py
│   ├── bug_hunter.py              # Détection de bugs
│   ├── architecture_critic.py     # Analyse architecture
│   ├── performance_analyst.py     # Analyse performance
│   └── security_auditor.py        # Audit sécurité
├── synthesis/
│   ├── __init__.py
│   ├── report_synthesizer.py     # Synthèse des reviews
│   └── consensus_analyzer.py     # Analyse consensus
├── reporters/
│   ├── __init__.py
│   ├── html_reporter.py           # Rapport HTML
│   ├── json_reporter.py           # Rapport JSON
│   └── cli_reporter.py            # Affichage CLI
└── integrations/
    ├── __init__.py
    ├── git_hooks.py               # Intégration Git
    └── github_actions.py          # GitHub Actions

scripts/
├── review_code.py                 # CLI principal
└── install_hooks.py               # Installation Git hooks

tests/
├── unit/test_multi_model_reviewer.py
├── integration/test_full_review.py
└── fixtures/
    └── sample_code/               # Code de test
```

### Diagramme de flux

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input: Code File                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │  MultiModelCodeReviewer.review()  │
         └───────────────┬───────────────────┘
                         │
                         ├──────┬──────┬──────┬──────┐
                         ▼      ▼      ▼      ▼      ▼
                      ┌────┐┌────┐┌────┐┌────┐┌────┐
                      │Bug ││Arch││Perf││Sec ││Qual│
                      │Hunt││Crit││Anal││Audi││Chec│
                      └──┬─┘└──┬─┘└──┬─┘└──┬─┘└──┬─┘
                         │     │     │     │     │
                    (GPT-4) (Claude)(Gemini)(GPT)(Claude)
                         │     │     │     │     │
                         └──┬──┴──┬──┴──┬──┴──┬──┘
                            ▼     ▼     ▼     ▼
                    ┌────────────────────────────────┐
                    │   Parallel Review Execution    │
                    │   (async/await, asyncio.gather)│
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │   Consensus Analyzer           │
                    │   - Issues trouvés par tous    │
                    │   - Issues uniques par modèle  │
                    │   - Conflits/divergences       │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │   Report Synthesizer           │
                    │   - Agrégation                 │
                    │   - Priorisation               │
                    │   - Déduplication              │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │   Multi-Format Output          │
                    │   - HTML (interactive)         │
                    │   - JSON (machine-readable)    │
                    │   - CLI (terminal-friendly)    │
                    └────────────────────────────────┘
```

---

## 📦 Composants Détaillés

### 1. MultiModelCodeReviewer (Core)

**Fichier**: `coffee_maker/code_review/multi_model_reviewer.py`

```python
"""Multi-model code review orchestrator."""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from coffee_maker.langchain_observe.builder import LLMBuilder
from coffee_maker.code_review.perspectives import (
    BugHunter,
    ArchitectureCritic,
    PerformanceAnalyst,
    SecurityAuditor,
)
from coffee_maker.code_review.synthesis import ReportSynthesizer, ConsensusAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ReviewIssue:
    """Single review issue found by a model."""

    severity: str  # critical, high, medium, low, info
    category: str  # bug, architecture, performance, security, style
    line_number: Optional[int]
    line_range: Optional[tuple]  # (start, end)
    title: str
    description: str
    suggestion: Optional[str]
    found_by_model: str  # Which model found this
    confidence: float  # 0.0-1.0


@dataclass
class ModelReview:
    """Complete review from one model."""

    model_name: str
    perspective: str  # bug_hunting, architecture, performance, security
    issues: List[ReviewIssue]
    summary: str
    execution_time: float
    cost_usd: float
    tokens_used: int


@dataclass
class CodeReviewReport:
    """Complete multi-model review report."""

    file_path: Path
    language: str
    total_lines: int

    # Individual model reviews
    model_reviews: List[ModelReview]

    # Aggregated results
    consensus_issues: List[ReviewIssue]  # Found by multiple models
    unique_issues: Dict[str, List[ReviewIssue]]  # Unique to each model
    all_issues: List[ReviewIssue]  # All issues sorted by severity

    # Statistics
    total_issues: int
    critical_issues: int
    models_used: List[str]
    total_cost_usd: float
    total_time_seconds: float

    # Model comparison
    model_agreement_rate: float  # 0.0-1.0
    most_effective_model: str

    # Metadata
    review_timestamp: str
    git_commit_hash: Optional[str]


class MultiModelCodeReviewer:
    """Multi-model code review orchestrator.

    This class coordinates multiple LLM-based code reviewers, each with
    a different perspective, to provide comprehensive code review.

    Example:
        >>> reviewer = MultiModelCodeReviewer()
        >>> report = await reviewer.review_file("my_code.py")
        >>> report.to_html("review_report.html")
    """

    def __init__(
        self,
        enable_perspectives: List[str] = None,
        cost_calculator = None,
        langfuse_client = None,
    ):
        """Initialize multi-model reviewer.

        Args:
            enable_perspectives: List of perspectives to enable
                ["bug_hunting", "architecture", "performance", "security"]
                Default: all enabled
            cost_calculator: Optional cost calculator
            langfuse_client: Optional Langfuse client for tracking
        """
        if enable_perspectives is None:
            enable_perspectives = [
                "bug_hunting",
                "architecture",
                "performance",
                "security"
            ]

        self.enable_perspectives = enable_perspectives
        self.cost_calculator = cost_calculator
        self.langfuse_client = langfuse_client

        # Initialize perspective agents
        self.perspectives = {}

        if "bug_hunting" in enable_perspectives:
            self.perspectives["bug_hunting"] = BugHunter(
                llm=self._build_llm("openai", "gpt-4o"),
            )

        if "architecture" in enable_perspectives:
            self.perspectives["architecture"] = ArchitectureCritic(
                llm=self._build_llm("anthropic", "claude-3-5-sonnet-20241022"),
            )

        if "performance" in enable_perspectives:
            self.perspectives["performance"] = PerformanceAnalyst(
                llm=self._build_llm("gemini", "gemini-2.0-flash-exp"),
            )

        if "security" in enable_perspectives:
            self.perspectives["security"] = SecurityAuditor(
                llm=self._build_llm("openai", "gpt-4o"),
            )

        # Synthesis components
        self.consensus_analyzer = ConsensusAnalyzer()
        self.synthesizer = ReportSynthesizer()

        logger.info(f"Initialized MultiModelCodeReviewer with perspectives: {enable_perspectives}")

    def _build_llm(self, provider: str, model: str):
        """Build LLM with AutoPickerLLM infrastructure."""
        builder = LLMBuilder()
        return (
            builder
            .with_primary(provider, model)
            .with_fallback("gemini", "gemini-2.5-flash")
            .with_cost_tracking(self.cost_calculator, self.langfuse_client)
            .with_context_fallback(True)
            .build()
        )

    async def review_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        git_context: bool = True,
    ) -> CodeReviewReport:
        """Review a single code file.

        Args:
            file_path: Path to code file
            language: Programming language (auto-detected if None)
            git_context: Include git context (diff, blame, etc.)

        Returns:
            Complete code review report
        """
        path = Path(file_path)

        # Read file
        code = path.read_text()

        # Detect language if not provided
        if language is None:
            language = self._detect_language(path)

        # Get git context if requested
        git_info = {}
        if git_context:
            git_info = self._get_git_context(path)

        # Run reviews in parallel
        logger.info(f"Starting parallel reviews for {file_path}")
        review_tasks = [
            self._run_perspective_review(name, agent, code, language, git_info)
            for name, agent in self.perspectives.items()
        ]

        model_reviews = await asyncio.gather(*review_tasks)

        # Analyze consensus
        consensus_issues = self.consensus_analyzer.find_consensus(model_reviews)
        unique_issues = self.consensus_analyzer.find_unique_issues(model_reviews)

        # Synthesize report
        report = self.synthesizer.create_report(
            file_path=path,
            language=language,
            code=code,
            model_reviews=model_reviews,
            consensus_issues=consensus_issues,
            unique_issues=unique_issues,
            git_context=git_info,
        )

        logger.info(
            f"Review complete: {report.total_issues} issues found, "
            f"${report.total_cost_usd:.4f} cost, "
            f"{report.total_time_seconds:.2f}s"
        )

        return report

    async def review_directory(
        self,
        directory: str,
        pattern: str = "**/*.py",
        max_files: int = 100,
    ) -> List[CodeReviewReport]:
        """Review all files in a directory.

        Args:
            directory: Directory to review
            pattern: Glob pattern for files
            max_files: Maximum files to review

        Returns:
            List of review reports
        """
        dir_path = Path(directory)
        files = list(dir_path.glob(pattern))[:max_files]

        logger.info(f"Reviewing {len(files)} files in {directory}")

        review_tasks = [
            self.review_file(str(file))
            for file in files
        ]

        reports = await asyncio.gather(*review_tasks)

        return reports

    async def _run_perspective_review(
        self,
        perspective_name: str,
        agent,
        code: str,
        language: str,
        git_info: dict,
    ) -> ModelReview:
        """Run a single perspective review."""
        import time

        start_time = time.time()

        try:
            issues = await agent.review(code, language, git_info)
            execution_time = time.time() - start_time

            # Get stats from agent
            stats = agent.get_stats()

            return ModelReview(
                model_name=agent.model_name,
                perspective=perspective_name,
                issues=issues,
                summary=agent.get_summary(),
                execution_time=execution_time,
                cost_usd=stats.get("cost_usd", 0.0),
                tokens_used=stats.get("total_tokens", 0),
            )

        except Exception as e:
            logger.error(f"Perspective {perspective_name} failed: {e}")
            execution_time = time.time() - start_time

            return ModelReview(
                model_name="error",
                perspective=perspective_name,
                issues=[],
                summary=f"Review failed: {e}",
                execution_time=execution_time,
                cost_usd=0.0,
                tokens_used=0,
            )

    def _detect_language(self, path: Path) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php",
        }
        return ext_map.get(path.suffix, "unknown")

    def _get_git_context(self, path: Path) -> dict:
        """Get git context for file."""
        try:
            import git

            repo = git.Repo(path, search_parent_directories=True)

            # Get recent commits for file
            commits = list(repo.iter_commits(paths=str(path), max_count=5))

            # Get current diff
            diff = repo.git.diff(str(path))

            # Get blame info
            blame = repo.git.blame(str(path))

            return {
                "commit_hash": repo.head.commit.hexsha,
                "branch": repo.active_branch.name,
                "recent_commits": [
                    {
                        "hash": c.hexsha[:7],
                        "message": c.message.strip(),
                        "author": c.author.name,
                        "date": c.committed_datetime.isoformat(),
                    }
                    for c in commits
                ],
                "diff": diff,
                "blame": blame,
            }

        except Exception as e:
            logger.warning(f"Could not get git context: {e}")
            return {}
```

---

### 2. Perspective Agents

#### BugHunter

**Fichier**: `coffee_maker/code_review/perspectives/bug_hunter.py`

```python
"""Bug hunting perspective agent."""

import logging
from typing import List, Optional

from coffee_maker.code_review.multi_model_reviewer import ReviewIssue

logger = logging.getLogger(__name__)


class BugHunter:
    """Specialized agent for finding bugs and logic errors.

    This agent focuses on:
    - Logic errors and edge cases
    - Null/None dereferences
    - Off-by-one errors
    - Race conditions
    - Exception handling issues
    - Type errors
    """

    SYSTEM_PROMPT = """You are an expert code reviewer specialized in finding bugs.

Your focus areas:
1. Logic Errors: Incorrect conditions, wrong operators, edge cases
2. Null Safety: Potential null/None dereferences, uninitialized variables
3. Boundary Conditions: Off-by-one errors, array/list bounds
4. Concurrency: Race conditions, deadlocks, thread safety
5. Error Handling: Missing try-catch, incorrect exception handling
6. Type Issues: Type mismatches, implicit conversions

For each issue found:
- Specify exact line number(s)
- Explain the bug clearly
- Provide a fix suggestion
- Rate severity: critical, high, medium, low, info
- Rate your confidence: 0.0-1.0

Output JSON format:
{
  "issues": [
    {
      "line_number": 42,
      "severity": "critical",
      "confidence": 0.95,
      "title": "Potential None dereference",
      "description": "Variable 'user' may be None when accessed on line 42",
      "suggestion": "Add None check: if user is not None: ..."
    }
  ],
  "summary": "Found 3 critical issues, 2 high priority..."
}
"""

    def __init__(self, llm):
        """Initialize bug hunter.

        Args:
            llm: LLM instance (AutoPickerLLM)
        """
        self.llm = llm
        self.model_name = getattr(llm, 'primary_model_name', 'unknown')
        self._stats = {"cost_usd": 0.0, "total_tokens": 0}

    async def review(
        self,
        code: str,
        language: str,
        git_info: dict,
    ) -> List[ReviewIssue]:
        """Review code for bugs.

        Args:
            code: Source code to review
            language: Programming language
            git_info: Git context information

        Returns:
            List of review issues
        """
        # Build prompt
        prompt = self._build_prompt(code, language, git_info)

        # Invoke LLM
        try:
            response = await self.llm.ainvoke({"input": prompt})

            # Update stats
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                self._stats["total_tokens"] = getattr(usage, "total_tokens", 0)

            # Parse response
            issues = self._parse_response(response.content)

            return issues

        except Exception as e:
            logger.error(f"Bug hunting failed: {e}")
            return []

    def _build_prompt(self, code: str, language: str, git_info: dict) -> str:
        """Build review prompt."""
        prompt = f"{self.SYSTEM_PROMPT}\n\n"
        prompt += f"Language: {language}\n\n"
        prompt += f"Code to review:\n```{language}\n{code}\n```\n\n"

        if git_info.get("recent_commits"):
            prompt += "Recent commits:\n"
            for commit in git_info["recent_commits"][:3]:
                prompt += f"- {commit['hash']}: {commit['message']}\n"
            prompt += "\n"

        prompt += "Please review this code for bugs and provide your analysis in JSON format."

        return prompt

    def _parse_response(self, response: str) -> List[ReviewIssue]:
        """Parse LLM response into review issues."""
        import json
        import re

        # Extract JSON from markdown code block if present
        json_match = re.search(r'```json\n(.+?)\n```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        try:
            data = json.loads(json_str)

            issues = []
            for issue_data in data.get("issues", []):
                issue = ReviewIssue(
                    severity=issue_data.get("severity", "medium"),
                    category="bug",
                    line_number=issue_data.get("line_number"),
                    line_range=None,
                    title=issue_data.get("title", ""),
                    description=issue_data.get("description", ""),
                    suggestion=issue_data.get("suggestion"),
                    found_by_model=self.model_name,
                    confidence=issue_data.get("confidence", 0.8),
                )
                issues.append(issue)

            self._summary = data.get("summary", "")

            return issues

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse bug hunter response: {e}")
            return []

    def get_summary(self) -> str:
        """Get review summary."""
        return getattr(self, '_summary', "No summary available")

    def get_stats(self) -> dict:
        """Get execution statistics."""
        return self._stats
```

#### ArchitectureCritic

**Fichier**: `coffee_maker/code_review/perspectives/architecture_critic.py`

```python
"""Architecture critique perspective agent."""

import logging
from typing import List

from coffee_maker.code_review.multi_model_reviewer import ReviewIssue

logger = logging.getLogger(__name__)


class ArchitectureCritic:
    """Specialized agent for architecture and design review.

    Focus areas:
    - Code structure and organization
    - Design patterns usage
    - Coupling and cohesion
    - Separation of concerns
    - SOLID principles
    - Code duplication
    - Modularity
    """

    SYSTEM_PROMPT = """You are a senior software architect reviewing code structure and design.

Your focus areas:
1. Structure: Code organization, module boundaries, file structure
2. Design Patterns: Appropriate use of patterns, anti-patterns
3. Coupling: Tight coupling issues, dependency injection opportunities
4. Cohesion: Single responsibility, separation of concerns
5. SOLID Principles: Violations and improvements
6. DRY: Code duplication, opportunities for abstraction
7. Maintainability: Code that's hard to maintain or extend

For each issue:
- Specify affected lines/sections
- Explain the architectural concern
- Suggest refactoring approach
- Rate severity: critical, high, medium, low, info
- Rate confidence: 0.0-1.0

Output JSON format:
{
  "issues": [
    {
      "line_range": [10, 50],
      "severity": "medium",
      "confidence": 0.85,
      "title": "High coupling between modules",
      "description": "Class directly instantiates dependencies...",
      "suggestion": "Use dependency injection pattern..."
    }
  ],
  "summary": "Overall structure is good but..."
}
"""

    def __init__(self, llm):
        self.llm = llm
        self.model_name = getattr(llm, 'primary_model_name', 'unknown')
        self._stats = {"cost_usd": 0.0, "total_tokens": 0}

    async def review(self, code: str, language: str, git_info: dict) -> List[ReviewIssue]:
        """Review code architecture."""
        prompt = self._build_prompt(code, language, git_info)

        try:
            response = await self.llm.ainvoke({"input": prompt})

            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                self._stats["total_tokens"] = getattr(usage, "total_tokens", 0)

            issues = self._parse_response(response.content)
            return issues

        except Exception as e:
            logger.error(f"Architecture review failed: {e}")
            return []

    def _build_prompt(self, code: str, language: str, git_info: dict) -> str:
        prompt = f"{self.SYSTEM_PROMPT}\n\n"
        prompt += f"Language: {language}\n\n"
        prompt += f"Code to review:\n```{language}\n{code}\n```\n\n"
        prompt += "Analyze the architecture and design. Provide JSON response."
        return prompt

    def _parse_response(self, response: str) -> List[ReviewIssue]:
        import json
        import re

        json_match = re.search(r'```json\n(.+?)\n```', response, re.DOTALL)
        json_str = json_match.group(1) if json_match else response

        try:
            data = json.loads(json_str)
            issues = []

            for issue_data in data.get("issues", []):
                line_range = issue_data.get("line_range")
                issue = ReviewIssue(
                    severity=issue_data.get("severity", "medium"),
                    category="architecture",
                    line_number=line_range[0] if line_range else None,
                    line_range=tuple(line_range) if line_range else None,
                    title=issue_data.get("title", ""),
                    description=issue_data.get("description", ""),
                    suggestion=issue_data.get("suggestion"),
                    found_by_model=self.model_name,
                    confidence=issue_data.get("confidence", 0.8),
                )
                issues.append(issue)

            self._summary = data.get("summary", "")
            return issues

        except json.JSONDecodeError:
            return []

    def get_summary(self) -> str:
        return getattr(self, '_summary', "")

    def get_stats(self) -> dict:
        return self._stats
```

---

### 3. Report Generation

**Fichier**: `coffee_maker/code_review/reporters/html_reporter.py`

```python
"""HTML report generator for code reviews."""

from pathlib import Path
from typing import List
from datetime import datetime

from coffee_maker.code_review.multi_model_reviewer import CodeReviewReport, ReviewIssue


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review: {file_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 6px; margin-bottom: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
        .summary-card {{ background: white; padding: 15px; border-radius: 6px; text-align: center; }}
        .summary-card .number {{ font-size: 32px; font-weight: bold; color: #3498db; }}
        .summary-card .label {{ color: #7f8c8d; font-size: 12px; text-transform: uppercase; }}

        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #2c3e50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #3498db; }}

        .issue {{ background: #fff; border-left: 4px solid; padding: 15px; margin-bottom: 15px; border-radius: 4px; }}
        .issue.critical {{ border-color: #e74c3c; background: #fff5f5; }}
        .issue.high {{ border-color: #e67e22; background: #fff8f0; }}
        .issue.medium {{ border-color: #f39c12; background: #fffaf0; }}
        .issue.low {{ border-color: #3498db; background: #f0f8ff; }}
        .issue.info {{ border-color: #95a5a6; background: #f8f9fa; }}

        .issue-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }}
        .issue-title {{ font-weight: bold; font-size: 16px; color: #2c3e50; }}
        .issue-badges {{ display: flex; gap: 8px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
        .badge.critical {{ background: #e74c3c; color: white; }}
        .badge.high {{ background: #e67e22; color: white; }}
        .badge.medium {{ background: #f39c12; color: white; }}
        .badge.low {{ background: #3498db; color: white; }}
        .badge.info {{ background: #95a5a6; color: white; }}
        .badge.model {{ background: #9b59b6; color: white; }}

        .issue-line {{ color: #7f8c8d; font-size: 13px; margin-bottom: 8px; }}
        .issue-description {{ margin-bottom: 10px; color: #555; }}
        .issue-suggestion {{ background: #e8f5e9; padding: 10px; border-radius: 4px; border-left: 3px solid #4caf50; }}
        .issue-suggestion strong {{ color: #2e7d32; }}

        .model-comparison {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .model-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; }}
        .model-card h3 {{ color: #2c3e50; margin-bottom: 15px; }}
        .model-stat {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #dee2e6; }}
        .model-stat:last-child {{ border-bottom: none; }}

        .consensus {{ background: #fff3cd; border: 2px solid #ffc107; padding: 20px; border-radius: 6px; margin-bottom: 20px; }}
        .consensus h3 {{ color: #856404; margin-bottom: 15px; }}

        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #7f8c8d; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Multi-Model Code Review</h1>
        <div class="meta">
            File: <strong>{file_path}</strong> |
            Language: <strong>{language}</strong> |
            Reviewed: {timestamp} |
            Lines: {total_lines}
        </div>

        <div class="summary">
            <h3>📊 Summary</h3>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="number">{total_issues}</div>
                    <div class="label">Total Issues</div>
                </div>
                <div class="summary-card">
                    <div class="number" style="color: #e74c3c;">{critical_issues}</div>
                    <div class="label">Critical</div>
                </div>
                <div class="summary-card">
                    <div class="number">{models_count}</div>
                    <div class="label">Models Used</div>
                </div>
                <div class="summary-card">
                    <div class="number">${cost:.4f}</div>
                    <div class="label">Total Cost</div>
                </div>
                <div class="summary-card">
                    <div class="number">{time:.1f}s</div>
                    <div class="label">Review Time</div>
                </div>
                <div class="summary-card">
                    <div class="number">{agreement:.0f}%</div>
                    <div class="label">Agreement Rate</div>
                </div>
            </div>
        </div>

        {consensus_section}

        <div class="section">
            <h2>🐛 All Issues</h2>
            {all_issues_html}
        </div>

        <div class="section">
            <h2>📈 Model Comparison</h2>
            <div class="model-comparison">
                {model_comparison_html}
            </div>
        </div>

        <div class="footer">
            Generated by Coffee Maker Multi-Model Code Review Agent<br>
            Models: {models_list}
        </div>
    </div>
</body>
</html>
"""


class HTMLReporter:
    """Generate HTML reports for code reviews."""

    @staticmethod
    def generate(report: CodeReviewReport, output_path: str):
        """Generate HTML report.

        Args:
            report: Code review report
            output_path: Path to save HTML file
        """
        # Generate consensus section
        consensus_html = ""
        if report.consensus_issues:
            consensus_html = '<div class="consensus">'
            consensus_html += '<h3>⚠️ Consensus Issues (Found by Multiple Models)</h3>'
            consensus_html += '<p>These issues were identified by multiple models and should be addressed with high priority.</p>'
            for issue in report.consensus_issues:
                consensus_html += HTMLReporter._issue_to_html(issue)
            consensus_html += '</div>'

        # Generate all issues HTML
        all_issues_html = ""
        for issue in report.all_issues:
            all_issues_html += HTMLReporter._issue_to_html(issue)

        if not all_issues_html:
            all_issues_html = '<p style="color: #27ae60; font-weight: bold;">✅ No issues found! Code looks good.</p>'

        # Generate model comparison
        model_comparison_html = ""
        for model_review in report.model_reviews:
            model_comparison_html += f"""
            <div class="model-card">
                <h3>{model_review.model_name}</h3>
                <div class="model-stat">
                    <span>Perspective:</span>
                    <strong>{model_review.perspective}</strong>
                </div>
                <div class="model-stat">
                    <span>Issues Found:</span>
                    <strong>{len(model_review.issues)}</strong>
                </div>
                <div class="model-stat">
                    <span>Cost:</span>
                    <strong>${model_review.cost_usd:.4f}</strong>
                </div>
                <div class="model-stat">
                    <span>Time:</span>
                    <strong>{model_review.execution_time:.2f}s</strong>
                </div>
                <div class="model-stat">
                    <span>Tokens:</span>
                    <strong>{model_review.tokens_used:,}</strong>
                </div>
            </div>
            """

        # Fill template
        html = HTML_TEMPLATE.format(
            file_name=report.file_path.name,
            file_path=str(report.file_path),
            language=report.language,
            timestamp=report.review_timestamp,
            total_lines=report.total_lines,
            total_issues=report.total_issues,
            critical_issues=report.critical_issues,
            models_count=len(report.models_used),
            cost=report.total_cost_usd,
            time=report.total_time_seconds,
            agreement=report.model_agreement_rate * 100,
            consensus_section=consensus_html,
            all_issues_html=all_issues_html,
            model_comparison_html=model_comparison_html,
            models_list=", ".join(report.models_used),
        )

        # Write file
        Path(output_path).write_text(html, encoding='utf-8')

    @staticmethod
    def _issue_to_html(issue: ReviewIssue) -> str:
        """Convert issue to HTML."""
        line_info = f"Line {issue.line_number}" if issue.line_number else "Multiple lines"
        if issue.line_range:
            line_info = f"Lines {issue.line_range[0]}-{issue.line_range[1]}"

        suggestion_html = ""
        if issue.suggestion:
            suggestion_html = f"""
            <div class="issue-suggestion">
                <strong>💡 Suggestion:</strong> {issue.suggestion}
            </div>
            """

        return f"""
        <div class="issue {issue.severity}">
            <div class="issue-header">
                <div class="issue-title">{issue.title}</div>
                <div class="issue-badges">
                    <span class="badge {issue.severity}">{issue.severity}</span>
                    <span class="badge model">{issue.found_by_model}</span>
                </div>
            </div>
            <div class="issue-line">📍 {line_info} | Category: {issue.category} | Confidence: {issue.confidence:.0%}</div>
            <div class="issue-description">{issue.description}</div>
            {suggestion_html}
        </div>
        """
```

---

## 🚀 Guide d'Utilisation

### Installation

```bash
# Créer l'environnement
cd /path/to/MonolithicCoffeeMakerAgent
poetry install

# Installer le package en mode dev
poetry install --with dev
```

### Configuration

```bash
# Copier .env.example → .env
cp .env.example .env

# Éditer .env et ajouter vos clés API
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
```

### Utilisation CLI

```bash
# Review d'un fichier
poetry run python scripts/review_code.py my_code.py

# Avec options
poetry run python scripts/review_code.py my_code.py \
    --language python \
    --output report.html \
    --perspectives bug_hunting architecture performance

# Review d'un répertoire
poetry run python scripts/review_code.py src/ \
    --pattern "**/*.py" \
    --max-files 10

# Avec budget limité
poetry run python scripts/review_code.py my_code.py \
    --max-cost 0.10
```

### Utilisation Python

```python
import asyncio
from coffee_maker.code_review import MultiModelCodeReviewer
from coffee_maker.code_review.reporters import HTMLReporter

async def main():
    # Créer le reviewer
    reviewer = MultiModelCodeReviewer(
        enable_perspectives=["bug_hunting", "architecture", "performance"],
    )

    # Review un fichier
    report = await reviewer.review_file("my_code.py")

    # Afficher résumé
    print(f"Found {report.total_issues} issues")
    print(f"Cost: ${report.total_cost_usd:.4f}")

    # Générer rapport HTML
    HTMLReporter.generate(report, "review_report.html")

    # Accéder aux issues critiques
    critical = [i for i in report.all_issues if i.severity == "critical"]
    for issue in critical:
        print(f"⚠️  Line {issue.line_number}: {issue.title}")

asyncio.run(main())
```

### Intégration Git Hooks

```bash
# Installer les hooks
poetry run python scripts/install_hooks.py

# Configuration dans .git/hooks/pre-commit
#!/bin/bash
poetry run python scripts/review_code.py --git-staged --fail-on-critical
```

---

## 📊 Métriques et Analytics

### Métriques collectées

1. **Par Review**:
   - Nombre total d'issues
   - Issues par sévérité
   - Issues par catégorie
   - Coût total (USD)
   - Temps d'exécution
   - Tokens utilisés

2. **Par Modèle**:
   - Issues trouvées
   - Coût par review
   - Latence moyenne
   - Taux de faux positifs (avec feedback)

3. **Consensus**:
   - Taux d'accord entre modèles
   - Issues trouvées par plusieurs modèles
   - Issues uniques par modèle

### Stockage dans SQLite

```sql
CREATE TABLE code_review_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    language TEXT,
    review_timestamp TIMESTAMP,
    total_issues INTEGER,
    critical_issues INTEGER,
    total_cost_usd REAL,
    total_time_seconds REAL,
    models_used TEXT,  -- JSON array
    git_commit_hash TEXT
);

CREATE TABLE review_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER,
    severity TEXT,
    category TEXT,
    line_number INTEGER,
    title TEXT,
    description TEXT,
    found_by_model TEXT,
    confidence REAL,
    FOREIGN KEY (report_id) REFERENCES code_review_reports(id)
);
```

---

## 🧪 Tests

### Tests unitaires

```python
# tests/unit/test_multi_model_reviewer.py
import pytest
from coffee_maker.code_review import MultiModelCodeReviewer

@pytest.mark.asyncio
async def test_review_simple_code():
    """Test review of simple code."""
    reviewer = MultiModelCodeReviewer(
        enable_perspectives=["bug_hunting"],
    )

    code = """
def divide(a, b):
    return a / b  # Bug: no zero check
"""

    # Mock file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()

        report = await reviewer.review_file(f.name)

    # Assertions
    assert report.total_issues > 0
    assert any("zero" in i.description.lower() for i in report.all_issues)
```

### Tests d'intégration

```python
# tests/integration/test_full_review.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_review_pipeline():
    """Test complete review pipeline."""
    reviewer = MultiModelCodeReviewer()

    # Review real file
    report = await reviewer.review_file("coffee_maker/code_review/multi_model_reviewer.py")

    assert report.total_issues >= 0
    assert report.total_cost_usd > 0
    assert len(report.model_reviews) > 0

    # Generate HTML report
    HTMLReporter.generate(report, "/tmp/test_report.html")
    assert Path("/tmp/test_report.html").exists()
```

---

## 📈 Roadmap

### Phase 1: MVP (Semaine 1)
- [x] Architecture de base
- [x] BugHunter + ArchitectureCritic
- [x] Rapport HTML basique
- [ ] CLI fonctionnel
- [ ] Tests unitaires

### Phase 2: Features (Semaine 2)
- [ ] PerformanceAnalyst + SecurityAuditor
- [ ] Consensus analyzer
- [ ] Rapport HTML avancé (interactif)
- [ ] Export JSON

### Phase 3: Integration (Semaine 3)
- [ ] Git hooks
- [ ] GitHub Actions
- [ ] Configuration avancée
- [ ] Filtres personnalisés

### Phase 4: Analytics (Semaine 4)
- [ ] Stockage SQLite
- [ ] Dashboard web (Gradio)
- [ ] Métriques temporelles
- [ ] Comparaison modèles

### Phase 5: Polish (Semaine 5)
- [ ] Documentation complète
- [ ] Exemples avancés
- [ ] Performance optimizations
- [ ] Vidéo démo

---

## 🎓 Exemples Avancés

### Review avec contraintes de coût

```python
reviewer = MultiModelCodeReviewer()

# Limiter le coût
report = await reviewer.review_file(
    "large_file.py",
    max_cost_usd=0.05,  # Max $0.05
)

if report.total_cost_usd > 0.05:
    print("⚠️  Review stopped: budget exceeded")
```

### Review incrémental (diff only)

```python
# Review seulement les lignes modifiées
report = await reviewer.review_git_diff(
    commit_range="HEAD~1..HEAD",
    perspectives=["bug_hunting"],  # Review rapide
)
```

### Review en batch

```python
# Review multiple files avec budget global
reviewer = MultiModelCodeReviewer()

reports = await reviewer.review_directory(
    "src/",
    pattern="**/*.py",
    max_files=50,
    max_total_cost=1.00,  # Budget global
)

# Agrégation
total_issues = sum(r.total_issues for r in reports)
total_cost = sum(r.total_cost_usd for r in reports)

print(f"Reviewed {len(reports)} files: {total_issues} issues, ${total_cost:.2f}")
```

### Custom perspective

```python
from coffee_maker.code_review.perspectives.base import BasePerspective

class CustomSecurityAuditor(BasePerspective):
    """Custom security auditor with specific rules."""

    SYSTEM_PROMPT = """You are a security expert focusing on:
    - SQL injection
    - XSS vulnerabilities
    - Authentication issues
    ...
    """

    # Implementation...

# Use custom perspective
reviewer = MultiModelCodeReviewer()
reviewer.add_perspective("custom_security", CustomSecurityAuditor(...))
```

---

## 🔧 Configuration Avancée

### Fichier de config `.code_review.yaml`

```yaml
# .code_review.yaml
perspectives:
  bug_hunting:
    enabled: true
    model: openai/gpt-4o
    fallback: gemini/gemini-2.5-flash

  architecture:
    enabled: true
    model: anthropic/claude-3-5-sonnet-20241022
    fallback: openai/gpt-4o-mini

  performance:
    enabled: true
    model: gemini/gemini-2.0-flash-exp

  security:
    enabled: false  # Disabled

output:
  html: true
  json: true
  cli: true

  html_template: custom_template.html  # Optional

filters:
  min_severity: medium  # Ignore low/info
  min_confidence: 0.7   # Ignore low confidence

  exclude_categories:
    - style
    - formatting

budget:
  max_cost_per_file: 0.10
  max_cost_per_review: 1.00

  fallback_on_budget:
    - gemini/gemini-2.5-flash-lite

git:
  auto_commit_message: true
  fail_on_critical: true
  fail_on_high: false
```

---

## 🤝 Contributing

### Ajouter une nouvelle perspective

1. Créer `coffee_maker/code_review/perspectives/my_perspective.py`
2. Hériter de `BasePerspective`
3. Implémenter `review()` et `_parse_response()`
4. Enregistrer dans `MultiModelCodeReviewer`

### Ajouter un nouveau reporter

1. Créer `coffee_maker/code_review/reporters/my_reporter.py`
2. Implémenter `generate(report, output_path)`
3. Ajouter aux exports

---

## 📚 Références

- [AutoPickerLLM Documentation](../autopicker_llm_implementation.md)
- [LangChain Documentation](https://python.langchain.com/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)

---

## 📝 Changelog

### v0.1.0 (Planning)
- Initial documentation
- Architecture design
- Core components specification

### v0.2.0 (Target)
- MVP implementation
- Basic CLI
- HTML reports

### v1.0.0 (Target)
- Full feature set
- Git integration
- Production ready

---

**Status**: 📝 Documentation Complete - Ready for Implementation
**Estimated Development Time**: 2-3 weeks
**Priority**: ⭐⭐⭐⭐⭐ (Highest)
