# Projet 5: LLM Performance Profiler

## 🎯 Vue d'ensemble

Un outil de **profiling automatisé** qui mesure finement les performances des LLMs sur différentes dimensions et génère des rapports comparatifs détaillés.

### Objectifs
- Benchmark automatisé et reproductible
- Métriques multi-dimensionnelles (latence, qualité, coût, token efficiency)
- Rapports HTML interactifs
- Stress testing et context window testing
- Export vers SQLite pour analytics

---

## 🏗️ Architecture

```
coffee_maker/llm_profiler/
├── __init__.py
├── profiler.py                  # Profiler principal
├── benchmarks/
│   ├── base_benchmark.py        # Benchmark de base
│   ├── code_gen_benchmark.py    # Code generation
│   ├── summarization_benchmark.py
│   ├── translation_benchmark.py
│   └── math_reasoning_benchmark.py
├── metrics/
│   ├── latency_meter.py         # Mesure latence
│   ├── quality_evaluator.py     # Évaluation qualité
│   ├── token_counter.py         # Comptage tokens
│   └── cost_calculator.py       # Calcul coûts
├── testing/
│   ├── stress_tester.py         # Stress tests
│   └── context_tester.py        # Context window tests
└── reporting/
    ├── html_reporter.py         # Rapports HTML
    ├── json_exporter.py         # Export JSON
    └── comparison_generator.py  # Comparaisons
```

---

## 📦 Composants Clés

### 1. LLMProfiler (Core)

