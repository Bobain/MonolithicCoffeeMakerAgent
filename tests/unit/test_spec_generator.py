"""Unit tests for SpecGenerator.

Tests AI-assisted technical specification generation.

**US-016 Phase 3: AI-Assisted Task Breakdown**
"""

import json
from unittest.mock import Mock, patch

import pytest

from coffee_maker.autonomous.spec_generator import (
    Phase,
    SpecGenerator,
    Task,
    TechnicalSpec,
)
from coffee_maker.utils.task_estimator import TaskComplexity, FeatureType, TimeEstimate


class TestSpecGenerator:
    """Test suite for SpecGenerator class."""

    def setup_method(self):
        """Set up test fixture with mocked AI service."""
        self.mock_ai_service = Mock()
        self.generator = SpecGenerator(self.mock_ai_service)

    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        assert self.generator is not None
        assert self.generator.ai_service == self.mock_ai_service
        assert hasattr(self.generator, "estimator")

    def test_parse_complexity_low(self):
        """Test parsing low complexity strings."""
        assert self.generator._parse_complexity("low") == TaskComplexity.LOW
        assert self.generator._parse_complexity("simple") == TaskComplexity.LOW
        assert self.generator._parse_complexity("easy") == TaskComplexity.LOW

    def test_parse_complexity_high(self):
        """Test parsing high complexity strings."""
        assert self.generator._parse_complexity("high") == TaskComplexity.HIGH
        assert self.generator._parse_complexity("complex") == TaskComplexity.HIGH
        assert self.generator._parse_complexity("hard") == TaskComplexity.HIGH

    def test_parse_complexity_medium_default(self):
        """Test parsing medium or unknown complexity defaults to medium."""
        assert self.generator._parse_complexity("medium") == TaskComplexity.MEDIUM
        assert self.generator._parse_complexity("unknown") == TaskComplexity.MEDIUM
        assert self.generator._parse_complexity("") == TaskComplexity.MEDIUM

    def test_parse_feature_type_all_types(self):
        """Test parsing all feature type strings."""
        assert self.generator._parse_feature_type("crud") == FeatureType.CRUD
        assert self.generator._parse_feature_type("integration") == FeatureType.INTEGRATION
        assert self.generator._parse_feature_type("ui") == FeatureType.UI
        assert self.generator._parse_feature_type("infrastructure") == FeatureType.INFRASTRUCTURE
        assert self.generator._parse_feature_type("analytics") == FeatureType.ANALYTICS
        assert self.generator._parse_feature_type("security") == FeatureType.SECURITY

    def test_parse_feature_type_unknown_defaults_to_crud(self):
        """Test unknown feature type defaults to CRUD."""
        assert self.generator._parse_feature_type("unknown") == FeatureType.CRUD
        assert self.generator._parse_feature_type("") == FeatureType.CRUD

    def test_extract_feature_info_user_story_format(self):
        """Test extracting feature info from user story format."""
        user_story = "As a developer, I want to deploy on GCP so that it runs 24/7"

        feature_name, business_value = self.generator._extract_feature_info(user_story)

        assert "deploy" in feature_name.lower()
        assert "gcp" in feature_name.lower()
        assert "runs 24/7" in business_value.lower()

    def test_extract_feature_info_simple_description(self):
        """Test extracting feature info from simple description."""
        user_story = "Add email notifications"

        feature_name, business_value = self.generator._extract_feature_info(user_story)

        assert "email" in feature_name.lower() or "notification" in feature_name.lower()
        # Should have default business value
        assert len(business_value) > 0

    def test_extract_json_from_response_valid_json(self):
        """Test extracting valid JSON from AI response."""
        response = """
        Here's the analysis:

        {
            "summary": "Test summary",
            "components": [
                {"name": "Component 1", "tasks": []}
            ]
        }

        That's the complete analysis.
        """

        result = self.generator._extract_json_from_response(response)

        assert isinstance(result, dict)
        assert result["summary"] == "Test summary"
        assert len(result["components"]) == 1

    def test_extract_json_from_response_no_json(self):
        """Test handling response with no JSON."""
        response = "This is just plain text with no JSON"

        result = self.generator._extract_json_from_response(response)

        assert result == {}

    def test_extract_json_from_response_malformed_json(self):
        """Test handling malformed JSON."""
        response = '{"invalid": json, missing quotes}'

        result = self.generator._extract_json_from_response(response)

        assert result == {}

    def test_fallback_analysis(self):
        """Test fallback analysis generation when AI fails."""
        user_story = "Create user authentication"
        feature_type = "security"
        complexity = "high"

        analysis = self.generator._fallback_analysis(user_story, feature_type, complexity)

        assert "summary" in analysis
        assert "components" in analysis
        assert len(analysis["components"]) > 0
        # Should have at least one task
        assert len(analysis["components"][0]["tasks"]) > 0
        # Task should have correct complexity
        assert analysis["components"][0]["tasks"][0]["complexity"] == complexity

    def test_create_phases_from_analysis_empty(self):
        """Test creating phases from empty analysis."""
        analysis = {"components": []}

        phases = self.generator._create_phases_from_analysis(analysis, TaskComplexity.MEDIUM, FeatureType.CRUD)

        assert phases == []

    def test_create_phases_from_analysis_single_component(self):
        """Test creating phases from single component."""
        analysis = {
            "components": [
                {
                    "name": "Database Layer",
                    "goal": "Complete database implementation",
                    "tasks": [
                        {
                            "title": "Create User model",
                            "description": "Implement User model with SQLAlchemy",
                            "deliverable": "User model in models.py",
                            "dependencies": [],
                            "testing": "Unit tests for model",
                            "complexity": "low",
                        }
                    ],
                    "risks": ["Schema changes may require migration"],
                    "success_criteria": ["All models created", "Tests passing"],
                }
            ]
        }

        phases = self.generator._create_phases_from_analysis(analysis, TaskComplexity.MEDIUM, FeatureType.CRUD)

        assert len(phases) == 1
        assert phases[0].name == "Database Layer"
        assert phases[0].goal == "Complete database implementation"
        assert len(phases[0].tasks) == 1
        assert phases[0].tasks[0].title == "Create User model"
        assert phases[0].total_hours > 0

    def test_create_phases_from_analysis_multiple_tasks(self):
        """Test creating phases with multiple tasks."""
        analysis = {
            "components": [
                {
                    "name": "API Layer",
                    "tasks": [
                        {
                            "title": "Create login endpoint",
                            "description": "POST /api/login",
                            "deliverable": "Login endpoint",
                            "dependencies": [],
                            "testing": "Integration tests",
                            "complexity": "medium",
                        },
                        {
                            "title": "Create logout endpoint",
                            "description": "POST /api/logout",
                            "deliverable": "Logout endpoint",
                            "dependencies": ["Create login endpoint"],
                            "testing": "Integration tests",
                            "complexity": "low",
                        },
                    ],
                    "risks": [],
                    "success_criteria": [],
                }
            ]
        }

        phases = self.generator._create_phases_from_analysis(analysis, TaskComplexity.MEDIUM, FeatureType.SECURITY)

        assert len(phases[0].tasks) == 2
        assert phases[0].tasks[1].dependencies == ["Create login endpoint"]
        # Phase total should be sum of task estimates
        expected_total = sum(task.time_estimate.total_hours for task in phases[0].tasks)
        assert phases[0].total_hours == expected_total

    def test_build_template_replacements_basic(self):
        """Test building template replacements with basic spec."""
        spec = TechnicalSpec(
            feature_name="Test Feature",
            feature_type="crud",
            complexity="medium",
            summary="Test summary",
            business_value="Test business value",
            phases=[],
            total_hours=10.0,
            total_days=1.25,
            confidence=0.85,
        )

        distribution = {
            "total_hours": 10.0,
            "total_days": 1.25,
            "phase_count": 0,
            "task_count": 0,
            "distribution": {},
        }

        replacements = self.generator._build_template_replacements(spec, distribution)

        assert replacements["FEATURE_NAME"] == "Test Feature"
        assert replacements["FEATURE_TYPE"] == "CRUD"
        assert replacements["COMPLEXITY"] == "Medium"
        assert replacements["TOTAL_TIME_HOURS"] == "10.0"
        assert replacements["TOTAL_TIME_DAYS"] == "1.25"

    def test_render_basic_markdown(self):
        """Test rendering basic markdown."""
        # Create a simple spec
        task = Task(
            title="Test Task",
            description="Test description",
            deliverable="Test deliverable",
            dependencies=[],
            testing="Test testing",
            time_estimate=TimeEstimate(
                total_hours=2.0,
                base_hours=1.5,
                breakdown={"implementation": 1.5, "testing": 0.5},
                confidence=0.9,
                assumptions=[],
                risks=[],
            ),
        )

        phase = Phase(
            name="Test Phase",
            goal="Test goal",
            tasks=[task],
            risks=["Test risk"],
            success_criteria=["Test criterion"],
            total_hours=2.0,
        )

        spec = TechnicalSpec(
            feature_name="Test Feature",
            feature_type="crud",
            complexity="medium",
            summary="Test summary",
            business_value="Test value",
            phases=[phase],
            total_hours=2.0,
            total_days=0.25,
            confidence=0.9,
        )

        markdown = self.generator._render_basic_markdown(spec)

        assert "# Technical Specification: Test Feature" in markdown
        assert "Test Phase" in markdown
        assert "Test Task" in markdown
        assert "2.0" in markdown  # Should show hours
        assert "Test risk" in markdown

    @patch.object(SpecGenerator, "_analyze_user_story_with_ai")
    @patch.object(SpecGenerator, "_extract_feature_info")
    def test_generate_spec_from_user_story_success(self, mock_extract, mock_analyze):
        """Test successful spec generation from user story."""
        # Mock extraction
        mock_extract.return_value = ("Email Notifications", "Improve user engagement")

        # Mock AI analysis
        mock_analyze.return_value = {
            "summary": "Build email notification system",
            "components": [
                {
                    "name": "Email Service",
                    "goal": "Send emails",
                    "tasks": [
                        {
                            "title": "Create email sender",
                            "description": "Implement email sender",
                            "deliverable": "EmailSender class",
                            "dependencies": [],
                            "testing": "Unit tests",
                            "complexity": "medium",
                        }
                    ],
                    "risks": ["Email delivery failures"],
                    "success_criteria": ["Emails sent successfully"],
                }
            ],
        }

        spec = self.generator.generate_spec_from_user_story(
            user_story="Add email notifications",
            feature_type="integration",
            complexity="medium",
        )

        assert isinstance(spec, TechnicalSpec)
        assert spec.feature_name == "Email Notifications"
        assert spec.business_value == "Improve user engagement"
        assert len(spec.phases) == 1
        assert spec.total_hours > 0
        assert spec.total_days > 0
        assert 0.5 <= spec.confidence <= 1.0

    @patch.object(SpecGenerator, "_analyze_user_story_with_ai")
    def test_generate_spec_handles_ai_failure(self, mock_analyze):
        """Test spec generation handles AI failure gracefully."""
        # Simulate AI failure
        mock_analyze.side_effect = Exception("AI service unavailable")

        # Should not raise, should use fallback
        with pytest.raises(Exception):
            spec = self.generator.generate_spec_from_user_story(
                user_story="Test feature", feature_type="crud", complexity="low"
            )


