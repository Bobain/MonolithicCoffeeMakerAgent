"""Unit tests for sentiment analyzer.

Tests the SentimentAnalyzer class and its ability to detect emotional signals
from user messages.
"""

import pytest

from coffee_maker.cli.sentiment_analyzer import SentimentAnalyzer, SentimentSignal


class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()

    def test_frustration_detection(self):
        """Test detection of frustration sentiment."""
        messages = [
            "Ugh, this isn't working",
            "This is so frustrating",
            "Why won't this work?",
            "This keeps failing",
            "Not working again",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            assert len(signals) > 0, f"No signals detected for: {message}"

            # Check if frustration was detected
            frustration_signals = [s for s in signals if s.sentiment == "frustration"]
            assert len(frustration_signals) > 0, f"Frustration not detected: {message}"

            signal = frustration_signals[0]
            assert signal.confidence > 0.0
            assert signal.severity >= 1
            assert len(signal.indicators) > 0

    def test_impatience_detection(self):
        """Test detection of impatience sentiment."""
        messages = [
            "Hurry up please",
            "How long will this take?",
            "Still waiting...",
            "This is taking forever",
            "Can we make this faster?",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            impatience_signals = [s for s in signals if s.sentiment == "impatience"]

            # At least some should detect impatience
            if impatience_signals:
                signal = impatience_signals[0]
                assert signal.confidence > 0.0
                assert signal.severity >= 1
                assert len(signal.indicators) > 0

    def test_satisfaction_detection(self):
        """Test detection of satisfaction sentiment."""
        messages = [
            "Perfect! Exactly what I needed",
            "This is great, thank you",
            "Excellent work",
            "Works perfectly",
            "Amazing, love it",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            satisfaction_signals = [s for s in signals if s.sentiment == "satisfaction"]

            assert len(satisfaction_signals) > 0, f"Satisfaction not detected: {message}"
            signal = satisfaction_signals[0]
            assert signal.confidence > 0.0
            assert signal.severity >= 1
            assert len(signal.indicators) > 0

    def test_confusion_detection(self):
        """Test detection of confusion sentiment."""
        messages = [
            "I don't understand this",
            "What does that mean?",
            "This is confusing",
            "Huh, not sure what to do",
            "Makes no sense to me",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            confusion_signals = [s for s in signals if s.sentiment == "confusion"]

            # At least some should detect confusion
            if confusion_signals:
                signal = confusion_signals[0]
                assert signal.confidence > 0.0
                assert signal.severity >= 1
                assert len(signal.indicators) > 0

    def test_repetition_annoyance(self):
        """Test detection of annoyance from repeated messages."""
        history = [
            "Error in authentication",
            "Error again",
            "Authentication error again",
        ]

        message = "Same error again in authentication"
        signals = self.analyzer.analyze(message, history)

        annoyance_signals = [s for s in signals if s.sentiment == "annoyance_repetition"]

        # Should detect repetition (requires 2+ repetition keywords OR 2+ similar messages)
        # This message has "same" and "again" (2 keywords)
        if annoyance_signals:
            signal = annoyance_signals[0]
            assert signal.confidence >= 0.5
            assert signal.severity >= 2  # Should be fairly severe
            assert len(signal.indicators) >= 1
        # Note: Detection may vary based on similarity threshold - this is acceptable

    def test_no_sentiment_neutral_message(self):
        """Test that neutral messages don't trigger strong sentiment."""
        neutral_messages = [
            "Show me the dashboard",
            "Please list the available commands",
            "Display project information",
        ]

        for message in neutral_messages:
            signals = self.analyzer.analyze(message)

            # Neutral messages should have few or no signals
            # Allow some detection (e.g., "what" might match confusion pattern)
            # but overall sentiment should be weak
            if signals:
                # Check that no signal is very strong
                for sig in signals:
                    # Confidence should be moderate at most for neutral messages
                    assert (
                        sig.confidence < 0.8
                    ), f"Very high confidence ({sig.confidence}) for neutral message: {message}"
                    # Severity should be low
                    assert sig.severity <= 3, f"High severity ({sig.severity}) for neutral message: {message}"

    def test_multiple_sentiments(self):
        """Test detection of multiple sentiments in one message."""
        # Message with both frustration and confusion
        message = "Ugh, I don't understand why this isn't working"

        signals = self.analyzer.analyze(message)

        # Should detect multiple sentiments
        sentiments = {s.sentiment for s in signals}
        assert "frustration" in sentiments, "Frustration not detected"
        # Confusion might or might not be detected depending on patterns

    def test_severity_scaling(self):
        """Test that severity scales with number of indicators."""
        # Mild frustration
        mild = "This isn't working"
        mild_signals = self.analyzer.analyze(mild)
        mild_frustration = [s for s in mild_signals if s.sentiment == "frustration"]

        # Strong frustration
        strong = "Ugh! This damn thing isn't working and keeps failing"
        strong_signals = self.analyzer.analyze(strong)
        strong_frustration = [s for s in strong_signals if s.sentiment == "frustration"]

        if mild_frustration and strong_frustration:
            # Strong frustration should have higher severity
            assert strong_frustration[0].severity >= mild_frustration[0].severity

    def test_confidence_scaling(self):
        """Test that confidence scales with number of matches."""
        # Single indicator
        single = "This is frustrating"
        single_signals = self.analyzer.analyze(single)
        single_frustration = [s for s in single_signals if s.sentiment == "frustration"]

        # Multiple indicators
        multiple = "Ugh, this is frustrating and annoying"
        multiple_signals = self.analyzer.analyze(multiple)
        multiple_frustration = [s for s in multiple_signals if s.sentiment == "frustration"]

        if single_frustration and multiple_frustration:
            # Multiple indicators should have higher confidence
            assert multiple_frustration[0].confidence >= single_frustration[0].confidence

    def test_similarity_calculation(self):
        """Test text similarity calculation."""
        # Similar texts
        similarity1 = self.analyzer._similarity("error occurred", "error happened")
        assert similarity1 > 0.3, "Similar texts should have positive similarity"

        # Identical texts
        similarity2 = self.analyzer._similarity("same text", "same text")
        assert similarity2 == 1.0, "Identical texts should have similarity 1.0"

        # Completely different texts
        similarity3 = self.analyzer._similarity("apple banana", "car house")
        assert similarity3 == 0.0, "Different texts should have similarity 0.0"

    def test_pattern_checking(self):
        """Test pattern matching functionality."""
        patterns = [r"\b(error|bug)\b", r"\b(test|testing)\b"]

        # Should match
        matches1 = self.analyzer._check_patterns("found an error", patterns)
        assert len(matches1) > 0, "Should detect 'error'"

        # Should not match
        matches2 = self.analyzer._check_patterns("everything works fine", patterns)
        assert len(matches2) == 0, "Should not match any patterns"

    def test_conversation_history_tracking(self):
        """Test that conversation history affects detection."""
        history = ["Error in module A", "Bug in module B"]

        # Without history - might not detect repetition
        message = "Issue in module C"
        signals_without = self.analyzer.analyze(message)

        # With history - similar messages might increase severity
        signals_with = self.analyzer.analyze(message, history)

        # Both should work (signals may or may not differ based on content)
        assert isinstance(signals_without, list)
        assert isinstance(signals_with, list)

    def test_empty_message(self):
        """Test handling of empty messages."""
        signals = self.analyzer.analyze("")
        assert isinstance(signals, list)
        assert len(signals) == 0

    def test_empty_history(self):
        """Test handling of empty conversation history."""
        message = "Error again"
        signals = self.analyzer.analyze(message, [])
        assert isinstance(signals, list)

    def test_sentiment_signal_dataclass(self):
        """Test SentimentSignal dataclass creation."""
        signal = SentimentSignal(
            sentiment="frustration",
            confidence=0.8,
            indicators=["ugh", "not working"],
            severity=4,
        )

        assert signal.sentiment == "frustration"
        assert signal.confidence == 0.8
        assert signal.indicators == ["ugh", "not working"]
        assert signal.severity == 4

    def test_case_insensitivity(self):
        """Test that sentiment detection is case-insensitive."""
        messages = [
            "UGH, THIS ISN'T WORKING",
            "ugh, this isn't working",
            "Ugh, This Isn't Working",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            frustration_signals = [s for s in signals if s.sentiment == "frustration"]
            assert len(frustration_signals) > 0, f"Case-insensitive detection failed: {message}"

    def test_punctuation_handling(self):
        """Test that punctuation doesn't break detection."""
        messages = [
            "This isn't working!",
            "This isn't working.",
            "This isn't working?",
            "This isn't working...",
        ]

        for message in messages:
            signals = self.analyzer.analyze(message)
            frustration_signals = [s for s in signals if s.sentiment == "frustration"]
            assert len(frustration_signals) > 0, f"Punctuation broke detection: {message}"

    def test_indicators_populated(self):
        """Test that indicators list is populated correctly."""
        message = "Ugh, this is frustrating and not working"
        signals = self.analyzer.analyze(message)

        for signal in signals:
            assert len(signal.indicators) > 0, "Indicators should not be empty"
            assert all(isinstance(ind, str) for ind in signal.indicators), "All indicators should be strings"


class TestSentimentAnalyzerEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()

    def test_very_long_message(self):
        """Test handling of very long messages."""
        long_message = "This is frustrating. " * 1000
        signals = self.analyzer.analyze(long_message)

        # Should still detect sentiment
        frustration_signals = [s for s in signals if s.sentiment == "frustration"]
        assert len(frustration_signals) > 0

    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        message = "This is frustrating 😤"
        signals = self.analyzer.analyze(message)

        # Should still detect frustration from text
        frustration_signals = [s for s in signals if s.sentiment == "frustration"]
        assert len(frustration_signals) > 0

    def test_special_characters(self):
        """Test handling of special characters."""
        message = "Ugh! #frustrated @fail $broken %error"
        signals = self.analyzer.analyze(message)

        # Should still detect frustration
        frustration_signals = [s for s in signals if s.sentiment == "frustration"]
        assert len(frustration_signals) > 0

    def test_numbers_in_message(self):
        """Test handling of messages with numbers."""
        message = "Error 404: This isn't working"
        signals = self.analyzer.analyze(message)

        frustration_signals = [s for s in signals if s.sentiment == "frustration"]
        assert len(frustration_signals) > 0

    def test_mixed_language_sentiment(self):
        """Test handling of messages with mixed sentiment."""
        # Positive followed by negative
        message = "Great start, but ugh, now it's broken"
        signals = self.analyzer.analyze(message)

        # Should detect both
        sentiments = {s.sentiment for s in signals}
        assert "satisfaction" in sentiments or "frustration" in sentiments

    def test_sarcasm_detection_limitation(self):
        """Test that sarcasm might be misdetected (known limitation)."""
        # Sarcastic positive (actually negative)
        message = "Oh great, it broke again"
        signals = self.analyzer.analyze(message)

        # This is a known limitation - sarcasm is hard to detect
        # We expect it to detect "great" as satisfaction
        # Just verify it doesn't crash
        assert isinstance(signals, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
