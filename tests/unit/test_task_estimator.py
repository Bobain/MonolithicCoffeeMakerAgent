"""Unit tests for TaskEstimator.

Tests the intelligent time estimation engine with various scenarios.

**US-016 Phase 3: AI-Assisted Task Breakdown**
"""

from coffee_maker.utils.task_estimator import (
    FeatureType,
    TaskComplexity,
    TaskEstimator,
    TimeEstimate,
)


class TestTaskEstimator:
    """Test suite for TaskEstimator class."""

    def setup_method(self):
        """Set up test fixture."""
        self.estimator = TaskEstimator()

    def test_estimator_initialization(self):
        """Test estimator initializes correctly."""
        assert self.estimator is not None
        assert hasattr(self.estimator, "BASE_ESTIMATES")
        assert hasattr(self.estimator, "TESTING_MULTIPLIER")

    def test_estimate_simple_low_complexity_task(self):
        """Test estimation for simple low complexity task."""
        estimate = self.estimator.estimate_task(
            task_description="Create simple model",
            complexity=TaskComplexity.LOW,
            feature_type=FeatureType.CRUD,
            requires_testing=False,
            requires_documentation=False,
            requires_security=False,
        )

        assert isinstance(estimate, TimeEstimate)
        assert estimate.total_hours == 1.5  # Base low complexity
        assert estimate.base_hours == 1.5
        assert "implementation" in estimate.breakdown
        assert estimate.confidence > 0.8  # High confidence for simple task

    def test_estimate_medium_complexity_with_testing(self):
        """Test estimation for medium complexity task with testing."""
        estimate = self.estimator.estimate_task(
            task_description="Create API endpoint",
            complexity=TaskComplexity.MEDIUM,
            feature_type=FeatureType.CRUD,
            requires_testing=True,
            requires_documentation=False,
            requires_security=False,
        )

        assert estimate.total_hours > 2.5  # Base + testing multiplier
        assert "testing" in estimate.breakdown
        assert estimate.breakdown["testing"] > 0
        # Should be around 2.5 * 1.3 = 3.25, rounded to 3.5
        assert 3.0 <= estimate.total_hours <= 3.5

    def test_estimate_high_complexity_full_requirements(self):
        """Test estimation for high complexity task with all requirements."""
        estimate = self.estimator.estimate_task(
            task_description="Create complex authentication system",
            complexity=TaskComplexity.HIGH,
            feature_type=FeatureType.SECURITY,
            requires_testing=True,
            requires_documentation=True,
            requires_security=True,
            is_integration_complex=False,
        )

        assert estimate.total_hours == 4.0  # Should be capped at maximum
        assert "testing" in estimate.breakdown
        assert "documentation" in estimate.breakdown
        assert "security" in estimate.breakdown
        assert len(estimate.risks) > 0  # Should have risks for high complexity

    def test_estimate_integration_task_with_complexity(self):
        """Test estimation for complex integration task."""
        estimate = self.estimator.estimate_task(
            task_description="Integrate with external payment API",
            complexity=TaskComplexity.HIGH,
            feature_type=FeatureType.INTEGRATION,
            requires_testing=True,
            requires_documentation=True,
            requires_security=True,
            is_integration_complex=True,
        )

        assert estimate.total_hours == 4.0  # Capped at maximum
        assert "integration_complexity" in estimate.breakdown
        assert "Third-party API" in str(estimate.risks)  # Should mention third-party risks

    def test_feature_type_adjustments(self):
        """Test that different feature types get appropriate adjustments."""
        # CRUD (baseline - no adjustment)
        crud_estimate = self.estimator.estimate_task(
            "CRUD task",
            TaskComplexity.MEDIUM,
            FeatureType.CRUD,
            requires_testing=False,
        )

        # Infrastructure (should add 0.7h)
        infra_estimate = self.estimator.estimate_task(
            "Infrastructure task",
            TaskComplexity.MEDIUM,
            FeatureType.INFRASTRUCTURE,
            requires_testing=False,
        )

        # Infrastructure should take longer
        assert infra_estimate.total_hours > crud_estimate.total_hours
        # Difference should be close to 0.7h (might be rounded)
        diff = infra_estimate.base_hours - crud_estimate.base_hours
        assert 0.5 <= diff <= 1.0  # Allow for rounding

    def test_multiplier_effects(self):
        """Test that multipliers are correctly applied."""
        # Base estimate without multipliers
        base_estimate = self.estimator.estimate_task(
            "Simple task",
            TaskComplexity.LOW,
            FeatureType.CRUD,
            requires_testing=False,
            requires_documentation=False,
            requires_security=False,
        )

        # With testing (1.3x multiplier)
        with_testing = self.estimator.estimate_task(
            "Simple task",
            TaskComplexity.LOW,
            FeatureType.CRUD,
            requires_testing=True,
            requires_documentation=False,
            requires_security=False,
        )

        # Testing should add ~30% to base time
        assert with_testing.total_hours > base_estimate.total_hours
        expected_increase = base_estimate.base_hours * 0.3  # 30% for testing
        actual_increase = with_testing.total_hours - base_estimate.total_hours
        assert abs(actual_increase - expected_increase) < 0.5  # Allow for rounding

    def test_confidence_calculation(self):
        """Test that confidence decreases with complexity and requirements."""
        # Simple task - high confidence
        simple = self.estimator.estimate_task(
            "Simple task",
            TaskComplexity.LOW,
            FeatureType.CRUD,
            requires_testing=False,
            requires_security=False,
        )

        # Complex task with security - lower confidence
        complex = self.estimator.estimate_task(
            "Complex secure task",
            TaskComplexity.HIGH,
            FeatureType.SECURITY,
            requires_testing=True,
            requires_security=True,
            is_integration_complex=True,
        )

        assert simple.confidence > complex.confidence
        assert simple.confidence >= 0.8  # High confidence for simple
        assert complex.confidence <= 0.7  # Lower confidence for complex

    def test_rounding_to_half_hour(self):
        """Test that all estimates are rounded to 0.5h."""
        # Run multiple estimates
        for complexity in [TaskComplexity.LOW, TaskComplexity.MEDIUM, TaskComplexity.HIGH]:
            estimate = self.estimator.estimate_task("Test task", complexity, FeatureType.CRUD, requires_testing=True)

            # Check total is multiple of 0.5
            assert (estimate.total_hours * 2) % 1 == 0  # Should be whole number when doubled

            # Check breakdown values are also rounded
            for hours in estimate.breakdown.values():
                assert (hours * 2) % 1 == 0

    def test_maximum_task_hours_cap(self):
        """Test that tasks are capped at MAX_TASK_HOURS."""
        # Create a very complex task that would exceed 4h
        estimate = self.estimator.estimate_task(
            "Extremely complex task with all requirements",
            TaskComplexity.HIGH,
            FeatureType.INFRASTRUCTURE,
            requires_testing=True,
            requires_documentation=True,
            requires_security=True,
            is_integration_complex=True,
        )

        assert estimate.total_hours <= self.estimator.MAX_TASK_HOURS
        assert estimate.total_hours == 4.0
        # Should have a warning in assumptions or risks about exceeding max
        combined_text = " ".join(estimate.assumptions + estimate.risks).lower()
        assert "4" in combined_text or "maximum" in combined_text

    def test_estimate_phase_empty_tasks(self):
        """Test phase estimation with no tasks."""
        phase_estimate = self.estimator.estimate_phase([], "Empty Phase")

        assert phase_estimate["total_hours"] == 0.0
        assert phase_estimate["task_count"] == 0
        assert phase_estimate["breakdown"] == {}
        assert phase_estimate["confidence"] == 0.0

    def test_estimate_phase_multiple_tasks(self):
        """Test phase estimation with multiple tasks."""
        task1 = self.estimator.estimate_task("Task 1", TaskComplexity.LOW, FeatureType.CRUD, requires_testing=True)
        task2 = self.estimator.estimate_task("Task 2", TaskComplexity.MEDIUM, FeatureType.UI, requires_testing=True)
        task3 = self.estimator.estimate_task("Task 3", TaskComplexity.LOW, FeatureType.CRUD, requires_testing=False)

        phase_estimate = self.estimator.estimate_phase([task1, task2, task3], "Phase 1")

        assert phase_estimate["task_count"] == 3
        assert phase_estimate["total_hours"] == (task1.total_hours + task2.total_hours + task3.total_hours)
        assert "implementation" in phase_estimate["breakdown"]
        assert "testing" in phase_estimate["breakdown"]
        # Confidence should be average
        expected_confidence = (task1.confidence + task2.confidence + task3.confidence) / 3
        assert abs(phase_estimate["confidence"] - expected_confidence) < 0.01

    def test_calculate_time_distribution_empty(self):
        """Test time distribution calculation with no phases."""
        distribution = self.estimator.calculate_time_distribution([])

        assert distribution["total_hours"] == 0.0
        assert distribution["total_days"] == 0.0
        assert distribution["phase_count"] == 0
        assert distribution["task_count"] == 0
        assert distribution["distribution"] == {}

    def test_calculate_time_distribution_multiple_phases(self):
        """Test time distribution across multiple phases."""
        # Create tasks for Phase 1
        phase1_tasks = [
            self.estimator.estimate_task(f"P1 Task {i}", TaskComplexity.MEDIUM, FeatureType.CRUD, requires_testing=True)
            for i in range(3)
        ]
        phase1 = self.estimator.estimate_phase(phase1_tasks, "Phase 1")

        # Create tasks for Phase 2
        phase2_tasks = [
            self.estimator.estimate_task(
                f"P2 Task {i}", TaskComplexity.HIGH, FeatureType.UI, requires_testing=True, requires_documentation=True
            )
            for i in range(2)
        ]
        phase2 = self.estimator.estimate_phase(phase2_tasks, "Phase 2")

        # Calculate distribution
        distribution = self.estimator.calculate_time_distribution([phase1, phase2])

        assert distribution["phase_count"] == 2
        assert distribution["task_count"] == 5  # 3 + 2
        assert distribution["total_hours"] == phase1["total_hours"] + phase2["total_hours"]
        assert distribution["total_days"] == round(distribution["total_hours"] / 8, 1)

        # Check that distribution contains expected activities
        assert "implementation" in distribution["distribution"]
        assert "testing" in distribution["distribution"]

        # Each percentage should be positive and reasonable
        for activity, data in distribution["distribution"].items():
            assert data["percentage"] > 0
            assert data["hours"] > 0

    def test_assumptions_tracking(self):
        """Test that assumptions are tracked correctly."""
        estimate = self.estimator.estimate_task(
            "Test task",
            TaskComplexity.MEDIUM,
            FeatureType.INTEGRATION,
            requires_testing=True,
            requires_documentation=True,
            requires_security=True,
        )

        assert len(estimate.assumptions) > 0
        # Should mention complexity, feature type, and multipliers
        assumptions_text = " ".join(estimate.assumptions).lower()
        assert "medium" in assumptions_text or "complexity" in assumptions_text
        assert "testing" in assumptions_text or "×" in assumptions_text

    def test_risks_identification(self):
        """Test that risks are identified for complex tasks."""
        # Simple task - few risks
        simple = self.estimator.estimate_task(
            "Simple task", TaskComplexity.LOW, FeatureType.CRUD, requires_testing=False
        )

        # Complex task - more risks
        complex = self.estimator.estimate_task(
            "Complex task",
            TaskComplexity.HIGH,
            FeatureType.INTEGRATION,
            requires_testing=True,
            requires_security=True,
            is_integration_complex=True,
        )

        assert len(complex.risks) >= len(simple.risks)
        # Complex task should mention specific risks
        risks_text = " ".join(complex.risks).lower()
        assert "security" in risks_text or "integration" in risks_text or "api" in risks_text

    def test_breakdown_structure(self):
        """Test that breakdown has correct structure."""
        estimate = self.estimator.estimate_task(
            "Full task",
            TaskComplexity.MEDIUM,
            FeatureType.CRUD,
            requires_testing=True,
            requires_documentation=True,
            requires_security=True,
        )

        # Check breakdown keys
        assert "implementation" in estimate.breakdown
        assert "testing" in estimate.breakdown
        assert "documentation" in estimate.breakdown
        assert "security" in estimate.breakdown

        # Check all breakdown values are positive
        for hours in estimate.breakdown.values():
            assert hours > 0

        # Check breakdown sums close to total (may differ due to rounding)
        breakdown_sum = sum(estimate.breakdown.values())
        # Allow for rounding differences
        assert abs(breakdown_sum - estimate.total_hours) < 1.0

    def test_all_feature_types(self):
        """Test estimation works for all feature types."""
        for feature_type in FeatureType:
            estimate = self.estimator.estimate_task(
                f"Test {feature_type.value} task",
                TaskComplexity.MEDIUM,
                feature_type,
                requires_testing=True,
            )

            assert estimate.total_hours > 0
            assert estimate.confidence > 0.5
            assert len(estimate.assumptions) > 0

    def test_all_complexity_levels(self):
        """Test estimation works for all complexity levels."""
        estimates = {}

        for complexity in TaskComplexity:
            estimate = self.estimator.estimate_task(
                f"Test {complexity.value} task",
                complexity,
                FeatureType.CRUD,
                requires_testing=False,
            )
            estimates[complexity] = estimate

        # Verify ordering: LOW < MEDIUM < HIGH
        assert estimates[TaskComplexity.LOW].total_hours < estimates[TaskComplexity.MEDIUM].total_hours
        assert estimates[TaskComplexity.MEDIUM].total_hours < estimates[TaskComplexity.HIGH].total_hours

        # Verify confidence ordering: LOW > MEDIUM > HIGH
        assert estimates[TaskComplexity.LOW].confidence > estimates[TaskComplexity.MEDIUM].confidence
        assert estimates[TaskComplexity.MEDIUM].confidence >= estimates[TaskComplexity.HIGH].confidence


class TestTaskEstimatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        """Set up test fixture."""
        self.estimator = TaskEstimator()

    def test_very_long_task_description(self):
        """Test with very long task description."""
        long_description = "Create " + "very " * 100 + "complex system"

        estimate = self.estimator.estimate_task(
            long_description,
            TaskComplexity.MEDIUM,
            FeatureType.CRUD,
        )

        assert estimate.total_hours > 0  # Should still work

    def test_empty_task_description(self):
        """Test with empty task description."""
        estimate = self.estimator.estimate_task(
            "",
            TaskComplexity.MEDIUM,
            FeatureType.CRUD,
        )

        assert estimate.total_hours > 0  # Should use defaults

    def test_all_requirements_disabled(self):
        """Test task with all optional requirements disabled."""
        estimate = self.estimator.estimate_task(
            "Minimal task",
            TaskComplexity.LOW,
            FeatureType.CRUD,
            requires_testing=False,
            requires_documentation=False,
            requires_security=False,
            is_integration_complex=False,
        )

        # Should only have implementation in breakdown
        assert "implementation" in estimate.breakdown
        assert "testing" not in estimate.breakdown
        assert "documentation" not in estimate.breakdown
        assert "security" not in estimate.breakdown