```python
"""LLM Performance Profiler."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class ProfileReport:
    """Performance profile report."""
    provider: str
    model: str
    timestamp: str

    # Latency metrics
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_mean: float

    # Quality metrics
    quality_score: float  # 0.0-1.0
    quality_std: float

    # Cost metrics
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float
    avg_cost_per_request: float

    # Token efficiency
    avg_input_tokens: int
    avg_output_tokens: int
    output_input_ratio: float

    # Reliability
    success_rate: float
    error_rate: float
    error_types: Dict[str, int]

    # Throughput
    requests_per_second: float

    # Raw data
    raw_results: List[Dict]


class LLMProfiler:
    """Comprehensive LLM performance profiler.

    Features:
    - Automated benchmarking
    - Multi-dimensional metrics
    - Statistical analysis
    - Stress testing
    - Context window testing
    - Comparative reports

    Example:
        >>> profiler = LLMProfiler()
        >>>
        >>> # Profile single model
        >>> report = await profiler.profile_model(
        ...     provider="openai",
        ...     model="gpt-4o-mini",
        ...     benchmark_suite="standard",
        ... )
        >>>
        >>> # Compare models
        >>> comparison = await profiler.compare_models([
        ...     ("openai", "gpt-4o-mini"),
        ...     ("anthropic", "claude-3-5-haiku"),
        ...     ("gemini", "gemini-2.5-flash"),
        ... ])
    """

    def __init__(self, db_path: str = "llm_metrics.db"):
        """Initialize profiler.

        Args:
            db_path: Path to SQLite database for storing results
        """
        self.db_path = db_path

        # Load benchmark suites
        from coffee_maker.llm_profiler.benchmarks import (
            CodeGenBenchmark,
            SummarizationBenchmark,
            TranslationBenchmark,
        )

        self.benchmarks = {
            "code_generation": CodeGenBenchmark(),
            "summarization": SummarizationBenchmark(),
            "translation": TranslationBenchmark(),
        }

        # Metrics collectors
        from coffee_maker.llm_profiler.metrics import (
            LatencyMeter,
            QualityEvaluator,
            TokenCounter,
        )

        self.latency_meter = LatencyMeter()
        self.quality_evaluator = QualityEvaluator()
        self.token_counter = TokenCounter()

        logger = logging.getLogger(__name__)
        logger.info("LLMProfiler initialized")

    async def profile_model(
        self,
        provider: str,
        model: str,
        benchmark_suite: str = "standard",
        n_iterations: int = 10,
    ) -> ProfileReport:
        """Profile a single model.

        Args:
            provider: LLM provider
            model: Model name
            benchmark_suite: Benchmark suite to use
            n_iterations: Number of iterations per test

        Returns:
            Performance profile report
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Profiling {provider}/{model}")

        # Get benchmark
        benchmark = self.benchmarks.get(benchmark_suite)
        if not benchmark:
            raise ValueError(f"Unknown benchmark: {benchmark_suite}")

        # Run benchmark
        results = []
        for test_case in benchmark.test_cases:
            for _ in range(n_iterations):
                result = await self._run_test_case(
                    provider, model, test_case
                )
                results.append(result)

        # Analyze results
        report = self._analyze_results(provider, model, results)

        # Store in database
        self._store_report(report)

        logger.info(
            f"Profile complete: {provider}/{model} - "
            f"Quality: {report.quality_score:.3f}, "
            f"P50 latency: {report.latency_p50:.2f}s, "
            f"Cost: ${report.avg_cost_per_request:.4f}"
        )

        return report

    async def compare_models(
        self,
        models: List[tuple],  # [(provider, model), ...]
        benchmark_suite: str = "standard",
    ) -> Dict:
        """Compare multiple models.

        Args:
            models: List of (provider, model) tuples
            benchmark_suite: Benchmark to use

        Returns:
            Comparison report dictionary
        """
        # Profile all models
        reports = []
        for provider, model in models:
            report = await self.profile_model(
                provider, model, benchmark_suite
            )
            reports.append(report)

        # Generate comparison
        comparison = self._generate_comparison(reports)

        return comparison

    async def stress_test(
        self,
        provider: str,
        model: str,
        concurrent_requests: List[int] = [1, 5, 10, 20, 50],
        duration_minutes: int = 10,
    ) -> Dict:
        """Run stress test.

        Args:
            provider: Provider name
            model: Model name
            concurrent_requests: List of concurrency levels to test
            duration_minutes: Duration per level

        Returns:
            Stress test results
        """
        from coffee_maker.llm_profiler.testing import StressTester

        tester = StressTester()
        results = await tester.run(
            provider=provider,
            model=model,
            concurrent_requests=concurrent_requests,
            duration_minutes=duration_minutes,
        )

        return results

    async def test_context_window(
        self,
        provider: str,
        model: str,
        context_sizes: List[int] = [1000, 10000, 50000, 100000],
    ) -> Dict:
        """Test context window performance.

        Args:
            provider: Provider name
            model: Model name
            context_sizes: List of context sizes (in tokens)

        Returns:
            Context window test results
        """
        from coffee_maker.llm_profiler.testing import ContextTester

        tester = ContextTester()
        results = await tester.run(
            provider=provider,
            model=model,
            context_sizes=context_sizes,
        )

        return results

    async def _run_test_case(
        self,
        provider: str,
        model: str,
        test_case: Dict,
    ) -> Dict:
        """Run single test case."""
        from coffee_maker.langchain_observe.builder import LLMBuilder
        import time

        # Build LLM
        llm = (
            LLMBuilder()
            .with_primary(provider, model)
            .with_cost_tracking()
            .build()
        )

        # Measure latency
        start_time = time.time()

        try:
            response = await llm.ainvoke({"input": test_case["prompt"]})
            latency = time.time() - start_time

            output = response.content

            # Extract tokens
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                input_tokens = getattr(usage, "input_tokens", 0)
                output_tokens = getattr(usage, "output_tokens", 0)

            # Evaluate quality
            quality = await self.quality_evaluator.evaluate(
                output=output,
                expected=test_case.get("expected_output"),
                criteria=test_case.get("criteria", []),
            )

            return {
                "success": True,
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "quality": quality,
                "output": output,
            }

        except Exception as e:
            return {
                "success": False,
                "latency": time.time() - start_time,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    def _analyze_results(
        self,
        provider: str,
        model: str,
        results: List[Dict],
    ) -> ProfileReport:
        """Analyze test results."""
        import numpy as np

        # Filter successful results
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]

        if not successful:
            raise ValueError("All tests failed")

        # Latency statistics
        latencies = [r["latency"] for r in successful]
        latency_p50 = np.percentile(latencies, 50)
        latency_p95 = np.percentile(latencies, 95)
        latency_p99 = np.percentile(latencies, 99)
        latency_mean = np.mean(latencies)

        # Quality statistics
        qualities = [r.get("quality", 0.0) for r in successful]
        quality_score = np.mean(qualities)
        quality_std = np.std(qualities)

        # Token statistics
        input_tokens = [r.get("input_tokens", 0) for r in successful]
        output_tokens = [r.get("output_tokens", 0) for r in successful]
        avg_input = np.mean(input_tokens)
        avg_output = np.mean(output_tokens)

        # Error analysis
        error_types = {}
        for r in failed:
            error_type = r.get("error_type", "Unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return ProfileReport(
            provider=provider,
            model=model,
            timestamp=datetime.now().isoformat(),
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            latency_mean=latency_mean,
            quality_score=quality_score,
            quality_std=quality_std,
            cost_per_1m_input_tokens=0.0,  # TODO
            cost_per_1m_output_tokens=0.0,  # TODO
            avg_cost_per_request=0.0,  # TODO
            avg_input_tokens=int(avg_input),
            avg_output_tokens=int(avg_output),
            output_input_ratio=avg_output / max(avg_input, 1),
            success_rate=len(successful) / len(results),
            error_rate=len(failed) / len(results),
            error_types=error_types,
            requests_per_second=1.0 / latency_mean,
            raw_results=results,
        )

    def _generate_comparison(self, reports: List[ProfileReport]) -> Dict:
        """Generate comparison report."""
        comparison = {
            "reports": reports,
            "summary": {},
            "winners": {},
        }

        # Find winners in each category
        comparison["winners"]["fastest"] = min(
            reports, key=lambda r: r.latency_p50
        )
        comparison["winners"]["best_quality"] = max(
            reports, key=lambda r: r.quality_score
        )
        comparison["winners"]["cheapest"] = min(
            reports, key=lambda r: r.avg_cost_per_request
        )
        comparison["winners"]["most_reliable"] = max(
            reports, key=lambda r: r.success_rate
        )

        return comparison

    def _store_report(self, report: ProfileReport):
        """Store report in database."""
        # TODO: Implement SQLite storage
        pass
```

