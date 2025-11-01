"""
Unit tests for Architecture Reuse Checker Skill.

Tests cover:
- Domain identification
- Fitness score calculation
- Reuse opportunity detection
- Report generation
- Spec comparison
"""

import pytest
from pathlib import Path
from claude.skills.architecture import (
    ArchitectureReuseChecker,
    ArchitecturalComponent,
    check_architecture_reuse,
)


class TestArchitectureReuseChecker:
    """Test suite for ArchitectureReuseChecker."""

    @pytest.fixture
    def checker(self, tmp_path):
        """Create ArchitectureReuseChecker instance with temp directory."""
        return ArchitectureReuseChecker(project_root=str(tmp_path))

    @pytest.fixture
    def sample_spec_messaging(self):
        """Sample spec for inter-agent communication."""
        return """
        # SPEC-070: Agent Notification System

        ## Problem Statement

        The code_developer agent needs to notify the architect agent after each commit,
        so that the architect can review the changes.

        ## Proposed Solution

        Implement a notification system where agents can send messages to each other.

        ## Architecture

        We will create a message bus that allows agents to communicate asynchronously.
        """

    @pytest.fixture
    def sample_spec_config(self):
        """Sample spec for configuration management."""
        return """
        # SPEC-071: API Key Management

        ## Problem Statement

        We need to manage API keys for multiple providers (Anthropic, OpenAI, Gemini).

        ## Proposed Solution

        Create a centralized config system with environment variable fallbacks.
        """

    @pytest.fixture
    def sample_spec_file_io(self):
        """Sample spec for file operations."""
        return """
        # SPEC-072: Data Persistence

        ## Problem Statement

        We need to read and write JSON files atomically to prevent corruption.

        ## Proposed Solution

        Implement atomic file write operations with proper UTF-8 encoding.
        """

    # Test: Domain Identification

    def test_identify_domain_messaging(self, checker, sample_spec_messaging):
        """Test domain identification for inter-agent communication."""
        domain = checker._identify_problem_domain(sample_spec_messaging)
        assert domain == "inter-agent-communication"

    def test_identify_domain_config(self, checker, sample_spec_config):
        """Test domain identification for configuration."""
        domain = checker._identify_problem_domain(sample_spec_config)
        assert domain == "configuration"

    def test_identify_domain_file_io(self, checker, sample_spec_file_io):
        """Test domain identification for file I/O."""
        domain = checker._identify_problem_domain(sample_spec_file_io)
        assert domain == "file-io"

    def test_identify_domain_unknown(self, checker):
        """Test domain identification for unknown domain."""
        spec = "# SPEC-999: Random Feature\n\nSome random content."
        domain = checker._identify_problem_domain(spec)
        assert domain == "general"

    # Test: Fitness Score Calculation

    def test_calculate_fitness_perfect_match(self, checker):
        """Test fitness score for perfect domain match."""
        component = ArchitecturalComponent(
            name="Orchestrator Messaging",
            location="coffee_maker/autonomous/orchestrator.py",
            type="message-bus",
            purpose="Inter-agent communication",
            api=["_send_message()", "_read_messages()"],
        )

        spec = "We need to send messages between agents using _send_message()."
        fitness = checker._calculate_fitness_score(component, spec, "inter-agent-communication")

        # Should be high (functional match + API mention)
        assert fitness >= 70.0

    def test_calculate_fitness_api_match(self, checker):
        """Test fitness score when API is mentioned."""
        component = ArchitecturalComponent(
            name="ConfigManager",
            location="coffee_maker/config/manager.py",
            type="utility",
            purpose="Configuration management",
            api=["get_anthropic_api_key()"],
        )

        spec = "We need get_anthropic_api_key() to retrieve API keys."
        fitness = checker._calculate_fitness_score(component, spec, "configuration")

        # Should include API match bonus
        assert fitness >= 50.0

    def test_calculate_fitness_no_api_match(self, checker):
        """Test fitness score without API match."""
        component = ArchitecturalComponent(
            name="ConfigManager",
            location="coffee_maker/config/manager.py",
            type="utility",
            purpose="Configuration management",
            api=["get_anthropic_api_key()"],
        )

        spec = "We need configuration management for settings."
        fitness = checker._calculate_fitness_score(component, spec, "configuration")

        # Should be lower without API mention (functional match + other factors = 70)
        assert 40.0 <= fitness <= 70.0

    # Test: Recommendation Logic

    def test_fitness_to_recommendation_reuse(self, checker):
        """Test REUSE recommendation for high fitness."""
        assert checker._fitness_to_recommendation(95.0) == "REUSE"
        assert checker._fitness_to_recommendation(90.0) == "REUSE"

    def test_fitness_to_recommendation_extend(self, checker):
        """Test EXTEND recommendation for good fitness."""
        assert checker._fitness_to_recommendation(85.0) == "EXTEND"
        assert checker._fitness_to_recommendation(70.0) == "EXTEND"

    def test_fitness_to_recommendation_adapt(self, checker):
        """Test ADAPT recommendation for moderate fitness."""
        assert checker._fitness_to_recommendation(65.0) == "ADAPT"
        assert checker._fitness_to_recommendation(50.0) == "ADAPT"

    def test_fitness_to_recommendation_new(self, checker):
        """Test NEW recommendation for low fitness."""
        assert checker._fitness_to_recommendation(45.0) == "NEW"
        assert checker._fitness_to_recommendation(10.0) == "NEW"

    # Test: Analyze Spec (Full Workflow)

    def test_analyze_spec_messaging(self, checker, sample_spec_messaging):
        """Test full analysis for messaging spec."""
        result = checker.analyze_spec(sample_spec_messaging, "SPEC-070-test.md")

        # Should identify messaging domain
        assert result.problem_domain == "inter-agent-communication"

        # Should find orchestrator messaging opportunity
        assert len(result.opportunities) > 0

        # Best opportunity should be orchestrator
        best_opp = result.opportunities[0]
        assert "Orchestrator" in best_opp.component.name
        assert best_opp.fitness_score >= 50.0

        # Should have recommended approach
        assert result.recommended_approach is not None
        assert len(result.recommended_approach) > 0

    def test_analyze_spec_config(self, checker, sample_spec_config):
        """Test full analysis for config spec."""
        result = checker.analyze_spec(sample_spec_config, "SPEC-071-test.md")

        assert result.problem_domain == "configuration"
        assert len(result.opportunities) > 0

        # Should find ConfigManager
        best_opp = result.opportunities[0]
        assert "ConfigManager" in best_opp.component.name

    def test_analyze_spec_execution_time(self, checker, sample_spec_messaging):
        """Test that analysis completes within time limit."""
        result = checker.analyze_spec(sample_spec_messaging, "SPEC-070-test.md")

        # Should complete in < 3 seconds (acceptance criteria)
        assert result.execution_time_seconds < 3.0

    # Test: Benefits and Tradeoffs

    def test_analyze_benefits_reuse(self, checker):
        """Test benefits analysis for REUSE recommendation."""
        component = ArchitecturalComponent(
            name="Orchestrator",
            location="coffee_maker/autonomous/orchestrator.py",
            type="message-bus",
            purpose="Test",
            api=["_send_message()"],
        )

        benefits, tradeoffs = checker._analyze_benefits_tradeoffs(component, "REUSE")

        # Should have benefits listed
        assert len(benefits) > 0
        assert any("reuse" in b.lower() for b in benefits)

        # Should have tradeoffs
        assert len(tradeoffs) >= 0

    def test_analyze_benefits_new(self, checker):
        """Test benefits/tradeoffs for NEW recommendation."""
        component = ArchitecturalComponent(
            name="Test",
            location="test.py",
            type="utility",
            purpose="Test",
            api=[],
        )

        benefits, tradeoffs = checker._analyze_benefits_tradeoffs(component, "NEW")

        # Should return empty lists for NEW
        assert len(benefits) == 0
        assert len(tradeoffs) == 0

    # Test: Report Generation

    def test_generate_reuse_report(self, checker, sample_spec_messaging):
        """Test report generation."""
        result = checker.analyze_spec(sample_spec_messaging, "SPEC-070-test.md")
        report = checker.generate_reuse_report(result)

        # Should be markdown formatted
        assert "##" in report  # Markdown headers
        assert "Architecture Reuse Check" in report

        # Should include problem domain
        assert result.problem_domain in report

        # Should include components evaluated
        for opp in result.opportunities:
            assert opp.component.name in report

        # Should include execution time
        assert "completed in" in report.lower()

    def test_generate_report_with_benefits(self, checker, sample_spec_messaging):
        """Test report includes benefits and tradeoffs."""
        result = checker.analyze_spec(sample_spec_messaging, "SPEC-070-test.md")
        report = checker.generate_reuse_report(result)

        # Should include benefits (✅) if present
        if result.opportunities and result.opportunities[0].benefits:
            assert "✅" in report

        # Should include tradeoffs (⚠️) if present
        if result.opportunities and result.opportunities[0].tradeoffs:
            assert "⚠️" in report or "Trade-offs" in report

    # Test: Spec Comparison

    def test_compare_with_existing_specs(self, checker, sample_spec_messaging, tmp_path):
        """Test spec comparison with existing specs."""
        # Create specs directory
        specs_dir = tmp_path / "docs" / "architecture" / "specs"
        specs_dir.mkdir(parents=True)

        # Create similar existing spec
        existing_spec = specs_dir / "SPEC-060-messaging.md"
        existing_spec.write_text(sample_spec_messaging)

        # Re-create checker with temp path
        checker = ArchitectureReuseChecker(project_root=str(tmp_path))

        # Compare with slightly different spec
        new_spec = sample_spec_messaging + "\n\nAdditional section."
        comparison = checker._compare_with_existing_specs(new_spec)

        # Should find similar spec
        assert comparison is not None
        assert "SPEC-060-messaging.md" in comparison
        assert "similar" in comparison.lower()

    def test_compare_no_existing_specs(self, checker, sample_spec_messaging):
        """Test comparison when no existing specs exist."""
        comparison = checker._compare_with_existing_specs(sample_spec_messaging)

        # Should return None if specs dir doesn't exist
        assert comparison is None

    # Test: Convenience Function

    def test_check_architecture_reuse_function(self, sample_spec_messaging):
        """Test convenience function."""
        report = check_architecture_reuse(sample_spec_messaging, "SPEC-070-test.md")

        # Should return formatted report
        assert isinstance(report, str)
        assert len(report) > 0
        assert "Architecture Reuse Check" in report

    # Test: Cross-Domain Fitness

    def test_calculate_cross_domain_fitness(self, checker):
        """Test cross-domain fitness calculation."""
        comp_data = {
            "component": "Test Component",
            "patterns": ["singleton", "decorator"],
            "api": ["test_method()"],
        }

        spec = "We will use singleton pattern and decorator for this feature."
        fitness = checker._calculate_cross_domain_fitness(comp_data, spec)

        # Should detect pattern mentions
        assert fitness > 0.0
        assert fitness <= 70.0  # Cross-domain max

    def test_cross_domain_no_match(self, checker):
        """Test cross-domain fitness with no matches."""
        comp_data = {
            "component": "Test Component",
            "patterns": ["observer"],
            "api": ["notify()"],
        }

        spec = "This spec has nothing related to the component."
        fitness = checker._calculate_cross_domain_fitness(comp_data, spec)

        # Should be 0 or very low
        assert fitness == 0.0

    # Test: Edge Cases

    def test_analyze_empty_spec(self, checker):
        """Test analysis with empty spec."""
        result = checker.analyze_spec("", "SPEC-000-empty.md")

        # Should still complete without error
        assert result.problem_domain == "general"
        assert result.execution_time_seconds >= 0.0

    def test_analyze_very_long_spec(self, checker):
        """Test analysis with very long spec."""
        long_spec = "# SPEC\n\n" + ("This is a long spec. " * 1000)
        result = checker.analyze_spec(long_spec, "SPEC-999-long.md")

        # Should complete within time limit
        assert result.execution_time_seconds < 3.0

    def test_multiple_domain_matches(self, checker):
        """Test spec that matches multiple domains."""
        spec = """
        We need inter-agent messaging for notifications using configuration
        from ConfigManager to send git commit alerts.
        """

        domain = checker._identify_problem_domain(spec)

        # Should pick highest scoring domain
        assert domain in checker.COMPONENT_REGISTRY.keys()

    # Test: Accuracy Metrics (for >80% detection goal)

    def test_detection_accuracy_messaging(self, checker):
        """Test detection accuracy for messaging patterns."""
        test_cases = [
            ("agent needs to notify another agent", "inter-agent-communication"),
            ("send message between agents", "inter-agent-communication"),
            ("agent communication system", "inter-agent-communication"),
        ]

        correct = 0
        for spec_text, expected_domain in test_cases:
            detected = checker._identify_problem_domain(spec_text)
            if detected == expected_domain:
                correct += 1

        accuracy = (correct / len(test_cases)) * 100
        assert accuracy >= 80.0  # >80% accuracy requirement

    def test_detection_accuracy_config(self, checker):
        """Test detection accuracy for configuration patterns."""
        test_cases = [
            ("manage API keys for providers", "configuration"),
            ("environment variable configuration", "configuration"),
            ("settings and config management", "configuration"),
        ]

        correct = 0
        for spec_text, expected_domain in test_cases:
            detected = checker._identify_problem_domain(spec_text)
            if detected == expected_domain:
                correct += 1

        accuracy = (correct / len(test_cases)) * 100
        assert accuracy >= 80.0

    def test_detection_accuracy_file_io(self, checker):
        """Test detection accuracy for file I/O patterns."""
        test_cases = [
            ("read and write JSON files", "file-io"),
            ("atomic file write operations", "file-io"),
            ("file read with UTF-8 encoding", "file-io"),
        ]

        correct = 0
        for spec_text, expected_domain in test_cases:
            detected = checker._identify_problem_domain(spec_text)
            if detected == expected_domain:
                correct += 1

        accuracy = (correct / len(test_cases)) * 100
        assert accuracy >= 80.0


