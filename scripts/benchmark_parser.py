#!/usr/bin/env python3
"""Benchmark ROADMAP parser performance - before vs after caching.

This script measures the performance improvement from implementing
the cached parser in US-021 Phase 4.
"""

import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.autonomous.roadmap_parser import RoadmapParser
from coffee_maker.autonomous.cached_roadmap_parser import CachedRoadmapParser


def benchmark_original_parser(iterations=100):
    """Benchmark original RoadmapParser."""
    print(f"\n{'='*80}")
    print(f"Benchmarking Original RoadmapParser ({iterations} iterations)")
    print(f"{'='*80}")

    roadmap_path = project_root / "docs" / "ROADMAP.md"

    start = time.time()
    for i in range(iterations):
        parser = RoadmapParser(str(roadmap_path))
        priorities = parser.get_priorities()
        next_priority = parser.get_next_planned_priority()
    end = time.time()

    total_time = end - start
    avg_time = total_time / iterations

    print(f"Total time: {total_time:.3f}s")
    print(f"Average per iteration: {avg_time:.4f}s ({avg_time*1000:.2f}ms)")
    print(f"Priorities found: {len(priorities)}")
    print(f"Next priority: {next_priority['name'] if next_priority else 'None'}")

    return total_time, avg_time


def benchmark_cached_parser(iterations=100):
    """Benchmark new CachedRoadmapParser."""
    print(f"\n{'='*80}")
    print(f"Benchmarking CachedRoadmapParser ({iterations} iterations)")
    print(f"{'='*80}")

    roadmap_path = project_root / "docs" / "ROADMAP.md"
    parser = CachedRoadmapParser(str(roadmap_path))  # Create once!

    start = time.time()
    for i in range(iterations):
        priorities = parser.get_priorities()  # Should use cache after first call
        next_priority = parser.get_next_planned_priority()
    end = time.time()

    total_time = end - start
    avg_time = total_time / iterations

    print(f"Total time: {total_time:.3f}s")
    print(f"Average per iteration: {avg_time:.4f}s ({avg_time*1000:.2f}ms)")
    print(f"Priorities found: {len(priorities)}")
    print(f"Next priority: {next_priority['name'] if next_priority else 'None'}")

    # Show cache stats
    stats = parser.get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Cached: {stats['cached']}")
    print(f"  Priorities count: {stats['priorities_count']}")
    print(f"  File size: {stats['file_size'] / 1024:.1f}KB")

    return total_time, avg_time


def compare_results(original_time, cached_time):
    """Compare and display performance improvement."""
    print(f"\n{'='*80}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*80}")

    improvement = ((original_time - cached_time) / original_time) * 100
    speedup = original_time / cached_time

    print(f"\nOriginal parser: {original_time:.3f}s")
    print(f"Cached parser:   {cached_time:.3f}s")
    print(f"\nImprovement: {improvement:.1f}% faster")
    print(f"Speedup: {speedup:.1f}x")

    if improvement >= 50:
        print("\n✅ EXCELLENT! Achieved target of 50%+ improvement")
    elif improvement >= 30:
        print("\n✅ GOOD! Significant improvement achieved")
    else:
        print("\n⚠️  Improvement less than expected (target: 50%)")

    return improvement, speedup


def main():
    """Run benchmarks and compare results."""
    print("🏁 ROADMAP Parser Performance Benchmark")
    print("=" * 80)
    print("US-021 Phase 4: Measuring caching optimization")
    print("=" * 80)

    iterations = 100

    # Benchmark original
    original_total, original_avg = benchmark_original_parser(iterations)

    # Benchmark cached
    cached_total, cached_avg = benchmark_cached_parser(iterations)

    # Compare
    improvement, speedup = compare_results(original_total, cached_total)

    print(f"\n{'='*80}")
    print("CONCLUSION")
    print(f"{'='*80}")
    print(f"\nThe cached parser is {speedup:.1f}x faster, reducing parse time by {improvement:.1f}%.")
    print(f"In a daemon that checks every 30s, this saves ~{original_avg - cached_avg:.3f}s per iteration.")
    print(f"\nWith the daemon running 24/7, this optimization saves:")
    print(f"  Per hour: {((original_avg - cached_avg) * (3600/30)):.1f} seconds")
    print(f"  Per day: {((original_avg - cached_avg) * (3600/30) * 24 / 60):.1f} minutes")


if __name__ == "__main__":
    main()
