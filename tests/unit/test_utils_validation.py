"""Unit tests for coffee_maker.utils.validation module."""

import pytest
from coffee_maker.utils.validation import (
    require_type,
    require_one_of,
    require_non_empty,
    require_positive,
    require_range,
    require_not_none,
    validate_url,
)


class TestRequireType:
    """Tests for require_type function."""

    def test_valid_single_type(self):
        """Should return value when type matches."""
        assert require_type(42, int, "value") == 42
        assert require_type("hello", str, "value") == "hello"
        assert require_type([1, 2, 3], list, "value") == [1, 2, 3]
        assert require_type({"key": "value"}, dict, "value") == {"key": "value"}

    def test_invalid_single_type(self):
        """Should raise TypeError when type doesn't match."""
        with pytest.raises(TypeError) as exc_info:
            require_type("string", int, "value")
        assert "value must be int, got str" in str(exc_info.value)

    def test_valid_tuple_of_types(self):
        """Should return value when type matches any in tuple."""
        assert require_type(42, (int, float), "value") == 42
        assert require_type(3.14, (int, float), "value") == 3.14
        assert require_type("test", (str, bytes), "value") == "test"

    def test_invalid_tuple_of_types(self):
        """Should raise TypeError when type doesn't match any in tuple."""
        with pytest.raises(TypeError) as exc_info:
            require_type("string", (int, float), "value")
        assert "value must be int or float, got str" in str(exc_info.value)

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(TypeError) as exc_info:
            require_type("invalid", int, "user_id")
        assert "user_id must be int, got str" in str(exc_info.value)


class TestRequireOneOf:
    """Tests for require_one_of function."""

    def test_valid_value_in_list(self):
        """Should return value when it's in options list."""
        assert require_one_of("tier1", ["tier1", "tier2", "tier3"], "tier") == "tier1"
        assert require_one_of(2, [1, 2, 3], "value") == 2
        assert require_one_of("openai", ["openai", "gemini"], "provider") == "openai"

    def test_invalid_value_not_in_list(self):
        """Should raise ValueError when value not in options."""
        with pytest.raises(ValueError) as exc_info:
            require_one_of("tier4", ["tier1", "tier2", "tier3"], "tier")
        assert "tier must be one of ['tier1', 'tier2', 'tier3'], got 'tier4'" in str(exc_info.value)

    def test_valid_value_in_tuple(self):
        """Should work with tuple of options."""
        assert require_one_of("a", ("a", "b", "c"), "value") == "a"

    def test_valid_value_in_set(self):
        """Should work with set of options."""
        assert require_one_of("x", {"x", "y", "z"}, "value") == "x"

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(ValueError) as exc_info:
            require_one_of("invalid", ["valid"], "status")
        assert "status must be one of ['valid'], got 'invalid'" in str(exc_info.value)


class TestRequireNonEmpty:
    """Tests for require_non_empty function."""

    def test_valid_non_empty_string(self):
        """Should return value when string is non-empty."""
        assert require_non_empty("hello", "value") == "hello"
        assert require_non_empty("  ", "value") == "  "  # Whitespace counts as non-empty

    def test_invalid_empty_string(self):
        """Should raise ValueError when string is empty."""
        with pytest.raises(ValueError) as exc_info:
            require_non_empty("", "value")
        assert "value cannot be empty" in str(exc_info.value)

    def test_valid_non_empty_list(self):
        """Should return value when list is non-empty."""
        assert require_non_empty([1, 2, 3], "items") == [1, 2, 3]
        assert require_non_empty([None], "items") == [None]

    def test_invalid_empty_list(self):
        """Should raise ValueError when list is empty."""
        with pytest.raises(ValueError) as exc_info:
            require_non_empty([], "items")
        assert "items cannot be empty" in str(exc_info.value)

    def test_valid_non_empty_dict(self):
        """Should return value when dict is non-empty."""
        assert require_non_empty({"key": "value"}, "config") == {"key": "value"}

    def test_invalid_empty_dict(self):
        """Should raise ValueError when dict is empty."""
        with pytest.raises(ValueError) as exc_info:
            require_non_empty({}, "config")
        assert "config cannot be empty" in str(exc_info.value)

    def test_valid_non_empty_set(self):
        """Should return value when set is non-empty."""
        assert require_non_empty({1, 2, 3}, "values") == {1, 2, 3}

    def test_invalid_empty_set(self):
        """Should raise ValueError when set is empty."""
        with pytest.raises(ValueError) as exc_info:
            require_non_empty(set(), "values")
        assert "values cannot be empty" in str(exc_info.value)

    def test_valid_non_empty_tuple(self):
        """Should return value when tuple is non-empty."""
        assert require_non_empty((1, 2), "coords") == (1, 2)

    def test_invalid_empty_tuple(self):
        """Should raise ValueError when tuple is empty."""
        with pytest.raises(ValueError) as exc_info:
            require_non_empty((), "coords")
        assert "coords cannot be empty" in str(exc_info.value)


