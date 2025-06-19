import pytest


@pytest.mark.xfail(reason="This feature (e.g., advanced_calculation) is not yet implemented.")
def test_feature_not_implemented_yet() -> None:
    """This test checks for a feature that is known to be missing or a bug that is expected. It's marked as xfail."""
    try:
        raise NotImplementedError("Oups, this is not yet implemented")
    except NotImplementedError:  # Specify the expected exception
        # This will raise a NameError : this is just another exemple of something not yet implemented
        call_unimplemented_function()


@pytest.mark.xfail(strict=True, reason="Known bug #XYZ: Division by zero under specific conditions.")
def test_known_bug_expected_to_fail_strictly() -> None:
    """This test covers a known bug. If it unexpectedly passes (XPASS), the test suite will fail because strict=True.
    This helps to identify when a bug marked as xfail has been fixed.
    """
    numerator = 10
    denominator_from_buggy_code = 0
    numerator / denominator_from_buggy_code  # This would cause a ZeroDivisionError
