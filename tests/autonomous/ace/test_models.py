"""Tests for ACE data models."""

from datetime import datetime


from coffee_maker.autonomous.ace.models import (
    DeltaItem,
    Evidence,
    Execution,
    ExecutionTrace,
    ExternalObservation,
    HealthMetrics,
    InternalObservation,
    Playbook,
    PlaybookBullet,
)


class TestExternalObservation:
    """Tests for ExternalObservation dataclass."""

    def test_create_empty(self):
        """Test creating empty external observation."""
        obs = ExternalObservation()
        assert obs.git_changes == []
        assert obs.files_created == []
        assert obs.files_modified == []
        assert obs.files_deleted == []
        assert obs.commands_executed == []

    def test_create_with_data(self):
        """Test creating external observation with data."""
        obs = ExternalObservation(
            git_changes=["Modified 2 files"],
            files_created=["test.py"],
            files_modified=["main.py", "utils.py"],
            files_deleted=[],
            commands_executed=["pytest", "git commit"],
        )
        assert obs.git_changes == ["Modified 2 files"]
        assert obs.files_created == ["test.py"]
        assert obs.files_modified == ["main.py", "utils.py"]
        assert len(obs.commands_executed) == 2

    def test_to_dict(self):
        """Test converting to dictionary."""
        obs = ExternalObservation(files_created=["test.py"], files_modified=["main.py"])
        data = obs.to_dict()
        assert data["files_created"] == ["test.py"]
        assert data["files_modified"] == ["main.py"]
        assert "git_changes" in data

    def test_from_dict(self):
        """Test loading from dictionary."""
        data = {
            "files_created": ["test.py"],
            "files_modified": ["main.py"],
            "git_changes": ["Modified 1 file"],
        }
        obs = ExternalObservation.from_dict(data)
        assert obs.files_created == ["test.py"]
        assert obs.files_modified == ["main.py"]
        assert obs.git_changes == ["Modified 1 file"]

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        obs = ExternalObservation(
            git_changes=["test"],
            files_created=["a.py"],
            files_modified=["b.py"],
            commands_executed=["ls"],
        )
        data = obs.to_dict()
        obs2 = ExternalObservation.from_dict(data)
        assert obs.git_changes == obs2.git_changes
        assert obs.files_created == obs2.files_created
        assert obs.commands_executed == obs2.commands_executed


class TestInternalObservation:
    """Tests for InternalObservation dataclass."""

    def test_create_empty(self):
        """Test creating empty internal observation."""
        obs = InternalObservation()
        assert obs.reasoning_steps == []
        assert obs.decisions_made == []
        assert obs.tools_called == []
        assert obs.context_used == []
        assert obs.context_ignored == []

    def test_create_with_data(self):
        """Test creating internal observation with data."""
        obs = InternalObservation(
            reasoning_steps=["Analyze requirement", "Implement solution"],
            decisions_made=["Use pytest for testing"],
            tools_called=[{"tool": "read", "params": {"file": "test.py"}}],
            context_used=["bullet_1", "bullet_2"],
            context_ignored=["bullet_3"],
        )
        assert len(obs.reasoning_steps) == 2
        assert len(obs.decisions_made) == 1
        assert len(obs.tools_called) == 1
        assert obs.context_used == ["bullet_1", "bullet_2"]

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        obs = InternalObservation(
            reasoning_steps=["step1"],
            decisions_made=["decision1"],
            tools_called=[{"tool": "test"}],
        )
        data = obs.to_dict()
        obs2 = InternalObservation.from_dict(data)
        assert obs.reasoning_steps == obs2.reasoning_steps
        assert obs.decisions_made == obs2.decisions_made


class TestExecutionTrace:
    """Tests for ExecutionTrace dataclass."""

    def test_create_trace(self):
        """Test creating execution trace."""
        trace = ExecutionTrace(
            trace_id="12345",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test query",
            current_context="# Test context",
        )
        assert trace.trace_id == "12345"
        assert trace.user_query == "Test query"
        assert trace.executions == []

    def test_add_executions(self):
        """Test adding executions to trace."""
        trace = ExecutionTrace(
            trace_id="12345",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test",
            current_context="",
        )

        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(),
            internal_observation=InternalObservation(),
            result_status="success",
        )

        trace.executions.append(exec1)
        assert len(trace.executions) == 1
        assert trace.executions[0].result_status == "success"

    def test_to_dict(self):
        """Test converting trace to dictionary."""
        trace = ExecutionTrace(
            trace_id="12345",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "test"},
            user_query="Test",
            current_context="",
        )
        data = trace.to_dict()
        assert data["trace_id"] == "12345"
        assert data["user_query"] == "Test"
        assert "timestamp" in data

    def test_from_dict(self):
        """Test loading trace from dictionary."""
        data = {
            "trace_id": "12345",
            "timestamp": datetime.now().isoformat(),
            "agent_identity": {"target_agent": "test"},
            "user_query": "Test query",
            "current_context": "Context",
            "executions": [],
            "comparative_observations": None,
            "helpful_context_elements": [],
            "problematic_context_elements": [],
            "new_insights_surfaced": [],
        }
        trace = ExecutionTrace.from_dict(data)
        assert trace.trace_id == "12345"
        assert trace.user_query == "Test query"

    def test_to_markdown(self):
        """Test generating markdown representation."""
        trace = ExecutionTrace(
            trace_id="12345",
            timestamp=datetime.now(),
            agent_identity={
                "target_agent": "code_developer",
                "agent_objective": "Test objective",
                "success_criteria": "Tests pass",
            },
            user_query="Test query",
            current_context="",
        )

        exec1 = Execution(
            execution_id=1,
            external_observation=ExternalObservation(files_created=["test.py"]),
            internal_observation=InternalObservation(reasoning_steps=["Step 1"]),
            result_status="success",
            duration_seconds=5.2,
        )
        trace.executions.append(exec1)

        markdown = trace.to_markdown()
        assert "# Execution Trace: 12345" in markdown
        assert "Test query" in markdown
        assert "Execution 1" in markdown
        assert "success" in markdown


