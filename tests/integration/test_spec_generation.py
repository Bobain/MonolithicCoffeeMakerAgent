"""Integration tests for end-to-end spec generation.

Tests the complete workflow from user story to technical specification.

**US-016 Phase 3: AI-Assisted Task Breakdown**
"""

import json
from unittest.mock import Mock, patch


from coffee_maker.autonomous.spec_generator import SpecGenerator, TechnicalSpec
from coffee_maker.cli.ai_service import AIService


class TestEndToEndSpecGeneration:
    """Test complete spec generation workflow."""

    @patch("coffee_maker.config.manager.ConfigManager.get_anthropic_api_key")
    @patch("coffee_maker.cli.ai_service.Anthropic")
    def test_complete_spec_generation_workflow(self, mock_anthropic, mock_get_key):
        """Test complete workflow from user story to markdown spec."""
        # Mock API key
        mock_get_key.return_value = "fake-api-key"

        # Mock AI response
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Build a CSV export feature for analytics data",
                "components": [
                    {
                        "name": "Export Service",
                        "goal": "Generate CSV files from data",
                        "tasks": [
                            {
                                "title": "Create CSV formatter",
                                "description": "Implement CSV formatting utility",
                                "deliverable": "CSVFormatter class in utils/",
                                "dependencies": [],
                                "testing": "Unit tests for CSV format validation",
                                "complexity": "low",
                            },
                            {
                                "title": "Create export endpoint",
                                "description": "REST API endpoint for CSV export",
                                "deliverable": "GET /api/export/csv endpoint",
                                "dependencies": ["Create CSV formatter"],
                                "testing": "Integration tests for endpoint",
                                "complexity": "medium",
                            },
                        ],
                        "risks": [
                            "Large datasets may cause memory issues",
                            "CSV format compatibility with Excel",
                        ],
                        "success_criteria": [
                            "CSV files generated correctly",
                            "All data fields exported",
                            "Performance acceptable for 10k rows",
                        ],
                    },
                    {
                        "name": "UI Integration",
                        "goal": "Add export button to analytics page",
                        "tasks": [
                            {
                                "title": "Create export button component",
                                "description": "React button component with download logic",
                                "deliverable": "ExportButton component",
                                "dependencies": [],
                                "testing": "Component tests",
                                "complexity": "low",
                            },
                        ],
                        "risks": ["Browser compatibility for file download"],
                        "success_criteria": ["Button triggers CSV download"],
                    },
                ],
            }
        )
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response

        # Create AI service
        ai_service = AIService(use_claude_cli=False)
        ai_service.client = mock_client

        # Generate spec
        spec_generator = SpecGenerator(ai_service)
        spec = spec_generator.generate_spec_from_user_story(
            user_story="As an analyst, I want to export analytics data as CSV so that I can analyze it in Excel",
            feature_type="analytics",
            complexity="medium",
        )

        # Verify spec structure
        assert isinstance(spec, TechnicalSpec)
        assert spec.feature_name is not None
        assert len(spec.feature_name) > 0
        assert spec.feature_type == "analytics"
        assert spec.complexity == "medium"
        assert len(spec.phases) == 2

        # Verify first phase
        phase1 = spec.phases[0]
        assert phase1.name == "Export Service"
        assert len(phase1.tasks) == 2
        assert phase1.total_hours > 0

        # Verify task estimates
        task1 = phase1.tasks[0]
        assert task1.title == "Create CSV formatter"
        assert task1.time_estimate is not None
        assert task1.time_estimate.total_hours > 0

        # Verify second phase
        phase2 = spec.phases[1]
        assert phase2.name == "UI Integration"
        assert len(phase2.tasks) == 1

        # Verify totals
        assert spec.total_hours > 0
        assert spec.total_days > 0
        assert 0.5 <= spec.confidence <= 1.0

    @patch("coffee_maker.config.manager.ConfigManager.get_anthropic_api_key")
    @patch("coffee_maker.cli.ai_service.Anthropic")
    def test_aiservice_generate_technical_spec_method(self, mock_anthropic, mock_get_key):
        """Test AIService.generate_technical_spec() integration."""
        # Mock API key
        mock_get_key.return_value = "fake-api-key"

        # Mock AI response
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Simple CRUD API for tasks",
                "components": [
                    {
                        "name": "API Layer",
                        "tasks": [
                            {
                                "title": "Create task model",
                                "description": "Task model with SQLAlchemy",
                                "deliverable": "Task model in models.py",
                                "dependencies": [],
                                "testing": "Unit tests",
                                "complexity": "low",
                            },
                            {
                                "title": "Create CRUD endpoints",
                                "description": "REST API for tasks",
                                "deliverable": "4 endpoints (GET, POST, PUT, DELETE)",
                                "dependencies": ["Create task model"],
                                "testing": "Integration tests",
                                "complexity": "medium",
                            },
                        ],
                        "risks": ["Database migration complexity"],
                        "success_criteria": ["All CRUD operations work"],
                    }
                ],
            }
        )
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response

        # Create AI service
        ai_service = AIService(use_claude_cli=False)
        ai_service.client = mock_client

        # Call generate_technical_spec
        result = ai_service.generate_technical_spec(
            user_story="Add task management CRUD API",
            feature_type="crud",
            complexity="low",
        )

        # Verify result structure
        assert "spec" in result
        assert "markdown" in result
        assert "summary" in result

        # Verify spec
        spec = result["spec"]
        assert isinstance(spec, TechnicalSpec)
        assert len(spec.phases) == 1

        # Verify markdown
        markdown = result["markdown"]
        assert isinstance(markdown, str)
        assert len(markdown) > 100

        # Verify summary
        summary = result["summary"]
        assert summary["total_hours"] > 0
        assert summary["total_days"] > 0
        assert summary["phase_count"] == 1
        assert summary["task_count"] == 2
        assert 0.5 <= summary["confidence"] <= 1.0

    def test_task_estimator_integration_with_spec_generator(self):
        """Test TaskEstimator integration in spec generation."""
        # Create mocked AI service
        mock_ai_service = Mock()
        mock_ai_service.use_claude_cli = False
        mock_ai_service.client = Mock()

        # Mock AI response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Test feature",
                "components": [
                    {
                        "name": "Test Component",
                        "tasks": [
                            {
                                "title": "Task 1",
                                "description": "Low complexity task",
                                "deliverable": "Deliverable 1",
                                "dependencies": [],
                                "testing": "Unit tests",
                                "complexity": "low",
                            },
                            {
                                "title": "Task 2",
                                "description": "High complexity task with security",
                                "deliverable": "Deliverable 2",
                                "dependencies": ["Task 1"],
                                "testing": "Integration and security tests",
                                "complexity": "high",
                            },
                        ],
                        "risks": [],
                        "success_criteria": [],
                    }
                ],
            }
        )
        mock_response.content = [mock_content]
        mock_ai_service.client.messages.create.return_value = mock_response

        # Generate spec
        spec_generator = SpecGenerator(mock_ai_service)
        spec = spec_generator.generate_spec_from_user_story(
            user_story="Test feature", feature_type="security", complexity="medium"
        )

        # Verify task estimates are different based on complexity
        task1 = spec.phases[0].tasks[0]
        task2 = spec.phases[0].tasks[1]

        assert task1.time_estimate.total_hours < task2.time_estimate.total_hours
        assert task1.time_estimate.confidence > task2.time_estimate.confidence

        # Verify phase total is sum of tasks
        expected_total = task1.time_estimate.total_hours + task2.time_estimate.total_hours
        assert spec.phases[0].total_hours == expected_total

    def test_multiple_feature_types_generate_different_estimates(self):
        """Test that different feature types produce different estimates."""
        # Create mocked AI service
        mock_ai_service = Mock()
        mock_ai_service.use_claude_cli = False
        mock_ai_service.client = Mock()

        # Mock AI response (same for both, so differences come from feature type)
        def create_mock_response():
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps(
                {
                    "summary": "Test",
                    "components": [
                        {
                            "name": "Component",
                            "tasks": [
                                {
                                    "title": "Task",
                                    "description": "Task desc",
                                    "deliverable": "Deliverable",
                                    "dependencies": [],
                                    "testing": "Tests",
                                    "complexity": "medium",
                                }
                            ],
                            "risks": [],
                            "success_criteria": [],
                        }
                    ],
                }
            )
            mock_response.content = [mock_content]
            return mock_response

        mock_ai_service.client.messages.create.return_value = create_mock_response()

        # Generate specs for different feature types
        spec_generator = SpecGenerator(mock_ai_service)

        crud_spec = spec_generator.generate_spec_from_user_story("Test", feature_type="crud", complexity="medium")

        # Reset mock
        mock_ai_service.client.messages.create.return_value = create_mock_response()

        infra_spec = spec_generator.generate_spec_from_user_story(
            "Test", feature_type="infrastructure", complexity="medium"
        )

        # Infrastructure should take longer than CRUD
        assert infra_spec.total_hours > crud_spec.total_hours


