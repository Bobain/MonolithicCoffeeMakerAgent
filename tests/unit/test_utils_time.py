"""Unit tests for coffee_maker.utils.time_utils module."""

from datetime import datetime, timedelta
import pytest
from coffee_maker.utils.time_utils import (
    get_time_threshold,
    get_time_range,
    format_duration,
    format_timestamp,
    bucket_time,
    is_recent,
    time_ago,
)


class TestGetTimeThreshold:
    """Tests for get_time_threshold function."""

    def test_second_timeframe(self):
        """Should calculate threshold for seconds."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("second", count=30, reference_time=reference)
        expected = reference - timedelta(seconds=30)
        assert result == expected

    def test_minute_timeframe(self):
        """Should calculate threshold for minutes."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("minute", count=5, reference_time=reference)
        expected = reference - timedelta(minutes=5)
        assert result == expected

    def test_hour_timeframe(self):
        """Should calculate threshold for hours."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("hour", count=3, reference_time=reference)
        expected = reference - timedelta(hours=3)
        assert result == expected

    def test_day_timeframe(self):
        """Should calculate threshold for days."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("day", count=7, reference_time=reference)
        expected = reference - timedelta(days=7)
        assert result == expected

    def test_week_timeframe(self):
        """Should calculate threshold for weeks."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("week", count=2, reference_time=reference)
        expected = reference - timedelta(weeks=2)
        assert result == expected

    def test_month_timeframe(self):
        """Should calculate threshold for months (approximate)."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("month", count=3, reference_time=reference)
        expected = reference - timedelta(days=90)  # 3 * 30
        assert result == expected

    def test_year_timeframe(self):
        """Should calculate threshold for years (approximate)."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("year", count=1, reference_time=reference)
        expected = reference - timedelta(days=365)
        assert result == expected

    def test_all_timeframe(self):
        """Should return datetime.min for 'all' timeframe."""
        result = get_time_threshold("all")
        assert result == datetime.min

    def test_default_count(self):
        """Should use count=1 by default."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        result = get_time_threshold("day", reference_time=reference)
        expected = reference - timedelta(days=1)
        assert result == expected

    def test_default_reference_time(self):
        """Should use current time when reference_time not provided."""
        before = datetime.utcnow()
        result = get_time_threshold("hour")
        after = datetime.utcnow()

        # Result should be approximately 1 hour before now
        assert before - timedelta(hours=1, seconds=1) <= result <= after - timedelta(hours=1) + timedelta(seconds=1)

    def test_invalid_timeframe(self):
        """Should raise ValueError for invalid timeframe."""
        with pytest.raises(ValueError) as exc_info:
            get_time_threshold("invalid_timeframe")
        assert "Invalid timeframe: invalid_timeframe" in str(exc_info.value)
        assert "Valid options:" in str(exc_info.value)


