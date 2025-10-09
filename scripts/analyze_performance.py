#!/usr/bin/env python3
"""Analyze LLM performance from exported metrics.

This script analyzes LLM performance data from the local database,
providing insights into latency, costs, usage patterns, and errors.

Usage:
    # Analyze last 7 days
    python scripts/analyze_performance.py

    # Analyze last 30 days
    python scripts/analyze_performance.py --days 30

    # Analyze specific model
    python scripts/analyze_performance.py --model "openai/gpt-4o"

    # Show most expensive prompts
    python scripts/analyze_performance.py --expensive --limit 10

    # Cost trends
    python scripts/analyze_performance.py --cost-trends --days 30

Example output:
    === LLM Performance Analysis (Last 7 days) ===

    Overall Metrics:
      Total Requests: 1,234
      Total Cost: $45.67
      Avg Cost/Request: $0.037
      Total Tokens: 2.3M

    Latency:
      Average: 1,234ms
      P50: 890ms
      P95: 3,200ms
      P99: 5,100ms

    By Model:
      openai/gpt-4o: 800 requests, $35.20 (77%)
      openai/gpt-4o-mini: 434 requests, $10.47 (23%)
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.langchain_observe.analytics import PerformanceAnalyzer
from coffee_maker.langchain_observe.analytics.config import ExportConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def format_number(num: float, decimals: int = 0) -> str:
    """Format number with commas."""
    if decimals == 0:
        return f"{int(num):,}"
    return f"{num:,.{decimals}f}"


def print_performance_metrics(metrics: dict, title: str = "Performance Metrics"):
    """Print performance metrics in a formatted table."""
    print(f"\n{title}:")
    print(f"  Total Requests: {format_number(metrics['total_requests'])}")
    print(f"  Total Cost: ${metrics['total_cost_usd']:.2f}")
    print(f"  Avg Cost/Request: ${metrics['avg_cost_per_request']:.4f}")
    print(f"  Total Tokens: {format_number(metrics['total_tokens'] / 1_000_000, 2)}M")

    if metrics["total_requests"] > 0:
        print(f"\nLatency:")
        print(f"  Average: {format_number(metrics['avg_latency_ms'])}ms")
        print(f"  P50: {format_number(metrics['p50_latency_ms'])}ms")
        print(f"  P95: {format_number(metrics['p95_latency_ms'])}ms")
        print(f"  P99: {format_number(metrics['p99_latency_ms'])}ms")

    if metrics["error_count"] > 0:
        print(f"\nErrors:")
        print(f"  Error Count: {metrics['error_count']}")
        print(f"  Error Rate: {metrics['error_rate']:.2%}")


def main():
    """Run performance analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze LLM performance metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Overall performance (last 7 days)
  python scripts/analyze_performance.py

  # Last 30 days
  python scripts/analyze_performance.py --days 30

  # Specific model
  python scripts/analyze_performance.py --model "openai/gpt-4o"

  # Most expensive prompts
  python scripts/analyze_performance.py --expensive --limit 10

  # Slowest requests
  python scripts/analyze_performance.py --slow --limit 10

  # Cost trends
  python scripts/analyze_performance.py --cost-trends --days 30

  # Error analysis
  python scripts/analyze_performance.py --errors
        """,
    )

    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)",
    )

    parser.add_argument(
        "--model",
        type=str,
        help="Filter by specific model (e.g., 'openai/gpt-4o')",
    )

    parser.add_argument(
        "--user",
        type=str,
        help="Filter by specific user ID",
    )

    parser.add_argument(
        "--expensive",
        action="store_true",
        help="Show most expensive prompts",
    )

    parser.add_argument(
        "--slow",
        action="store_true",
        help="Show slowest requests",
    )

    parser.add_argument(
        "--cost-trends",
        action="store_true",
        help="Show cost trends over time",
    )

    parser.add_argument(
        "--errors",
        action="store_true",
        help="Show error analysis",
    )

    parser.add_argument(
        "--by-model",
        action="store_true",
        help="Show breakdown by model",
    )

    parser.add_argument(
        "--by-user",
        action="store_true",
        help="Show breakdown by user",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit for lists (default: 10)",
    )

    args = parser.parse_args()

    try:
        # Load config to get database URL
        config = ExportConfig.from_env()
        db_url = config.db_url

        logger.info(f"Analyzing database: {db_url}")

        # Create analyzer
        analyzer = PerformanceAnalyzer(db_url)

        # Print header
        print("\n" + "=" * 70)
        print(f"LLM Performance Analysis (Last {args.days} days)")
        print("=" * 70)

        # Overall metrics
        if not (args.expensive or args.slow or args.cost_trends or args.errors):
            metrics = analyzer.get_llm_performance(days=args.days, model=args.model, user_id=args.user)
            print_performance_metrics(metrics, "Overall Metrics")

        # By model breakdown
        if args.by_model:
            print("\n" + "=" * 70)
            print("Performance by Model")
            print("=" * 70)
            by_model = analyzer.get_performance_by_model(days=args.days)

            # Sort by cost
            sorted_models = sorted(by_model.items(), key=lambda x: x[1]["total_cost_usd"], reverse=True)

            for model, metrics in sorted_models:
                pct = metrics["total_cost_usd"] / sum(m["total_cost_usd"] for m in by_model.values()) * 100
                print(f"\n{model}:")
                print(
                    f"  Requests: {format_number(metrics['total_requests'])} "
                    f"| Cost: ${metrics['total_cost_usd']:.2f} ({pct:.1f}%)"
                )
                print(
                    f"  Avg Latency: {format_number(metrics['avg_latency_ms'])}ms "
                    f"| P95: {format_number(metrics['p95_latency_ms'])}ms"
                )

        # By user breakdown
        if args.by_user:
            print("\n" + "=" * 70)
            print("Usage by User")
            print("=" * 70)
            by_user = analyzer.get_usage_by_user(days=args.days)

            # Sort by cost
            sorted_users = sorted(by_user.items(), key=lambda x: x[1]["total_cost_usd"], reverse=True)

            for user_id, metrics in sorted_users[: args.limit]:
                print(f"\n{user_id}:")
                print(
                    f"  Requests: {format_number(metrics['total_requests'])} "
                    f"| Cost: ${metrics['total_cost_usd']:.2f}"
                )
                print(f"  Tokens: {format_number(metrics['total_tokens'])}")

        # Most expensive prompts
        if args.expensive:
            print("\n" + "=" * 70)
            print(f"Most Expensive Prompts (Top {args.limit})")
            print("=" * 70)
            expensive = analyzer.get_most_expensive_prompts(limit=args.limit, days=args.days)

            for i, prompt in enumerate(expensive, 1):
                print(f"\n{i}. ${prompt['total_cost']:.4f} - {prompt['model']}")
                print(f"   Tokens: {format_number(prompt['total_tokens'])}")
                print(f"   Input: {prompt['input'][:100]}...")

        # Slowest requests
        if args.slow:
            print("\n" + "=" * 70)
            print(f"Slowest Requests (Top {args.limit})")
            print("=" * 70)
            slow = analyzer.get_slowest_requests(limit=args.limit, days=args.days)

            for i, req in enumerate(slow, 1):
                print(f"\n{i}. {format_number(req['latency_ms'])}ms - {req['model']}")
                print(f"   Tokens: {format_number(req['total_tokens'])}")
                print(f"   Input: {req['input'][:100]}...")

        # Cost trends
        if args.cost_trends:
            print("\n" + "=" * 70)
            print("Cost Trends (Daily)")
            print("=" * 70)
            trends = analyzer.get_cost_over_time(days=args.days, bucket_hours=24, model=args.model)

            for bucket in trends[-14:]:  # Show last 14 days
                date = bucket["time_bucket"].strftime("%Y-%m-%d")
                cost = bucket["total_cost"]
                requests = bucket["total_requests"]
                tokens = bucket["total_tokens"]
                print(
                    f"{date}: ${cost:>7.2f} | "
                    f"{format_number(requests):>5} requests | "
                    f"{format_number(tokens / 1000):>6}K tokens"
                )

        # Error analysis
        if args.errors:
            print("\n" + "=" * 70)
            print("Error Analysis")
            print("=" * 70)
            error_analysis = analyzer.get_error_analysis(days=args.days)

            print(f"\nTotal Errors: {error_analysis['total_errors']}")
            print(f"Error Rate: {error_analysis['error_rate']:.2%}")

            if error_analysis["errors_by_model"]:
                print("\nErrors by Model:")
                for model, count in sorted(error_analysis["errors_by_model"].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {model}: {count}")

            if error_analysis["common_error_messages"]:
                print(f"\nMost Common Errors (Top {min(5, len(error_analysis['common_error_messages']))}):")
                for i, error in enumerate(error_analysis["common_error_messages"][:5], 1):
                    print(f"  {i}. [{error['count']}x] {error['message'][:80]}")

        print("\n" + "=" * 70)

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Make sure the database has been set up and populated.")
        logger.error("Run: python scripts/export_langfuse_data.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
