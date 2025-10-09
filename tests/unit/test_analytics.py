"""Unit tests for analytics module."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from coffee_maker.langchain_observe.analytics.analyzer import PerformanceAnalyzer
from coffee_maker.langchain_observe.analytics.config import ExportConfig
from coffee_maker.langchain_observe.analytics.models import Base, Generation, Trace


@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    yield db_url

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_data(temp_db):
    """Insert sample data for testing."""
    engine = create_engine(temp_db)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Create traces
        now = datetime.utcnow()

        for i in range(10):
            trace = Trace(
                id=f"trace-{i}",
                name=f"test-trace-{i}",
                user_id=f"user-{i % 3}",  # 3 different users
                created_at=now - timedelta(hours=i),
            )
            session.add(trace)

            # Create generations for each trace
            for j in range(2):
                generation = Generation(
                    id=f"gen-{i}-{j}",
                    trace_id=f"trace-{i}",
                    name=f"generation-{i}-{j}",
                    model="openai/gpt-4o" if i % 2 == 0 else "openai/gpt-4o-mini",
                    input=f"Test prompt {i}-{j}",
                    output=f"Test output {i}-{j}",
                    input_tokens=100 * (i + 1),
                    output_tokens=50 * (i + 1),
                    total_tokens=150 * (i + 1),
                    input_cost=0.01 * (i + 1),
                    output_cost=0.005 * (i + 1),
                    total_cost=0.015 * (i + 1),
                    latency_ms=100 + (i * 50),
                    created_at=now - timedelta(hours=i),
                    level="DEFAULT",
                )
                session.add(generation)

        # Add some error generations
        error_trace = Trace(
            id="error-trace",
            name="error-test",
            created_at=now - timedelta(hours=1),
        )
        session.add(error_trace)

        error_gen = Generation(
            id="error-gen",
            trace_id="error-trace",
            model="openai/gpt-4o",
            input="Error prompt",
            output="Error output",
            level="ERROR",
            status_message="Rate limit exceeded",
            created_at=now - timedelta(hours=1),
        )
        session.add(error_gen)

        session.commit()

    return temp_db


class TestExportConfig:
    """Test ExportConfig."""

    def test_default_config(self, monkeypatch):
        """Test loading default configuration."""
        monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
        monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")

        config = ExportConfig.from_env()

        assert config.langfuse_public_key == "pk-test"
        assert config.langfuse_secret_key == "sk-test"
        assert config.db_type == "sqlite"
        assert config.sqlite_path == "llm_metrics.db"

    def test_sqlite_db_url(self):
        """Test SQLite database URL generation."""
        config = ExportConfig(
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
            db_type="sqlite",
            sqlite_path="test.db",
        )

        assert config.db_url == "sqlite:///test.db"

    def test_postgresql_db_url(self):
        """Test PostgreSQL database URL generation."""
        config = ExportConfig(
            langfuse_public_key="pk-test",
            langfuse_secret_key="sk-test",
            db_type="postgresql",
            postgres_user="testuser",
            postgres_password="testpass",
            postgres_host="localhost",
            postgres_port=5432,
            postgres_database="testdb",
        )

        assert config.db_url == "postgresql://testuser:testpass@localhost:5432/testdb"

    def test_missing_credentials(self, monkeypatch):
        """Test error when credentials are missing."""
        monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
        monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)

        with pytest.raises(ValueError, match="LANGFUSE_PUBLIC_KEY"):
            ExportConfig.from_env()


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer."""

    def test_get_llm_performance(self, sample_data):
        """Test getting overall performance metrics."""
        analyzer = PerformanceAnalyzer(sample_data)
        metrics = analyzer.get_llm_performance(days=7)

        # Check basic metrics
        assert metrics["total_requests"] == 21  # 10 traces * 2 gens + 1 error
        assert metrics["total_tokens"] > 0
        assert metrics["total_cost_usd"] > 0
        assert metrics["avg_latency_ms"] > 0

        # Check percentiles
        assert metrics["p50_latency_ms"] > 0
        assert metrics["p95_latency_ms"] >= metrics["p50_latency_ms"]
        assert metrics["p99_latency_ms"] >= metrics["p95_latency_ms"]

        # Check error rate
        assert metrics["error_count"] == 1
        assert 0 <= metrics["error_rate"] <= 1

    def test_get_performance_by_model(self, sample_data):
        """Test getting performance breakdown by model."""
        analyzer = PerformanceAnalyzer(sample_data)
        by_model = analyzer.get_performance_by_model(days=7)

        # Should have two models
        assert "openai/gpt-4o" in by_model
        assert "openai/gpt-4o-mini" in by_model

        # Each model should have valid metrics
        for model, metrics in by_model.items():
            assert metrics["total_requests"] > 0
            assert metrics["total_cost_usd"] >= 0

    def test_filter_by_model(self, sample_data):
        """Test filtering by specific model."""
        analyzer = PerformanceAnalyzer(sample_data)

        gpt4_metrics = analyzer.get_llm_performance(days=7, model="openai/gpt-4o")
        mini_metrics = analyzer.get_llm_performance(days=7, model="openai/gpt-4o-mini")

        # Should have different request counts
        assert gpt4_metrics["total_requests"] != mini_metrics["total_requests"]

        # Combined should equal total
        total_metrics = analyzer.get_llm_performance(days=7)
        assert gpt4_metrics["total_requests"] + mini_metrics["total_requests"] == total_metrics["total_requests"]

    def test_filter_by_user(self, sample_data):
        """Test filtering by user ID."""
        analyzer = PerformanceAnalyzer(sample_data)

        user0_metrics = analyzer.get_llm_performance(days=7, user_id="user-0")
        user1_metrics = analyzer.get_llm_performance(days=7, user_id="user-1")

        # Each user should have some requests
        assert user0_metrics["total_requests"] > 0
        assert user1_metrics["total_requests"] > 0

    def test_get_most_expensive_prompts(self, sample_data):
        """Test getting most expensive prompts."""
        analyzer = PerformanceAnalyzer(sample_data)
        expensive = analyzer.get_most_expensive_prompts(limit=5, days=7)

        assert len(expensive) <= 5
        assert len(expensive) > 0

        # Should be sorted by cost (descending)
        costs = [p["total_cost"] for p in expensive]
        assert costs == sorted(costs, reverse=True)

        # Check structure
        assert "generation_id" in expensive[0]
        assert "model" in expensive[0]
        assert "input" in expensive[0]
        assert "total_cost" in expensive[0]

    def test_get_slowest_requests(self, sample_data):
        """Test getting slowest requests."""
        analyzer = PerformanceAnalyzer(sample_data)
        slow = analyzer.get_slowest_requests(limit=5, days=7)

        assert len(slow) <= 5
        assert len(slow) > 0

        # Should be sorted by latency (descending)
        latencies = [r["latency_ms"] for r in slow]
        assert latencies == sorted(latencies, reverse=True)

    def test_get_usage_by_user(self, sample_data):
        """Test getting usage statistics by user."""
        analyzer = PerformanceAnalyzer(sample_data)
        by_user = analyzer.get_usage_by_user(days=7)

        # Should have 3 users (user-0, user-1, user-2)
        assert len(by_user) == 3
        assert "user-0" in by_user
        assert "user-1" in by_user
        assert "user-2" in by_user

        # Each user should have valid metrics
        for user_id, metrics in by_user.items():
            assert metrics["total_requests"] > 0

    def test_get_cost_over_time(self, sample_data):
        """Test getting cost trends over time."""
        analyzer = PerformanceAnalyzer(sample_data)
        trends = analyzer.get_cost_over_time(days=7, bucket_hours=24)

        # Should have some buckets
        assert len(trends) > 0

        # Each bucket should have valid data
        for bucket in trends:
            assert "time_bucket" in bucket
            assert "total_cost" in bucket
            assert "total_requests" in bucket
            assert "total_tokens" in bucket

        # Should be sorted by time
        times = [b["time_bucket"] for b in trends]
        assert times == sorted(times)

    def test_get_error_analysis(self, sample_data):
        """Test error analysis."""
        analyzer = PerformanceAnalyzer(sample_data)
        errors = analyzer.get_error_analysis(days=7)

        assert errors["total_errors"] == 1
        assert 0 <= errors["error_rate"] <= 1

        # Should have error breakdown
        assert "openai/gpt-4o" in errors["errors_by_model"]

        # Should have common error messages
        assert len(errors["common_error_messages"]) > 0
        assert errors["common_error_messages"][0]["message"] == "Rate limit exceeded"
        assert errors["common_error_messages"][0]["count"] == 1

    def test_empty_database(self, temp_db):
        """Test analysis on empty database."""
        analyzer = PerformanceAnalyzer(temp_db)
        metrics = analyzer.get_llm_performance(days=7)

        # Should return zeros for empty database
        assert metrics["total_requests"] == 0
        assert metrics["total_cost_usd"] == 0
        assert metrics["avg_latency_ms"] == 0

    def test_percentile_calculation(self, sample_data):
        """Test percentile calculation accuracy."""
        analyzer = PerformanceAnalyzer(sample_data)

        # Create analyzer instance to test _percentile method
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        p50 = analyzer._percentile(values, 50)
        p95 = analyzer._percentile(values, 95)
        p99 = analyzer._percentile(values, 99)

        # P50 should be around median (5 or 6 depending on implementation)
        assert 5 <= p50 <= 6
        assert p95 >= p50
        assert p99 >= p95
        assert p99 == 10  # P99 of 1-10 should be 10