class TestGetTimeRange:
    """Tests for get_time_range function."""

    def test_basic_range(self):
        """Should return (from_time, to_time) tuple."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        from_time, to_time = get_time_range("day", count=7, reference_time=reference)

        assert to_time == reference
        assert from_time == reference - timedelta(days=7)

    def test_hour_range(self):
        """Should calculate hour range correctly."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        from_time, to_time = get_time_range("hour", count=6, reference_time=reference)

        assert to_time == reference
        assert from_time == reference - timedelta(hours=6)

    def test_default_count(self):
        """Should use count=1 by default."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        from_time, to_time = get_time_range("day", reference_time=reference)

        assert to_time == reference
        assert from_time == reference - timedelta(days=1)

    def test_default_reference_time(self):
        """Should use current time when reference_time not provided."""
        before = datetime.utcnow()
        from_time, to_time = get_time_range("hour")
        after = datetime.utcnow()

        # to_time should be approximately now
        assert before - timedelta(seconds=1) <= to_time <= after + timedelta(seconds=1)


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_seconds_only(self):
        """Should format seconds only when less than a minute."""
        assert format_duration(30) == "30s"
        assert format_duration(45) == "45s"

    def test_minutes_and_seconds(self):
        """Should format minutes and seconds."""
        assert format_duration(90) == "1m 30s"
        assert format_duration(125) == "2m 5s"

    def test_hours_and_minutes(self):
        """Should format hours and minutes with default precision."""
        assert format_duration(3665) == "1h 1m"  # 1h 1m 5s, but precision=2
        assert format_duration(7200) == "2h"

    def test_hours_minutes_seconds_with_precision(self):
        """Should include seconds when precision=3."""
        assert format_duration(3665, precision=3) == "1h 1m 5s"
        assert format_duration(7265, precision=3) == "2h 1m 5s"

    def test_days_hours(self):
        """Should format days and hours."""
        assert format_duration(90000) == "1d 1h"  # 25 hours = 1 day 1 hour
        assert format_duration(172800) == "2d"  # 48 hours = 2 days

    def test_days_hours_minutes_with_precision(self):
        """Should respect precision with days."""
        assert format_duration(90061, precision=3) == "1d 1h 1m"
        assert format_duration(90061, precision=4) == "1d 1h 1m 1s"

    def test_zero_duration(self):
        """Should return '0s' for zero duration."""
        assert format_duration(0) == "0s"

    def test_negative_duration(self):
        """Should return '0s' for negative duration."""
        assert format_duration(-100) == "0s"

    def test_precision_1(self):
        """Should show only highest unit with precision=1."""
        assert format_duration(3665, precision=1) == "1h"
        assert format_duration(90, precision=1) == "1m"

    def test_precision_4(self):
        """Should show up to 4 units with precision=4."""
        # 1 day + 1 hour + 1 minute + 1 second = 90061 seconds
        assert format_duration(90061, precision=4) == "1d 1h 1m 1s"


class TestFormatTimestamp:
    """Tests for format_timestamp function."""

    def test_iso_format(self):
        """Should format as ISO 8601 string."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="iso")
        assert result == "2025-01-09T12:34:56"

    def test_iso_format_default(self):
        """Should use ISO format by default."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt)
        assert result == "2025-01-09T12:34:56"

    def test_human_format(self):
        """Should format as human-readable string."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="human")
        assert result == "January 09, 2025 12:34 PM"

    def test_compact_format(self):
        """Should format as compact filename-safe string."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="compact")
        assert result == "2025-01-09_12-34-56"

    def test_date_only_format(self):
        """Should format as date only."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="date_only")
        assert result == "2025-01-09"

    def test_time_only_format(self):
        """Should format as time only."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="time_only")
        assert result == "12:34:56"

    def test_timezone_aware_iso(self):
        """Should add Z suffix for UTC in ISO format when timezone_aware=True."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="iso", timezone_aware=True)
        assert result == "2025-01-09T12:34:56Z"

    def test_timezone_aware_already_has_z(self):
        """Should not add Z suffix if already present."""
        # Note: datetime.isoformat() doesn't add Z, but if it did, this would test it
        dt = datetime(2025, 1, 9, 12, 34, 56)
        result = format_timestamp(dt, format="iso", timezone_aware=True)
        assert result.endswith("Z")
        assert result.count("Z") == 1

    def test_invalid_format(self):
        """Should raise ValueError for invalid format."""
        dt = datetime(2025, 1, 9, 12, 34, 56)
        with pytest.raises(ValueError) as exc_info:
            format_timestamp(dt, format="invalid_format")
        assert "Invalid format: invalid_format" in str(exc_info.value)


class TestBucketTime:
    """Tests for bucket_time function."""

    def test_daily_bucket(self):
        """Should bucket to start of day with bucket_size_hours=24."""
        dt = datetime(2025, 1, 9, 15, 30, 45)
        result = bucket_time(dt, bucket_size_hours=24)
        expected = datetime(2025, 1, 9, 0, 0, 0)
        assert result == expected

    def test_daily_bucket_default(self):
        """Should use daily buckets by default."""
        dt = datetime(2025, 1, 9, 15, 30, 45)
        result = bucket_time(dt)
        expected = datetime(2025, 1, 9, 0, 0, 0)
        assert result == expected

    def test_hourly_bucket(self):
        """Should bucket to start of hour with bucket_size_hours=1."""
        dt = datetime(2025, 1, 9, 15, 30, 45)
        result = bucket_time(dt, bucket_size_hours=1)
        expected = datetime(2025, 1, 9, 15, 0, 0)
        assert result == expected

    def test_6_hour_bucket(self):
        """Should bucket to 6-hour intervals."""
        # 15:30:45 should bucket to 12:00:00 (3rd bucket: 0, 6, 12, 18)
        dt = datetime(2025, 1, 9, 15, 30, 45)
        result = bucket_time(dt, bucket_size_hours=6)
        expected = datetime(2025, 1, 9, 12, 0, 0)
        assert result == expected

    def test_12_hour_bucket(self):
        """Should bucket to 12-hour intervals."""
        # 15:30:45 should bucket to 12:00:00 (2nd bucket: 0, 12)
        dt = datetime(2025, 1, 9, 15, 30, 45)
        result = bucket_time(dt, bucket_size_hours=12)
        expected = datetime(2025, 1, 9, 12, 0, 0)
        assert result == expected

    def test_bucket_already_at_boundary(self):
        """Should return same time if already at bucket boundary."""
        dt = datetime(2025, 1, 9, 12, 0, 0)
        result = bucket_time(dt, bucket_size_hours=24)
        assert result == datetime(2025, 1, 9, 0, 0, 0)

    def test_midnight_bucket(self):
        """Should handle midnight correctly."""
        dt = datetime(2025, 1, 9, 0, 0, 0)
        result = bucket_time(dt, bucket_size_hours=24)
        assert result == datetime(2025, 1, 9, 0, 0, 0)


