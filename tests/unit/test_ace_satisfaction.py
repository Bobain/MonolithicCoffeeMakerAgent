"""Tests for ACE satisfaction feedback system.

This module tests the complete satisfaction feedback loop:
1. User satisfaction data structure in ExecutionTrace
2. Satisfaction collection via user_listener_ace
3. Satisfaction attachment via generator
4. Satisfaction signal extraction via reflector
5. Satisfaction weighting via curator
"""

import json
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from coffee_maker.autonomous.ace.curator import ACECurator
from coffee_maker.autonomous.ace.generator import ACEGenerator
from coffee_maker.autonomous.ace.models import (
    DeltaItem,
    Evidence,
    Execution,
    ExecutionTrace,
    ExternalObservation,
    InternalObservation,
)
from coffee_maker.autonomous.ace.reflector import ACEReflector
from coffee_maker.cli.user_listener_ace import UserListenerACE


class TestExecutionTraceSatisfaction:
    """Test satisfaction field in ExecutionTrace model."""

    def test_trace_with_satisfaction(self):
        """Test creating trace with satisfaction data."""
        satisfaction = {
            "score": 4,
            "positive_feedback": "Fast and accurate",
            "improvement_areas": "Could add more tests",
            "timestamp": "2025-10-15T12:00:00",
        }

        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Implement feature X",
            current_context="",
            user_satisfaction=satisfaction,
        )

        assert trace.user_satisfaction == satisfaction
        assert trace.user_satisfaction["score"] == 4

    def test_trace_to_dict_with_satisfaction(self):
        """Test serializing trace with satisfaction to dict."""
        satisfaction = {
            "score": 5,
            "feedback": "Excellent",
            "timestamp": "2025-10-15T12:00:00",
        }

        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test",
            current_context="",
            user_satisfaction=satisfaction,
        )

        trace_dict = trace.to_dict()
        assert "user_satisfaction" in trace_dict
        assert trace_dict["user_satisfaction"]["score"] == 5

    def test_trace_from_dict_with_satisfaction(self):
        """Test deserializing trace with satisfaction from dict."""
        satisfaction = {
            "score": 3,
            "feedback": "Neutral",
            "timestamp": "2025-10-15T12:00:00",
        }

        data = {
            "trace_id": "test_123",
            "timestamp": datetime.now().isoformat(),
            "agent_identity": {"target_agent": "code_developer"},
            "user_query": "Test",
            "current_context": "",
            "user_satisfaction": satisfaction,
        }

        trace = ExecutionTrace.from_dict(data)
        assert trace.user_satisfaction == satisfaction
        assert trace.user_satisfaction["score"] == 3

    def test_trace_to_markdown_with_satisfaction(self):
        """Test markdown representation includes satisfaction."""
        satisfaction = {
            "score": 5,
            "feedback": "Great work!",
            "timestamp": "2025-10-15T12:00:00",
        }

        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test",
            current_context="",
            user_satisfaction=satisfaction,
        )

        markdown = trace.to_markdown()
        assert "User Satisfaction" in markdown
        assert "5/5" in markdown
        assert "Great work!" in markdown


class TestUserListenerACESatisfaction:
    """Test satisfaction collection in user_listener_ace."""

    @patch("coffee_maker.cli.user_listener_ace.ClaudeCLIInterface")
    def test_collect_satisfaction_success(self, mock_claude_cli):
        """Test successful satisfaction collection."""
        # Mock Claude CLI response
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = json.dumps(
            {
                "score": 4,
                "positive_feedback": "Fast implementation",
                "improvement_areas": "More tests needed",
            }
        )
        mock_claude_cli.return_value.execute_prompt.return_value = mock_result

        ace = UserListenerACE(enabled=True)
        satisfaction = ace.collect_satisfaction(trace_id="test_123", session_summary="Implemented feature X")

        assert satisfaction["score"] == 4
        assert satisfaction["positive_feedback"] == "Fast implementation"
        assert satisfaction["improvement_areas"] == "More tests needed"
        assert "timestamp" in satisfaction

    @patch("coffee_maker.cli.user_listener_ace.ClaudeCLIInterface")
    def test_collect_satisfaction_with_code_block(self, mock_claude_cli):
        """Test parsing satisfaction from JSON code block."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = """
```json
{
  "score": 5,
  "positive_feedback": "Excellent work",
  "improvement_areas": ""
}
```
        """
        mock_claude_cli.return_value.execute_prompt.return_value = mock_result

        ace = UserListenerACE(enabled=True)
        satisfaction = ace.collect_satisfaction(trace_id="test_123", session_summary="Test")

        assert satisfaction["score"] == 5
        assert satisfaction["positive_feedback"] == "Excellent work"

    @patch("coffee_maker.cli.user_listener_ace.ClaudeCLIInterface")
    def test_collect_satisfaction_natural_language_fallback(self, mock_claude_cli):
        """Test extracting score from natural language."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = "The user gave a score: 3"
        mock_claude_cli.return_value.execute_prompt.return_value = mock_result

        ace = UserListenerACE(enabled=True)
        satisfaction = ace.collect_satisfaction(trace_id="test_123", session_summary="Test")

        assert satisfaction["score"] == 3

    def test_collect_satisfaction_disabled(self):
        """Test satisfaction collection when ACE is disabled."""
        ace = UserListenerACE(enabled=False)
        satisfaction = ace.collect_satisfaction(trace_id="test_123", session_summary="Test")

        assert satisfaction == {}


