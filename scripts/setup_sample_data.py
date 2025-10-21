#!/usr/bin/env python3
"""Setup sample data for the analytics dashboard.

This script creates sample LLM traces and generations for testing the dashboard.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from coffee_maker.langfuse_observe.analytics.models_sqlite import init_database, Trace, Generation


def generate_sample_data(db_path: str, num_traces: int = 100):
    """Generate sample data for testing.

    Args:
        db_path: Path to SQLite database
        num_traces: Number of traces to generate
    """
    print(f"Initializing database at: {db_path}")
    conn = init_database(db_path)

    models = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "gemini-pro",
    ]

    agents = [
        "code_developer",
        "project_manager",
        "assistant",
        "spec_manager",
        "implementation_agent",
    ]

    # Cost per 1K tokens (approximate)
    model_costs = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
    }

    print(f"Generating {num_traces} sample traces...")

    for i in range(num_traces):
        # Random timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Create trace
        trace_id = str(uuid4())
        agent = random.choice(agents)

        trace = Trace(
            id=trace_id,
            name=f"{agent}_task",
            user_id=f"user_{random.randint(1, 10)}",
            session_id=f"session_{random.randint(1, 20)}",
            trace_metadata={"agent": agent, "priority": random.randint(1, 5)},
            created_at=created_at,
            tags=[agent, "production"],
        )

        conn.execute(
            """
            INSERT OR REPLACE INTO traces
            (id, name, user_id, session_id, trace_metadata, input, output,
             created_at, updated_at, release, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            trace.to_db_row(),
        )

        # Create 1-3 generations per trace
        num_generations = random.randint(1, 3)
        for j in range(num_generations):
            model = random.choice(models)
            generation_id = str(uuid4())

            # Random token counts
            input_tokens = random.randint(100, 5000)
            output_tokens = random.randint(50, 2000)
            total_tokens = input_tokens + output_tokens

            # Calculate costs
            costs = model_costs.get(model, {"input": 0.001, "output": 0.002})
            input_cost = (input_tokens / 1000) * costs["input"]
            output_cost = (output_tokens / 1000) * costs["output"]
            total_cost = input_cost + output_cost

            # Random latency (500ms - 30s)
            latency_ms = random.randint(500, 30000)

            generation = Generation(
                id=generation_id,
                trace_id=trace_id,
                name=f"{model}_generation",
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                input_cost=input_cost,
                output_cost=output_cost,
                total_cost=total_cost,
                latency_ms=latency_ms,
                created_at=created_at + timedelta(seconds=j),
                metadata={"agent": agent, "model": model},
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO generations
                (id, trace_id, name, model, model_parameters, input, output,
                 input_tokens, output_tokens, total_tokens, input_cost, output_cost, total_cost,
                 latency_ms, created_at, updated_at, metadata, level, status_message,
                 completion_start_time, completion_end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                generation.to_db_row(),
            )

        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{num_traces} traces...")

    conn.commit()

    # Print statistics
    cursor = conn.execute("SELECT COUNT(*) FROM traces")
    trace_count = cursor.fetchone()[0]

    cursor = conn.execute("SELECT COUNT(*) FROM generations")
    gen_count = cursor.fetchone()[0]

    cursor = conn.execute("SELECT SUM(total_cost) FROM generations")
    total_cost = cursor.fetchone()[0] or 0.0

    cursor = conn.execute("SELECT SUM(total_tokens) FROM generations")
    total_tokens = cursor.fetchone()[0] or 0

    print("\n" + "=" * 60)
    print("✅ Sample Data Generated Successfully")
    print("=" * 60)
    print(f"\nTraces created: {trace_count:,}")
    print(f"Generations created: {gen_count:,}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"\nDatabase: {db_path}")
    print("\nYou can now start the dashboard:")
    print("  streamlit run streamlit_apps/analytics_dashboard/app.py")

    conn.close()


if __name__ == "__main__":
    db_path = project_root / "llm_metrics.db"
    generate_sample_data(str(db_path), num_traces=100)