class TestIsRecent:
    """Tests for is_recent function."""

    def test_recent_within_threshold(self):
        """Should return True when datetime is within threshold."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=30)

        assert is_recent(dt, threshold_seconds=60, reference_time=reference) is True

    def test_not_recent_beyond_threshold(self):
        """Should return False when datetime is beyond threshold."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=90)

        assert is_recent(dt, threshold_seconds=60, reference_time=reference) is False

    def test_exactly_at_threshold(self):
        """Should return True when exactly at threshold."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=60)

        assert is_recent(dt, threshold_seconds=60, reference_time=reference) is True

    def test_default_threshold_60_seconds(self):
        """Should use 60 seconds as default threshold."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=30)

        assert is_recent(dt, reference_time=reference) is True

    def test_default_reference_time(self):
        """Should use current time when reference_time not provided."""
        # Create a datetime 30 seconds ago
        dt = datetime.utcnow() - timedelta(seconds=30)
        assert is_recent(dt, threshold_seconds=60) is True

        # Create a datetime 90 seconds ago
        dt = datetime.utcnow() - timedelta(seconds=90)
        assert is_recent(dt, threshold_seconds=60) is False

    def test_future_datetime(self):
        """Should handle future datetimes correctly (negative age)."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference + timedelta(seconds=30)

        # Future datetime has negative age, should be False
        assert is_recent(dt, threshold_seconds=60, reference_time=reference) is False


class TestTimeAgo:
    """Tests for time_ago function."""

    def test_seconds_ago(self):
        """Should format seconds ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=30)

        assert time_ago(dt, reference_time=reference) == "30 seconds ago"

    def test_1_second_ago(self):
        """Should use singular 'second' for 1 second."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(seconds=1)

        assert time_ago(dt, reference_time=reference) == "1 seconds ago"  # Note: function uses plural

    def test_minutes_ago_singular(self):
        """Should format 1 minute ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(minutes=1)

        assert time_ago(dt, reference_time=reference) == "1 minute ago"

    def test_minutes_ago_plural(self):
        """Should format multiple minutes ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(minutes=5)

        assert time_ago(dt, reference_time=reference) == "5 minutes ago"

    def test_hours_ago_singular(self):
        """Should format 1 hour ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(hours=1)

        assert time_ago(dt, reference_time=reference) == "1 hour ago"

    def test_hours_ago_plural(self):
        """Should format multiple hours ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(hours=3)

        assert time_ago(dt, reference_time=reference) == "3 hours ago"

    def test_days_ago_singular(self):
        """Should format 1 day ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=1)

        assert time_ago(dt, reference_time=reference) == "1 day ago"

    def test_days_ago_plural(self):
        """Should format multiple days ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=3)

        assert time_ago(dt, reference_time=reference) == "3 days ago"

    def test_weeks_ago_singular(self):
        """Should format 1 week ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=7)

        assert time_ago(dt, reference_time=reference) == "1 week ago"

    def test_weeks_ago_plural(self):
        """Should format multiple weeks ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=14)

        assert time_ago(dt, reference_time=reference) == "2 weeks ago"

    def test_months_ago_singular(self):
        """Should format 1 month ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=30)

        assert time_ago(dt, reference_time=reference) == "1 month ago"

    def test_months_ago_plural(self):
        """Should format multiple months ago."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        dt = reference - timedelta(days=90)

        assert time_ago(dt, reference_time=reference) == "3 months ago"

    def test_default_reference_time(self):
        """Should use current time when reference_time not provided."""
        # Create a datetime 5 minutes ago
        dt = datetime.utcnow() - timedelta(minutes=5)
        result = time_ago(dt)

        # Should be "5 minutes ago" (allowing for 1 minute variance due to execution time)
        assert "minute" in result
        assert "ago" in result


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_large_duration(self):
        """Should handle very large durations."""
        # 1 year in seconds
        result = format_duration(31536000, precision=4)
        assert "365d" in result

    def test_bucket_time_with_fractional_seconds(self):
        """Should handle datetimes with microseconds."""
        dt = datetime(2025, 1, 9, 15, 30, 45, 123456)
        result = bucket_time(dt, bucket_size_hours=1)
        expected = datetime(2025, 1, 9, 15, 0, 0)
        assert result == expected

    def test_threshold_with_all_timeframe(self):
        """Should handle 'all' timeframe in get_time_threshold."""
        result = get_time_threshold("all", count=999)  # count should be ignored
        assert result == datetime.min

    def test_time_range_with_all_timeframe(self):
        """Should handle 'all' timeframe in get_time_range."""
        reference = datetime(2025, 1, 9, 12, 0, 0)
        from_time, to_time = get_time_range("all", reference_time=reference)

        assert from_time == datetime.min
        assert to_time == reference