---

## 📊 Benchmarks

### Code Generation Benchmark

```python
"""Code generation benchmark."""

class CodeGenBenchmark:
    """Benchmark for code generation tasks."""

    def __init__(self):
        self.test_cases = [
            {
                "prompt": "Write a Python function to sort a list using quicksort",
                "expected_output": "def quicksort",
                "criteria": ["correctness", "efficiency", "readability"],
            },
            {
                "prompt": "Implement binary search in Python",
                "expected_output": "def binary_search",
                "criteria": ["correctness", "edge_cases"],
            },
            # ... 100 test cases
        ]
```

---

## 🚀 Exemples d'Utilisation

### Exemple 1: Profile Simple

```python
profiler = LLMProfiler()

report = await profiler.profile_model(
    provider="openai",
    model="gpt-4o-mini",
)

print(f"Quality: {report.quality_score:.3f}")
print(f"P50 Latency: {report.latency_p50:.2f}s")
print(f"Cost: ${report.avg_cost_per_request:.4f}")
```

### Exemple 2: Compare Models

```python
comparison = await profiler.compare_models([
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-3-5-haiku"),
    ("gemini", "gemini-2.5-flash"),
])

print(f"Fastest: {comparison['winners']['fastest'].model}")
print(f"Best Quality: {comparison['winners']['best_quality'].model}")
print(f"Cheapest: {comparison['winners']['cheapest'].model}")
```

### Exemple 3: Stress Test

```python
stress_results = await profiler.stress_test(
    provider="openai",
    model="gpt-4o-mini",
    concurrent_requests=[1, 5, 10, 20],
)

for concurrency, metrics in stress_results.items():
    print(f"{concurrency} concurrent: {metrics['p50_latency']:.2f}s")
```

---

## 📈 Roadmap

### Phase 1: Core (1 semaine)
- [ ] LLMProfiler base
- [ ] Latency measurement
- [ ] Basic benchmarks
- [ ] SQLite storage

### Phase 2: Benchmarks (1 semaine)
- [ ] Code generation
- [ ] Summarization
- [ ] Translation
- [ ] Math reasoning
- [ ] Quality evaluator

### Phase 3: Testing (1 semaine)
- [ ] Stress tester
- [ ] Context window tester
- [ ] Error analysis
- [ ] Statistical analysis

### Phase 4: Reporting (1 semaine)
- [ ] HTML reports
- [ ] JSON export
- [ ] Comparison charts
- [ ] Dashboard

---

**Status**: 📝 Documentation Complete
**Estimated Development Time**: 3-4 weeks
**Priority**: ⭐⭐⭐⭐