class TestRequirePositive:
    """Tests for require_positive function."""

    def test_valid_positive_int(self):
        """Should return value when int is positive."""
        assert require_positive(42, "value") == 42
        assert require_positive(1, "value") == 1

    def test_invalid_zero_by_default(self):
        """Should raise ValueError when value is zero (default behavior)."""
        with pytest.raises(ValueError) as exc_info:
            require_positive(0, "value")
        assert "value must be > 0, got 0" in str(exc_info.value)

    def test_valid_zero_when_allowed(self):
        """Should return 0 when allow_zero=True."""
        assert require_positive(0, "value", allow_zero=True) == 0

    def test_invalid_negative_int(self):
        """Should raise ValueError when int is negative."""
        with pytest.raises(ValueError) as exc_info:
            require_positive(-5, "value")
        assert "value must be > 0, got -5" in str(exc_info.value)

    def test_invalid_negative_int_with_allow_zero(self):
        """Should raise ValueError when int is negative even with allow_zero."""
        with pytest.raises(ValueError) as exc_info:
            require_positive(-1, "value", allow_zero=True)
        assert "value must be >= 0, got -1" in str(exc_info.value)

    def test_valid_positive_float(self):
        """Should return value when float is positive."""
        assert require_positive(3.14, "value") == 3.14
        assert require_positive(0.001, "value") == 0.001

    def test_invalid_negative_float(self):
        """Should raise ValueError when float is negative."""
        with pytest.raises(ValueError) as exc_info:
            require_positive(-2.5, "value")
        assert "value must be > 0, got -2.5" in str(exc_info.value)

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(ValueError) as exc_info:
            require_positive(-10, "token_count")
        assert "token_count must be > 0, got -10" in str(exc_info.value)


class TestRequireRange:
    """Tests for require_range function."""

    def test_valid_value_in_range(self):
        """Should return value when it's within range."""
        assert require_range(5, 1, 10, "value") == 5
        assert require_range(1, 1, 10, "value") == 1
        assert require_range(10, 1, 10, "value") == 10

    def test_invalid_value_below_min(self):
        """Should raise ValueError when value is below minimum."""
        with pytest.raises(ValueError) as exc_info:
            require_range(0, 1, 10, "value")
        assert "value must be >= 1, got 0" in str(exc_info.value)

    def test_invalid_value_above_max(self):
        """Should raise ValueError when value is above maximum."""
        with pytest.raises(ValueError) as exc_info:
            require_range(11, 1, 10, "value")
        assert "value must be <= 10, got 11" in str(exc_info.value)

    def test_valid_with_min_only(self):
        """Should work with only minimum bound."""
        assert require_range(100, min_value=1, param_name="value") == 100
        with pytest.raises(ValueError) as exc_info:
            require_range(0, min_value=1, param_name="value")
        assert "value must be >= 1, got 0" in str(exc_info.value)

    def test_valid_with_max_only(self):
        """Should work with only maximum bound."""
        assert require_range(-100, max_value=10, param_name="value") == -100
        with pytest.raises(ValueError) as exc_info:
            require_range(11, max_value=10, param_name="value")
        assert "value must be <= 10, got 11" in str(exc_info.value)

    def test_valid_float_range(self):
        """Should work with float values."""
        assert require_range(1.5, 0.0, 2.0, "temperature") == 1.5
        assert require_range(0.0, 0.0, 1.0, "value") == 0.0

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(ValueError) as exc_info:
            require_range(15, 1, 10, "safety_margin")
        assert "safety_margin must be <= 10, got 15" in str(exc_info.value)


