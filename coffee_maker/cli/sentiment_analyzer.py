"""Sentiment analyzer for implicit user feedback.

Detects emotional signals from user messages to improve ACE framework learning:
- Frustration, impatience, annoyance (negative signals)
- Satisfaction, excitement (positive signals)
- Confusion (need for clarity)

This module enables the ACE framework to learn from implicit user feedback
in addition to explicit satisfaction ratings.

Example:
    >>> analyzer = SentimentAnalyzer()
    >>> signals = analyzer.analyze("Ugh, this isn't working again")
    >>> for signal in signals:
    ...     print(f"{signal.sentiment}: {signal.confidence:.2f}")
    frustration: 0.60
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SentimentSignal:
    """Detected sentiment signal from user message.

    Attributes:
        sentiment: Type of sentiment (frustration, impatience, satisfaction, etc.)
        confidence: Confidence level (0.0-1.0)
        indicators: Words/patterns that triggered detection
        severity: Severity level (1-5, where 5 is very strong)

    Example:
        >>> signal = SentimentSignal(
        ...     sentiment="frustration",
        ...     confidence=0.8,
        ...     indicators=["ugh", "not working"],
        ...     severity=4
        ... )
    """

    sentiment: str
    confidence: float
    indicators: List[str]
    severity: int


class SentimentAnalyzer:
    """Analyze user messages for implicit emotional signals.

    Detects various sentiment types from user text:
    - Negative: frustration, impatience, annoyance
    - Positive: satisfaction, excitement
    - Neutral: confusion (signals need for clarity)

    The analyzer uses pattern matching and context awareness to identify
    sentiment with confidence scores and severity levels.

    Example:
        >>> analyzer = SentimentAnalyzer()
        >>> signals = analyzer.analyze("This is perfect! Exactly what I needed")
        >>> print(signals[0].sentiment)
        satisfaction
    """

    # Frustration indicators (negative emotion)
    FRUSTRATION_PATTERNS = [
        r"\b(ugh|argh|gah|damn|damnit)\b",
        r"\b(frustrat(ed|ing)|annoying|irritating)\b",
        r"\b(why (is|does|won't|can't))\b",
        r"\b(this (doesn't|isn't|won't) work)",
        r"\b(not working|broken|failing)\b",
        r"\b(keep(s)? (failing|breaking|crashing))\b",
        r"\b(still (broken|failing|not working))\b",
    ]

    # Impatience indicators (negative emotion)
    IMPATIENCE_PATTERNS = [
        r"\b(hurry|quick(ly)?|fast(er)?|asap)\b",
        r"\b(how long|taking forever|so slow)\b",
        r"\b(still waiting|not done yet)\b",
        r"\b(come on|let's go)\b",
        r"\b(when (will|is) (this|it))\b",
    ]

    # Satisfaction indicators (positive emotion)
    SATISFACTION_PATTERNS = [
        r"\b(great|excellent|perfect|awesome|amazing)\b",
        r"\b(thank(s| you)|appreciate)\b",
        r"\b(exactly|precisely) what I (wanted|needed)\b",
        r"\b(love (it|this)|works (great|perfectly))\b",
        r"\b(good job|well done)\b",
        r"\b(nice|fantastic|wonderful)\b",
    ]

    # Confusion indicators (neutral, needs clarity)
    CONFUSION_PATTERNS = [
        r"\b(confus(ed|ing)|don't understand)\b",
        r"\b(what does (this|that) mean)\b",
        r"\b(huh|what|unclear)\b",
        r"\b(makes no sense|doesn't make sense)\b",
        r"\b(not sure (what|how|why))\b",
    ]

    # Keywords that indicate repetition/annoyance when combined with other signals
    REPETITION_KEYWORDS = ["again", "still", "another", "yet another", "same", "repeat"]

    def analyze(self, message: str, conversation_history: Optional[List[str]] = None) -> List[SentimentSignal]:
        """Analyze user message for sentiment signals.

        Performs pattern matching against known sentiment indicators and
        considers conversation history for context-aware detection.

        Args:
            message: User's message to analyze
            conversation_history: Recent messages for context (last 5-10)
                                Used to detect repetition and annoyance patterns

        Returns:
            List of detected sentiment signals, sorted by severity (highest first)

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> # Simple frustration
            >>> signals = analyzer.analyze("This isn't working")
            >>> signals[0].sentiment
            'frustration'

            >>> # With repetition context
            >>> history = ["Error again", "Still broken"]
            >>> signals = analyzer.analyze("Same error", history)
            >>> len([s for s in signals if s.sentiment == "annoyance_repetition"])
            1
        """
        signals = []
        message_lower = message.lower()

        # Check frustration
        frustration_matches = self._check_patterns(message_lower, self.FRUSTRATION_PATTERNS)
        if frustration_matches:
            signals.append(
                SentimentSignal(
                    sentiment="frustration",
                    confidence=min(1.0, len(frustration_matches) * 0.3 + 0.3),
                    indicators=frustration_matches,
                    severity=min(5, len(frustration_matches) + 2),
                )
            )

        # Check impatience
        impatience_matches = self._check_patterns(message_lower, self.IMPATIENCE_PATTERNS)
        if impatience_matches:
            signals.append(
                SentimentSignal(
                    sentiment="impatience",
                    confidence=min(1.0, len(impatience_matches) * 0.4 + 0.3),
                    indicators=impatience_matches,
                    severity=min(5, len(impatience_matches) + 1),
                )
            )

        # Check satisfaction
        satisfaction_matches = self._check_patterns(message_lower, self.SATISFACTION_PATTERNS)
        if satisfaction_matches:
            signals.append(
                SentimentSignal(
                    sentiment="satisfaction",
                    confidence=min(1.0, len(satisfaction_matches) * 0.3 + 0.4),
                    indicators=satisfaction_matches,
                    severity=min(5, len(satisfaction_matches) + 2),
                )
            )

        # Check confusion
        confusion_matches = self._check_patterns(message_lower, self.CONFUSION_PATTERNS)
        if confusion_matches:
            signals.append(
                SentimentSignal(
                    sentiment="confusion",
                    confidence=min(1.0, len(confusion_matches) * 0.4 + 0.3),
                    indicators=confusion_matches,
                    severity=min(5, len(confusion_matches) + 1),
                )
            )

        # Check for annoyance from repetition (requires history)
        if conversation_history:
            repetition_signal = self._detect_repetition_annoyance(message_lower, conversation_history)
            if repetition_signal:
                signals.append(repetition_signal)

        # Sort by severity (highest first)
        signals.sort(key=lambda s: s.severity, reverse=True)

        return signals

    def _check_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Check text against regex patterns and return matched phrases.

        Args:
            text: Text to check (lowercase)
            patterns: List of regex patterns

        Returns:
            List of matched phrases

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> matches = analyzer._check_patterns(
            ...     "this isn't working",
            ...     [r"\b(not working|broken)\b", r"\b(this (doesn't|isn't))\b"]
            ... )
            >>> "this isn't" in matches
            True
        """
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            # Flatten tuples from group matches
            for match in found:
                if isinstance(match, tuple):
                    # Use the full match (first group typically)
                    matches.append(match[0] if match[0] else str(match))
                else:
                    matches.append(match)
        return matches

    def _detect_repetition_annoyance(self, message: str, history: List[str]) -> Optional[SentimentSignal]:
        """Detect annoyance from repeated issues.

        Looks for:
        1. Repetition keywords in current message (again, still, etc.)
        2. Similar messages in conversation history

        Args:
            message: Current message (lowercase)
            history: Previous messages

        Returns:
            SentimentSignal if repetition detected, None otherwise

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> history = ["Error occurred", "Same error", "Error again"]
            >>> signal = analyzer._detect_repetition_annoyance("Error again", history)
            >>> signal.sentiment
            'annoyance_repetition'
        """
        # Count repetition keywords in current message
        repetition_count = sum(1 for kw in self.REPETITION_KEYWORDS if kw in message)

        # Count similar messages in history
        similar_count = sum(1 for h in history if self._similarity(message, h.lower()) > 0.6)

        # Detect if user is mentioning same issue repeatedly
        if repetition_count >= 2 or similar_count >= 2:
            total_signals = repetition_count + similar_count
            return SentimentSignal(
                sentiment="annoyance_repetition",
                confidence=min(0.9, 0.5 + total_signals * 0.1),
                indicators=[
                    f"repetition keywords: {repetition_count}",
                    f"similar messages: {similar_count}",
                ],
                severity=min(5, total_signals),
            )

        return None

    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate simple Jaccard similarity between two texts.

        Uses word-level comparison with Jaccard index:
        similarity = |intersection| / |union|

        Args:
            text1: First text (lowercase)
            text2: Second text (lowercase)

        Returns:
            Similarity score (0.0-1.0)

        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> analyzer._similarity("error occurred", "error happened")
            0.5  # "error" is shared, "occurred" and "happened" differ
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