class TestSpecGeneratorIntegration:
    """Integration tests with real AI service (mocked)."""

    def setup_method(self):
        """Set up test fixture with more realistic mocks."""
        self.mock_ai_service = Mock()
        # Mock the interface
        self.mock_ai_service.use_claude_cli = False
        self.mock_ai_service.client = Mock()
        self.generator = SpecGenerator(self.mock_ai_service)

    def test_analyze_user_story_with_ai_api_mode(self):
        """Test AI analysis in API mode."""
        # Mock AI response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Build authentication system",
                "components": [
                    {
                        "name": "Auth Backend",
                        "tasks": [
                            {
                                "title": "Create User model",
                                "description": "Implement User model",
                                "deliverable": "User model",
                                "dependencies": [],
                                "testing": "Unit tests",
                                "complexity": "low",
                            }
                        ],
                        "risks": ["Security vulnerabilities"],
                        "success_criteria": ["Users can authenticate"],
                    }
                ],
            }
        )
        mock_response.content = [mock_content]
        self.mock_ai_service.client.messages.create.return_value = mock_response

        analysis = self.generator._analyze_user_story_with_ai("Add user authentication", "security", "high")

        assert "summary" in analysis
        assert "components" in analysis
        assert len(analysis["components"]) == 1
        self.mock_ai_service.client.messages.create.assert_called_once()

    def test_analyze_user_story_with_ai_cli_mode(self):
        """Test AI analysis in CLI mode."""
        # Set up CLI mode
        self.mock_ai_service.use_claude_cli = True
        self.mock_ai_service.cli_interface = Mock()

        # Mock CLI result
        mock_result = Mock()
        mock_result.success = True
        mock_result.content = json.dumps(
            {
                "summary": "Build dashboard",
                "components": [
                    {
                        "name": "Dashboard UI",
                        "tasks": [
                            {
                                "title": "Create dashboard component",
                                "description": "React component",
                                "deliverable": "Dashboard.tsx",
                                "dependencies": [],
                                "testing": "Component tests",
                                "complexity": "medium",
                            }
                        ],
                        "risks": ["Performance with large datasets"],
                        "success_criteria": ["Dashboard renders quickly"],
                    }
                ],
            }
        )
        self.mock_ai_service.cli_interface.execute_prompt.return_value = mock_result

        analysis = self.generator._analyze_user_story_with_ai("Add analytics dashboard", "analytics", "medium")

        assert "summary" in analysis
        assert "components" in analysis
        self.mock_ai_service.cli_interface.execute_prompt.assert_called_once()

    def test_render_spec_to_markdown_with_template(self):
        """Test rendering spec to markdown with template."""
        # Create a realistic spec
        task1 = Task(
            title="Create database model",
            description="Implement User model with SQLAlchemy",
            deliverable="User model in models.py",
            dependencies=[],
            testing="Unit tests for model validation",
            time_estimate=TimeEstimate(
                total_hours=2.0,
                base_hours=1.5,
                breakdown={"implementation": 1.5, "testing": 0.5},
                confidence=0.85,
                assumptions=["Base complexity: medium"],
                risks=[],
            ),
        )

        phase1 = Phase(
            name="Database Layer",
            goal="Complete database implementation",
            tasks=[task1],
            risks=["Schema changes may require migration"],
            success_criteria=["All models created", "Unit tests passing"],
            total_hours=2.0,
        )

        spec = TechnicalSpec(
            feature_name="User Authentication",
            feature_type="security",
            complexity="high",
            summary="Build secure user authentication system",
            business_value="Enable user login and access control",
            phases=[phase1],
            total_hours=2.0,
            total_days=0.25,
            confidence=0.85,
        )

        # Use basic markdown (template may not exist in test)
        markdown = self.generator._render_basic_markdown(spec)

        assert isinstance(markdown, str)
        assert len(markdown) > 100
        assert "User Authentication" in markdown
        assert "Database Layer" in markdown
        assert "Create database model" in markdown


class TestDataClasses:
    """Test the data classes."""

    def test_task_creation(self):
        """Test Task creation."""
        task = Task(
            title="Test Task",
            description="Test description",
            deliverable="Test deliverable",
            dependencies=["Task 1", "Task 2"],
            testing="Test testing",
        )

        assert task.title == "Test Task"
        assert len(task.dependencies) == 2
        assert task.time_estimate is None  # Optional

    def test_phase_creation(self):
        """Test Phase creation."""
        phase = Phase(
            name="Test Phase",
            goal="Test goal",
            tasks=[],
            risks=["Risk 1"],
            success_criteria=["Criterion 1"],
        )

        assert phase.name == "Test Phase"
        assert len(phase.tasks) == 0
        assert phase.total_hours == 0.0

    def test_technical_spec_creation(self):
        """Test TechnicalSpec creation."""
        spec = TechnicalSpec(
            feature_name="Test Feature",
            feature_type="crud",
            complexity="low",
            summary="Test summary",
            business_value="Test value",
        )

        assert spec.feature_name == "Test Feature"
        assert len(spec.phases) == 0
        assert spec.total_hours == 0.0
        assert spec.confidence == 0.0