class TestRequireNotNone:
    """Tests for require_not_none function."""

    def test_valid_non_none_value(self):
        """Should return value when it's not None."""
        assert require_not_none(42, "value") == 42
        assert require_not_none("hello", "value") == "hello"
        assert require_not_none([], "value") == []
        assert require_not_none(0, "value") == 0
        assert require_not_none(False, "value") is False

    def test_invalid_none_value(self):
        """Should raise ValueError when value is None."""
        with pytest.raises(ValueError) as exc_info:
            require_not_none(None, "value")
        assert "value cannot be None" in str(exc_info.value)

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(ValueError) as exc_info:
            require_not_none(None, "config")
        assert "config cannot be None" in str(exc_info.value)


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_http_url(self):
        """Should return URL when it's valid HTTP."""
        assert validate_url("http://example.com", "url") == "http://example.com"
        assert validate_url("http://api.example.com/v1", "url") == "http://api.example.com/v1"

    def test_valid_https_url(self):
        """Should return URL when it's valid HTTPS."""
        assert validate_url("https://example.com", "url") == "https://example.com"
        assert validate_url("https://api.example.com/v1/users", "url") == "https://api.example.com/v1/users"

    def test_invalid_missing_protocol(self):
        """Should raise ValueError when protocol is missing."""
        with pytest.raises(ValueError) as exc_info:
            validate_url("example.com", "url")
        assert "url must be a valid URL (http:// or https://)" in str(exc_info.value)

    def test_invalid_empty_url(self):
        """Should raise ValueError when URL is empty."""
        with pytest.raises(ValueError) as exc_info:
            validate_url("", "url")
        assert "url cannot be empty" in str(exc_info.value)

    def test_require_https_valid(self):
        """Should return URL when HTTPS is required and provided."""
        assert validate_url("https://example.com", "api_url", require_https=True) == "https://example.com"

    def test_require_https_invalid_http(self):
        """Should raise ValueError when HTTPS required but HTTP provided."""
        with pytest.raises(ValueError) as exc_info:
            validate_url("http://example.com", "api_url", require_https=True)
        assert "api_url must start with https://, got 'http://example.com'" in str(exc_info.value)

    def test_require_https_invalid_missing_protocol(self):
        """Should raise ValueError when HTTPS required but no protocol."""
        with pytest.raises(ValueError) as exc_info:
            validate_url("example.com", "api_url", require_https=True)
        assert "api_url must start with https://" in str(exc_info.value)

    def test_custom_param_name(self):
        """Should use custom parameter name in error message."""
        with pytest.raises(ValueError) as exc_info:
            validate_url("ftp://example.com", "webhook_url")
        assert "webhook_url must be a valid URL (http:// or https://)" in str(exc_info.value)


class TestChaining:
    """Tests for chaining multiple validation functions."""

    def test_chain_type_and_range(self):
        """Should be able to chain type and range validation."""
        value = require_type(5, int, "value")
        result = require_range(value, 1, 10, "value")
        assert result == 5

    def test_chain_type_and_non_empty(self):
        """Should be able to chain type and non-empty validation."""
        value = require_type("hello", str, "name")
        result = require_non_empty(value, "name")
        assert result == "hello"

    def test_chain_not_none_and_type(self):
        """Should be able to chain not-none and type validation."""
        value = require_not_none({"key": "value"}, "config")
        result = require_type(value, dict, "config")
        assert result == {"key": "value"}

    def test_chain_url_validation(self):
        """Should be able to chain URL validation with other checks."""
        url = require_not_none("https://api.example.com", "api_url")
        result = validate_url(url, "api_url", require_https=True)
        assert result == "https://api.example.com"
