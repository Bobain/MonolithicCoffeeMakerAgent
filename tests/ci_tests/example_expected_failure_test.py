# co-author : Gemini Code Assist
import pytest


@pytest.mark.xfail(reason="This feature (e.g., advanced_calculation) is not yet implemented.")
def test_feature_not_implemented_yet() -> None:
    """
    This test checks for a feature that is known to be missing
    or a bug that is expected. It's marked as xfail.
    """
    try:
        raise NotImplementedError("Oups, this is not yet implemented")
    except NotImplementedError:
        # Imagine this is a call to a function or method that does not even exists
        with pytest.raises(NotImplementedError):
            call_unimplemented_function()


@pytest.mark.xfail(strict=True, reason="Known bug #XYZ: Division by zero under specific conditions.")
def test_known_bug_expected_to_fail_strictly() -> None:
    """
    This test covers a known bug. If it unexpectedly passes (XPASS),
    the test suite will fail because strict=True. This helps to
    identify when a bug marked as xfail has been fixed.
    """
    numerator = 10
    denominator_from_buggy_code = 0  # This would cause a ZeroDivisionError

    # This assertion will fail because of the ZeroDivisionError
    buggy_calculation_result = numerator / denominator_from_buggy_code  # instead of, say, 2