class TestGeneratorSatisfaction:
    """Test satisfaction attachment in generator."""

    def test_attach_satisfaction_success(self, tmp_path):
        """Test successfully attaching satisfaction to trace."""
        # Create a mock trace
        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test",
            current_context="",
        )

        # Create generator with temp directory
        mock_interface = Mock()
        generator = ACEGenerator(agent_interface=mock_interface)
        generator.config.trace_dir = tmp_path

        # Write trace first
        generator.trace_manager.write_trace(trace)

        # Attach satisfaction
        satisfaction = {
            "score": 4,
            "feedback": "Good",
            "timestamp": "2025-10-15T12:00:00",
        }
        generator.attach_satisfaction("test_123", satisfaction)

        # Verify trace was updated
        updated_trace = generator.trace_manager.read_trace("test_123")
        assert updated_trace.user_satisfaction == satisfaction
        assert updated_trace.user_satisfaction["score"] == 4

    def test_attach_satisfaction_invalid_score(self, tmp_path):
        """Test validation of satisfaction score."""
        mock_interface = Mock()
        generator = ACEGenerator(agent_interface=mock_interface)
        generator.config.trace_dir = tmp_path

        # Invalid score (out of range)
        with pytest.raises(ValueError, match="must be integer between 1-5"):
            generator.attach_satisfaction("test_123", {"score": 6, "feedback": ""})

    def test_attach_satisfaction_missing_score(self, tmp_path):
        """Test validation requires score field."""
        mock_interface = Mock()
        generator = ACEGenerator(agent_interface=mock_interface)
        generator.config.trace_dir = tmp_path

        with pytest.raises(ValueError, match="must contain 'score'"):
            generator.attach_satisfaction("test_123", {"feedback": "Good"})

    def test_attach_satisfaction_trace_not_found(self, tmp_path):
        """Test error when trace doesn't exist."""
        mock_interface = Mock()
        generator = ACEGenerator(agent_interface=mock_interface)
        generator.config.trace_dir = tmp_path

        with pytest.raises(FileNotFoundError):
            generator.attach_satisfaction(
                "nonexistent_trace",
                {"score": 4, "feedback": "Good"},
            )


class TestReflectorSatisfactionSignals:
    """Test satisfaction signal extraction in reflector."""

    def test_extract_high_satisfaction_signal(self, tmp_path):
        """Test extracting success pattern from high satisfaction."""
        # Create trace with high satisfaction
        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Implement feature X",
            current_context="",
            executions=[
                Execution(
                    execution_id=1,
                    external_observation=ExternalObservation(
                        files_created=["test.py"],
                        files_modified=["main.py"],
                    ),
                    internal_observation=InternalObservation(
                        reasoning_steps=["Step 1", "Step 2"],
                    ),
                    result_status="success",
                )
            ],
            user_satisfaction={
                "score": 5,
                "positive_feedback": "Excellent implementation",
                "improvement_areas": "",
                "timestamp": "2025-10-15T12:00:00",
            },
        )

        reflector = ACEReflector(agent_name="code_developer", traces_base_dir=tmp_path)
        deltas = reflector._extract_satisfaction_signals([trace])

        assert len(deltas) == 1
        delta = deltas[0]
        assert delta.insight_type == "success_pattern"
        assert delta.priority == 4
        assert delta.confidence >= 0.9  # High confidence for score=5
        assert "5/5" in delta.evidence[0].example

    def test_extract_low_satisfaction_signal(self, tmp_path):
        """Test extracting failure mode from low satisfaction."""
        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Fix bug",
            current_context="",
            executions=[
                Execution(
                    execution_id=1,
                    external_observation=ExternalObservation(),
                    internal_observation=InternalObservation(),
                    result_status="failure",
                )
            ],
            user_satisfaction={
                "score": 1,
                "positive_feedback": "",
                "improvement_areas": "Didn't solve the problem",
                "timestamp": "2025-10-15T12:00:00",
            },
        )

        reflector = ACEReflector(agent_name="code_developer", traces_base_dir=tmp_path)
        deltas = reflector._extract_satisfaction_signals([trace])

        assert len(deltas) == 1
        delta = deltas[0]
        assert delta.insight_type == "failure_mode"
        assert delta.priority == 5  # High priority to avoid
        assert delta.confidence >= 0.7  # Confidence for score=1 is 0.8 = 0.7 + (2-1)*0.1

    def test_skip_neutral_satisfaction(self, tmp_path):
        """Test that neutral satisfaction (score=3) is skipped."""
        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Test",
            current_context="",
            executions=[
                Execution(
                    execution_id=1,
                    external_observation=ExternalObservation(),
                    internal_observation=InternalObservation(),
                    result_status="success",
                )
            ],
            user_satisfaction={
                "score": 3,
                "feedback": "Okay",
                "timestamp": "2025-10-15T12:00:00",
            },
        )

        reflector = ACEReflector(agent_name="code_developer", traces_base_dir=tmp_path)
        deltas = reflector._extract_satisfaction_signals([trace])

        assert len(deltas) == 0  # Neutral satisfaction skipped