class TestSpecGenerationWithRealEstimator:
    """Test spec generation with real TaskEstimator (no mocks)."""

    def test_realistic_crud_feature_estimation(self):
        """Test realistic estimation for CRUD feature."""
        # Create mocked AI service
        mock_ai_service = Mock()
        mock_ai_service.use_claude_cli = False
        mock_ai_service.client = Mock()

        # Mock realistic CRUD analysis
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Simple user management CRUD",
                "components": [
                    {
                        "name": "Backend",
                        "tasks": [
                            {
                                "title": "Create User model",
                                "description": "SQLAlchemy model",
                                "deliverable": "User model",
                                "dependencies": [],
                                "testing": "Model tests",
                                "complexity": "low",
                            },
                            {
                                "title": "Create CRUD endpoints",
                                "description": "REST API endpoints",
                                "deliverable": "4 endpoints",
                                "dependencies": ["Create User model"],
                                "testing": "API tests",
                                "complexity": "medium",
                            },
                        ],
                        "risks": [],
                        "success_criteria": [],
                    }
                ],
            }
        )
        mock_response.content = [mock_content]
        mock_ai_service.client.messages.create.return_value = mock_response

        # Generate spec with real estimator
        spec_generator = SpecGenerator(mock_ai_service)
        spec = spec_generator.generate_spec_from_user_story(
            "User management CRUD", feature_type="crud", complexity="low"
        )

        # Verify realistic estimates (CRUD should be relatively quick)
        assert 3.0 <= spec.total_hours <= 10.0  # Reasonable for simple CRUD
        assert spec.total_days <= 1.5  # Should take less than 2 days

    def test_realistic_complex_integration_estimation(self):
        """Test realistic estimation for complex integration."""
        # Create mocked AI service
        mock_ai_service = Mock()
        mock_ai_service.use_claude_cli = False
        mock_ai_service.client = Mock()

        # Mock complex integration analysis
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = json.dumps(
            {
                "summary": "Payment gateway integration",
                "components": [
                    {
                        "name": "Integration Layer",
                        "tasks": [
                            {
                                "title": "Set up API client",
                                "description": "Configure payment gateway client",
                                "deliverable": "Client configuration",
                                "dependencies": [],
                                "testing": "Integration tests",
                                "complexity": "medium",
                            },
                            {
                                "title": "Implement payment processing",
                                "description": "Process payments securely",
                                "deliverable": "Payment processor",
                                "dependencies": ["Set up API client"],
                                "testing": "Security and integration tests",
                                "complexity": "high",
                            },
                            {
                                "title": "Handle webhooks",
                                "description": "Process payment webhooks",
                                "deliverable": "Webhook handler",
                                "dependencies": ["Implement payment processing"],
                                "testing": "Integration tests",
                                "complexity": "high",
                            },
                        ],
                        "risks": [],
                        "success_criteria": [],
                    }
                ],
            }
        )
        mock_response.content = [mock_content]
        mock_ai_service.client.messages.create.return_value = mock_response

        # Generate spec with real estimator
        spec_generator = SpecGenerator(mock_ai_service)
        spec = spec_generator.generate_spec_from_user_story(
            "Payment gateway integration",
            feature_type="integration",
            complexity="high",
        )

        # Verify realistic estimates (complex integration should take longer)
        assert spec.total_hours >= 8.0  # Should be substantial
        assert spec.total_days >= 1.0  # At least a day
        assert spec.confidence <= 0.85  # Lower confidence for complex integration
