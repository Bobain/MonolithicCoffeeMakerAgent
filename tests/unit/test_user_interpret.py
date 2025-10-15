"""Unit tests for user_interpret agent."""

from coffee_maker.cli.user_interpret import UserInterpret


class TestUserInterpret:
    """Test user_interpret intent interpretation and agent selection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = UserInterpret()

    def test_interpret_feature_request(self):
        """Test interpretation of feature request."""
        result = self.interpreter.interpret("I need authentication in the app")

        assert result["intent"] == "add_feature"
        assert result["delegated_to"] == "code_developer"
        assert "code_developer" in result["message_to_user"]
        assert result["confidence"] > 0.7

    def test_interpret_bug_report(self):
        """Test interpretation of bug report."""
        result = self.interpreter.interpret("The tests are failing")

        assert result["intent"] == "report_bug"
        assert result["delegated_to"] == "code_developer"
        assert "code_developer" in result["message_to_user"]

    def test_interpret_documentation_request(self):
        """Test interpretation of documentation request."""
        result = self.interpreter.interpret("Update the docs for the ACE framework")

        assert result["intent"] == "update_documentation"
        assert result["delegated_to"] == "project_manager"
        assert "project_manager" in result["message_to_user"]

    def test_interpret_demo_request(self):
        """Test interpretation of demo request."""
        result = self.interpreter.interpret("Show me how the dashboard works")

        assert result["intent"] == "request_demo"
        assert result["delegated_to"] == "assistant"
        assert "assistant" in result["message_to_user"]

    def test_interpret_how_to_question(self):
        """Test interpretation of how-to question."""
        result = self.interpreter.interpret("How does the ACE framework work?")

        assert result["intent"] == "ask_how_to"
        assert result["delegated_to"] == "assistant"
        assert "assistant" in result["message_to_user"]

    def test_interpret_status_check(self):
        """Test interpretation of status check."""
        result = self.interpreter.interpret("What's the status of the project?")

        assert result["intent"] == "check_status"
        assert result["delegated_to"] == "project_manager"
        assert "project_manager" in result["message_to_user"]

    def test_interpret_roadmap_request(self):
        """Test interpretation of roadmap request."""
        result = self.interpreter.interpret("Show me the roadmap")

        assert result["intent"] == "view_roadmap"
        assert result["delegated_to"] == "project_manager"
        assert "project_manager" in result["message_to_user"]

    def test_interpret_feedback(self):
        """Test interpretation of feedback."""
        result = self.interpreter.interpret("Great work on the feature!")

        assert result["intent"] == "provide_feedback"
        assert result["delegated_to"] == "curator"
        assert "curator" in result["message_to_user"]

    def test_interpret_general_question(self):
        """Test interpretation of general question."""
        result = self.interpreter.interpret("Tell me about this project")

        assert result["intent"] == "general_question"
        assert result["delegated_to"] == "assistant"
        assert "assistant" in result["message_to_user"]

    def test_sentiment_with_frustration(self):
        """Test sentiment detection with frustration."""
        result = self.interpreter.interpret("Ugh, the tests are failing again")

        assert result["intent"] == "report_bug"
        assert result["delegated_to"] == "code_developer"
        # Should detect frustration
        assert len(result["sentiment_signals"]) > 0
        assert any(sig.sentiment == "frustration" for sig in result["sentiment_signals"])
        # Should acknowledge frustration in message
        assert "frustrated" in result["message_to_user"].lower()

    def test_sentiment_with_satisfaction(self):
        """Test sentiment detection with satisfaction."""
        result = self.interpreter.interpret("Perfect! This works great!")

        assert result["intent"] == "provide_feedback"
        # Should detect satisfaction
        assert len(result["sentiment_signals"]) > 0
        assert any(sig.sentiment == "satisfaction" for sig in result["sentiment_signals"])

    def test_confidence_calculation(self):
        """Test confidence calculation for clear vs ambiguous intents."""
        # Clear intent (feature request)
        clear_result = self.interpreter.interpret("Implement authentication feature")
        assert clear_result["confidence"] > 0.85

        # Less clear intent (general question)
        unclear_result = self.interpreter.interpret("Something about the code")
        assert unclear_result["confidence"] < clear_result["confidence"]

    def test_conversation_history_tracking(self):
        """Test conversation history is tracked."""
        assert len(self.interpreter.conversation_history) == 0

        self.interpreter.interpret("First message")
        assert len(self.interpreter.conversation_history) == 1

        self.interpreter.interpret("Second message")
        assert len(self.interpreter.conversation_history) == 2

    def test_conversation_history_limit(self):
        """Test conversation history is limited to 10 messages."""
        for i in range(15):
            self.interpreter.interpret(f"Message {i}")

        assert len(self.interpreter.conversation_history) == 10
        assert "Message 14" in self.interpreter.conversation_history
        assert "Message 4" not in self.interpreter.conversation_history

    def test_delegation_message_format(self):
        """Test delegation message has correct format."""
        result = self.interpreter.interpret("Fix the bug")

        message = result["message_to_user"]
        # Should mention the agent
        assert "code_developer" in message
        # Should mention what will be done
        assert "fix" in message.lower()
        # Should mention coming back
        assert "come back" in message.lower()

    def test_result_structure(self):
        """Test result has all required fields."""
        result = self.interpreter.interpret("Test message")

        assert "intent" in result
        assert "sentiment_signals" in result
        assert "delegated_to" in result
        assert "message_to_user" in result
        assert "confidence" in result

        # Check types
        assert isinstance(result["intent"], str)
        assert isinstance(result["sentiment_signals"], list)
        assert isinstance(result["delegated_to"], str)
        assert isinstance(result["message_to_user"], str)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