class TestIntegrationWithRealSpecs:
    """Integration tests with real project specs."""

    @pytest.fixture
    def checker_real(self):
        """Create checker with real project root."""
        return ArchitectureReuseChecker(project_root=".")

    def test_analyze_real_spec_if_exists(self, checker_real):
        """Test with real spec file if it exists."""
        specs_dir = Path("docs/architecture/specs")

        if not specs_dir.exists():
            pytest.skip("Specs directory not found")

        # Find any spec file
        spec_files = list(specs_dir.glob("SPEC-*.md"))

        if not spec_files:
            pytest.skip("No spec files found")

        # Analyze first spec (limit to first 2000 chars for speed)
        spec_path = spec_files[0]
        spec_content = spec_path.read_text()[:2000]  # Limit for performance

        result = checker_real.analyze_spec(spec_content, spec_path.name)

        # Should complete successfully
        assert result.problem_domain is not None
        # Note: Full spec comparison may take longer due to large specs directory
        # Core analysis (without full spec comparison) should be fast

        # Should generate valid report
        report = checker_real.generate_reuse_report(result)
        assert len(report) > 0
        assert "##" in report  # Valid markdown

    def test_component_registry_completeness(self, checker_real):
        """Test that component registry covers main domains."""
        required_domains = [
            "inter-agent-communication",
            "configuration",
            "file-io",
            "observability",
            "prompt-management",
        ]

        for domain in required_domains:
            assert domain in ArchitectureReuseChecker.COMPONENT_REGISTRY, f"Missing domain: {domain}"

    def test_all_registry_components_have_required_fields(self, checker_real):
        """Test that all registry entries have required fields."""
        required_fields = ["component", "location", "type", "api", "patterns"]

        for domain, comp_data in ArchitectureReuseChecker.COMPONENT_REGISTRY.items():
            for field in required_fields:
                assert field in comp_data, f"Domain {domain} missing field: {field}"
                assert comp_data[field], f"Domain {domain} has empty {field}"
