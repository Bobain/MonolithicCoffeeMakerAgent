"""Tests for the standardized error handler module."""

import logging
import pytest
from coffee_maker.cli.error_handler import (
    handle_error,
    handle_warning,
    handle_info,
    handle_success,
    ErrorContext,
    ErrorSeverity,
)


class TestErrorHandler:
    """Tests for error handling functions."""

    def test_handle_error_format(self, capsys):
        """Test error message format."""
        result = handle_error("view", "File not found")

        captured = capsys.readouterr()
        assert "❌ Error in 'view': File not found" in captured.err
        assert result == 1

    def test_handle_error_with_exception(self, capsys, caplog):
        """Test error with exception logging."""
        caplog.set_level(logging.ERROR)
        exception = ValueError("Invalid input")
        result = handle_error(
            "status",
            "Invalid priority",
            exception=exception,
        )

        captured = capsys.readouterr()
        assert "❌ Error in 'status': Invalid priority" in captured.err
        assert result == 1
        assert "Command 'status' failed: Invalid priority" in caplog.text

    def test_handle_error_with_context(self, caplog):
        """Test error with context logging."""
        caplog.set_level(logging.DEBUG)
        context = {"args": {"priority": 5}}
        handle_error("view", "Error", context=context)

        assert "Error context" in caplog.text

    def test_handle_warning_format(self, capsys):
        """Test warning message format."""
        result = handle_warning("metrics", "Some data missing")

        captured = capsys.readouterr()
        assert "⚠️  Warning in 'metrics': Some data missing" in captured.err
        assert result == 0  # Warnings don't fail

    def test_handle_warning_logging(self, caplog):
        """Test warning logging."""
        caplog.set_level(logging.WARNING)
        handle_warning("metrics", "Some data missing")

        assert "Command 'metrics': Some data missing" in caplog.text

    def test_handle_info_format(self, capsys):
        """Test info message format."""
        result = handle_info("view", "Showing roadmap")

        captured = capsys.readouterr()
        assert "ℹ️  Info: Showing roadmap" in captured.out
        assert result == 0

    def test_handle_info_logging(self, caplog):
        """Test info logging."""
        caplog.set_level(logging.INFO)
        handle_info("view", "Showing roadmap")

        assert "Command 'view': Showing roadmap" in caplog.text

    def test_handle_success_format(self, capsys):
        """Test success message format."""
        result = handle_success("respond", "Notification approved")

        captured = capsys.readouterr()
        assert "✅ Success: Notification approved" in captured.out
        assert result == 0

    def test_handle_success_logging(self, caplog):
        """Test success logging."""
        caplog.set_level(logging.INFO)
        handle_success("respond", "Notification approved")

        assert "Command 'respond': Notification approved" in caplog.text

    def test_error_exit_program(self):
        """Test error exit_program flag."""
        with pytest.raises(SystemExit) as exc_info:
            handle_error("view", "Fatal error", exit_program=True)
        assert exc_info.value.code == 1

    def test_error_context_dataclass(self):
        """Test ErrorContext dataclass."""
        context = ErrorContext(
            command="view",
            message="Test error",
            severity=ErrorSeverity.ERROR,
        )
        assert context.command == "view"
        assert context.message == "Test error"
        assert context.severity == ErrorSeverity.ERROR
        assert context.exit_code == 1

    def test_error_severity_enum(self):
        """Test ErrorSeverity enum."""
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.SUCCESS.value == "success"

    def test_multiple_errors_sequence(self, capsys, caplog):
        """Test handling multiple errors in sequence."""
        caplog.set_level(logging.ERROR)

        # First error
        handle_error("cmd1", "Error 1")
        captured1 = capsys.readouterr()
        assert "❌ Error in 'cmd1': Error 1" in captured1.err

        # Second error
        handle_error("cmd2", "Error 2")
        captured2 = capsys.readouterr()
        assert "❌ Error in 'cmd2': Error 2" in captured2.err

        # Both should be logged
        assert "Command 'cmd1' failed: Error 1" in caplog.text
        assert "Command 'cmd2' failed: Error 2" in caplog.text

    def test_context_with_dict_args(self):
        """Test context with dictionary arguments."""
        context = {"priority": 5, "command": "view", "user": "test_user"}
        result = handle_error("view", "Test", context=context)
        assert result == 1
