"""Tests for ROI Calculator."""

from claude.skills.refactoring_analysis.proactive_refactoring_analysis import (
    ROICalculator,
)


class TestROICalculator:
    """Test ROI calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ROICalculator()

    def test_very_high_roi(self):
        """Test VERY HIGH ROI calculation (>200%)."""
        result = self.calculator.calculate_roi(effort_hours=3, time_saved_hours=15)

        assert result["roi_percentage"] == 400.0
        assert result["roi_category"] == "VERY HIGH"
        assert result["break_even_months"] == 0.2

    def test_high_roi(self):
        """Test HIGH ROI calculation (100-200%)."""
        result = self.calculator.calculate_roi(effort_hours=10, time_saved_hours=20)

        assert result["roi_percentage"] == 100.0
        assert result["roi_category"] == "HIGH"
        assert result["break_even_months"] == 0.5

    def test_medium_roi(self):
        """Test MEDIUM ROI calculation (50-100%)."""
        result = self.calculator.calculate_roi(effort_hours=10, time_saved_hours=15)

        assert result["roi_percentage"] == 50.0
        assert result["roi_category"] == "MEDIUM"
        assert result["break_even_months"] == 0.7

    def test_low_roi(self):
        """Test LOW ROI calculation (<50%)."""
        result = self.calculator.calculate_roi(effort_hours=10, time_saved_hours=11)

        assert result["roi_percentage"] == 10.0
        assert result["roi_category"] == "LOW"
        assert result["break_even_months"] == 0.9

    def test_negative_roi(self):
        """Test negative ROI (effort > time saved)."""
        result = self.calculator.calculate_roi(effort_hours=10, time_saved_hours=5)

        assert result["roi_percentage"] == -50.0
        assert result["roi_category"] == "LOW"
        assert result["break_even_months"] == 2.0

    def test_zero_effort(self):
        """Test with zero effort (edge case)."""
        result = self.calculator.calculate_roi(effort_hours=0, time_saved_hours=10)

        assert result["roi_percentage"] == 0
        assert result["roi_category"] == "UNKNOWN"
        assert result["break_even_months"] == 0

    def test_zero_time_saved(self):
        """Test with zero time saved."""
        result = self.calculator.calculate_roi(effort_hours=10, time_saved_hours=0)

        assert result["roi_percentage"] == -100.0
        assert result["roi_category"] == "LOW"
        assert result["break_even_months"] == 100.0  # Very long break-even