class TestDeltaItem:
    """Tests for DeltaItem dataclass."""

    def test_create_delta(self):
        """Test creating delta item."""
        delta = DeltaItem(
            delta_id="delta_1",
            insight_type="success_pattern",
            title="Test Pattern",
            description="Test description",
            recommendation="Use this pattern",
            priority=4,
            confidence=0.8,
        )
        assert delta.delta_id == "delta_1"
        assert delta.insight_type == "success_pattern"
        assert delta.priority == 4
        assert delta.confidence == 0.8

    def test_add_evidence(self):
        """Test adding evidence to delta."""
        delta = DeltaItem(
            delta_id="delta_1",
            insight_type="failure_mode",
            title="Test",
            description="Test",
            recommendation="Test",
        )
        evidence = Evidence(trace_id="trace_1", execution_id=1, example="Example failure")
        delta.evidence.append(evidence)
        assert len(delta.evidence) == 1

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        delta = DeltaItem(
            delta_id="delta_1",
            insight_type="success_pattern",
            title="Test",
            description="Desc",
            recommendation="Rec",
            priority=5,
            confidence=0.9,
        )
        data = delta.to_dict()
        delta2 = DeltaItem.from_dict(data)
        assert delta.delta_id == delta2.delta_id
        assert delta.priority == delta2.priority
        assert delta.confidence == delta2.confidence


class TestPlaybookBullet:
    """Tests for PlaybookBullet dataclass."""

    def test_create_bullet(self):
        """Test creating playbook bullet."""
        bullet = PlaybookBullet(bullet_id="bullet_1", type="success_pattern", content="Test bullet content")
        assert bullet.bullet_id == "bullet_1"
        assert bullet.type == "success_pattern"
        assert bullet.content == "Test bullet content"
        assert bullet.helpful_count == 0
        assert bullet.harmful_count == 0

    def test_update_metrics(self):
        """Test updating bullet metrics."""
        bullet = PlaybookBullet(bullet_id="bullet_1", type="success_pattern", content="Test")
        bullet.helpful_count += 1
        bullet.confidence = 0.9
        assert bullet.helpful_count == 1
        assert bullet.confidence == 0.9

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        bullet = PlaybookBullet(
            bullet_id="bullet_1",
            type="success_pattern",
            content="Content",
            helpful_count=5,
            harmful_count=1,
            confidence=0.85,
        )
        data = bullet.to_dict()
        bullet2 = PlaybookBullet.from_dict(data)
        assert bullet.bullet_id == bullet2.bullet_id
        assert bullet.helpful_count == bullet2.helpful_count
        assert bullet.confidence == bullet2.confidence


class TestPlaybook:
    """Tests for Playbook dataclass."""

    def test_create_playbook(self):
        """Test creating playbook."""
        playbook = Playbook(
            playbook_version="1.0",
            agent_name="code_developer",
            agent_objective="Implement features",
            success_criteria="Tests pass",
            last_updated=datetime.now(),
            total_bullets=0,
            effectiveness_score=0.0,
        )
        assert playbook.agent_name == "code_developer"
        assert playbook.total_bullets == 0
        assert playbook.categories == {}

    def test_add_bullets_to_categories(self):
        """Test adding bullets to playbook categories."""
        playbook = Playbook(
            playbook_version="1.0",
            agent_name="test",
            agent_objective="Test",
            success_criteria="Pass",
            last_updated=datetime.now(),
            total_bullets=0,
            effectiveness_score=0.0,
        )

        bullet1 = PlaybookBullet(bullet_id="b1", type="success_pattern", content="Pattern 1")
        bullet2 = PlaybookBullet(bullet_id="b2", type="failure_mode", content="Failure 1")

        playbook.categories["success_patterns"] = [bullet1]
        playbook.categories["failure_modes"] = [bullet2]

        assert len(playbook.categories) == 2
        assert len(playbook.categories["success_patterns"]) == 1

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        playbook = Playbook(
            playbook_version="1.0",
            agent_name="test",
            agent_objective="Test",
            success_criteria="Pass",
            last_updated=datetime.now(),
            total_bullets=5,
            effectiveness_score=0.75,
        )
        data = playbook.to_dict()
        playbook2 = Playbook.from_dict(data)
        assert playbook.agent_name == playbook2.agent_name
        assert playbook.total_bullets == playbook2.total_bullets


class TestHealthMetrics:
    """Tests for HealthMetrics dataclass."""

    def test_create_metrics(self):
        """Test creating health metrics."""
        metrics = HealthMetrics(
            total_bullets=100,
            avg_helpful_count=5.2,
            effectiveness_ratio=0.85,
            bullets_added_this_session=10,
            bullets_updated_this_session=5,
            bullets_pruned_this_session=2,
        )
        assert metrics.total_bullets == 100
        assert metrics.effectiveness_ratio == 0.85

    def test_roundtrip(self):
        """Test to_dict/from_dict roundtrip."""
        metrics = HealthMetrics(total_bullets=50, avg_helpful_count=3.5, effectiveness_ratio=0.9)
        data = metrics.to_dict()
        metrics2 = HealthMetrics.from_dict(data)
        assert metrics.total_bullets == metrics2.total_bullets
        assert metrics.avg_helpful_count == metrics2.avg_helpful_count