class TestCuratorSatisfactionWeighting:
    """Test satisfaction weighting in curator."""

    def test_get_satisfaction_boost_high(self):
        """Test boost for high satisfaction delta."""
        curator = ACECurator("code_developer")

        delta = DeltaItem(
            delta_id="satisfaction_test_123_12345",
            insight_type="success_pattern",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(
                    trace_id="test_123",
                    execution_id=1,
                    example="User satisfaction: 5/5",
                )
            ],
            confidence=0.8,
        )

        boost = curator._get_satisfaction_boost(delta)
        assert boost == 0.2  # High satisfaction boost

    def test_get_satisfaction_boost_low(self):
        """Test penalty for low satisfaction delta."""
        curator = ACECurator("code_developer")

        delta = DeltaItem(
            delta_id="satisfaction_test_123_12345",
            insight_type="failure_mode",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(
                    trace_id="test_123",
                    execution_id=1,
                    example="User satisfaction: 1/5",
                )
            ],
            confidence=0.8,
        )

        boost = curator._get_satisfaction_boost(delta)
        assert boost == -0.2  # Low satisfaction penalty

    def test_get_satisfaction_boost_neutral(self):
        """Test no boost for neutral satisfaction."""
        curator = ACECurator("code_developer")

        delta = DeltaItem(
            delta_id="satisfaction_test_123_12345",
            insight_type="optimization",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[
                Evidence(
                    trace_id="test_123",
                    execution_id=1,
                    example="User satisfaction: 3/5",
                )
            ],
            confidence=0.5,
        )

        boost = curator._get_satisfaction_boost(delta)
        assert boost == 0.0  # Neutral satisfaction

    def test_get_satisfaction_boost_non_satisfaction_delta(self):
        """Test no boost for regular (non-satisfaction) delta."""
        curator = ACECurator("code_developer")

        delta = DeltaItem(
            delta_id="delta_regular_12345",
            insight_type="best_practice",
            title="Test",
            description="Test",
            recommendation="Test",
            evidence=[],
            confidence=0.7,
        )

        boost = curator._get_satisfaction_boost(delta)
        assert boost == 0.0  # No satisfaction boost


class TestEndToEndSatisfactionFlow:
    """Test complete satisfaction feedback flow."""

    @patch("coffee_maker.cli.user_listener_ace.ClaudeCLIInterface")
    def test_full_satisfaction_cycle(self, mock_claude_cli, tmp_path):
        """Test complete flow from collection to curation."""
        # Setup
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = json.dumps(
            {
                "score": 5,
                "positive_feedback": "Perfect execution",
                "improvement_areas": "",
            }
        )
        mock_claude_cli.return_value.execute_prompt.return_value = mock_result

        # 1. Collect satisfaction
        ace = UserListenerACE(enabled=True)
        satisfaction = ace.collect_satisfaction(trace_id="test_123", session_summary="Implemented feature")

        assert satisfaction["score"] == 5

        # 2. Create trace and attach satisfaction
        mock_interface = Mock()
        generator = ACEGenerator(agent_interface=mock_interface)
        generator.config.trace_dir = tmp_path

        trace = ExecutionTrace(
            trace_id="test_123",
            timestamp=datetime.now(),
            agent_identity={"target_agent": "code_developer"},
            user_query="Implement feature",
            current_context="",
            executions=[
                Execution(
                    execution_id=1,
                    external_observation=ExternalObservation(files_created=["feature.py"]),
                    internal_observation=InternalObservation(reasoning_steps=["Analyzed requirements"]),
                    result_status="success",
                )
            ],
        )

        generator.trace_manager.write_trace(trace)
        generator.attach_satisfaction("test_123", satisfaction)

        # 3. Extract satisfaction signals
        reflector = ACEReflector(agent_name="code_developer", traces_base_dir=tmp_path)
        updated_trace = generator.trace_manager.read_trace("test_123")
        deltas = reflector._extract_satisfaction_signals([updated_trace])

        assert len(deltas) == 1
        assert deltas[0].insight_type == "success_pattern"
        assert deltas[0].confidence >= 0.9

        # 4. Curator applies satisfaction weighting
        curator = ACECurator("code_developer")
        boost = curator._get_satisfaction_boost(deltas[0])

        assert boost == 0.2  # High satisfaction boost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