class TestDatabaseModels:
    """Test database models."""

    def test_create_trace(self, temp_db):
        """Test creating trace record."""
        engine = create_engine(temp_db)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            trace = Trace(
                id="test-trace",
                name="test",
                user_id="user-123",
                created_at=datetime.utcnow(),
            )
            session.add(trace)
            session.commit()

            # Retrieve and verify
            retrieved = session.query(Trace).filter_by(id="test-trace").first()
            assert retrieved is not None
            assert retrieved.name == "test"
            assert retrieved.user_id == "user-123"

    def test_create_generation(self, temp_db):
        """Test creating generation record."""
        engine = create_engine(temp_db)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            # First create a trace
            trace = Trace(id="trace-1", name="trace", created_at=datetime.utcnow())
            session.add(trace)

            # Then create generation
            generation = Generation(
                id="gen-1",
                trace_id="trace-1",
                model="openai/gpt-4o",
                input="test input",
                output="test output",
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                total_cost=0.015,
                latency_ms=1234,
                created_at=datetime.utcnow(),
            )
            session.add(generation)
            session.commit()

            # Retrieve and verify
            retrieved = session.query(Generation).filter_by(id="gen-1").first()
            assert retrieved is not None
            assert retrieved.model == "openai/gpt-4o"
            assert retrieved.input_tokens == 100
            assert retrieved.total_cost == 0.015

    def test_trace_generation_relationship(self, temp_db):
        """Test relationship between trace and generations."""
        engine = create_engine(temp_db)
        Session = sessionmaker(bind=engine)

        with Session() as session:
            trace = Trace(id="trace-1", name="trace", created_at=datetime.utcnow())

            gen1 = Generation(
                id="gen-1",
                trace_id="trace-1",
                model="openai/gpt-4o",
                created_at=datetime.utcnow(),
            )
            gen2 = Generation(
                id="gen-2",
                trace_id="trace-1",
                model="openai/gpt-4o-mini",
                created_at=datetime.utcnow(),
            )

            session.add(trace)
            session.add(gen1)
            session.add(gen2)
            session.commit()

            # Test relationship
            retrieved_trace = session.query(Trace).filter_by(id="trace-1").first()
            assert len(retrieved_trace.generations) == 2

            # Test cascade delete
            session.delete(retrieved_trace)
            session.commit()

            # Generations should be deleted too
            assert session.query(Generation).count() == 0
