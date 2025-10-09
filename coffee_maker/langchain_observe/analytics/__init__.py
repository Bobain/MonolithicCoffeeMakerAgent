"""Analytics and observability for LLM operations.

This module provides comprehensive analytics capabilities for Coffee Maker Agent:

- **Langfuse Export**: Export traces to local SQLite/PostgreSQL database
- **Performance Metrics**: Analyze LLM, prompt, and agent performance
- **Cost Tracking**: Detailed cost analytics and optimization insights
- **Rate Limiting**: Multi-process safe rate limit counters

Key Components:
    - LangfuseExporter: Export Langfuse data to local database
    - PerformanceAnalyzer: Analyze LLM and prompt performance
    - DatabaseSchema: SQLAlchemy models for metrics storage

Example:
    Export Langfuse data to SQLite:
    >>> from coffee_maker.langchain_observe.analytics import LangfuseExporter
    >>> from coffee_maker.langchain_observe.analytics.config import ExportConfig
    >>>
    >>> config = ExportConfig.from_env()
    >>> exporter = LangfuseExporter(config)
    >>> exporter.setup_database()
    >>> stats = exporter.export_traces()
    >>> print(f"Exported {stats['generations']} generations")

    Analyze LLM performance:
    >>> from coffee_maker.langchain_observe.analytics import PerformanceAnalyzer
    >>>
    >>> analyzer = PerformanceAnalyzer("llm_metrics.db")
    >>> perf = analyzer.get_llm_performance(days=7)
    >>> print(f"Average latency: {perf['avg_latency']:.2f}s")

See Also:
    - :class:`LangfuseExporter`: Main export functionality
    - :mod:`coffee_maker.langchain_observe.analytics.metrics`: Performance metrics
"""

from coffee_maker.langchain_observe.analytics.config import ExportConfig
from coffee_maker.langchain_observe.analytics.exporter import LangfuseExporter
from coffee_maker.langchain_observe.analytics.analyzer import PerformanceAnalyzer

__all__ = [
    "LangfuseExporter",
    "PerformanceAnalyzer",
    "ExportConfig",
]
