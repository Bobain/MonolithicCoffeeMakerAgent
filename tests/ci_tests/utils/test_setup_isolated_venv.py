# author : gemini-code-assist
import logging  # For caplog
import pathlib
import shutil  # For mocking shutil.rmtree
import subprocess
import sys
from unittest import mock

import pytest

# Assuming your project root is correctly added to sys.path by pytest
# or your poetry setup, so this import works.
from coffee_maker.utils import setup_isolated_venv as siv

# Define a common set of packages for testing
TEST_PACKAGES = ["requests", "numpy==1.23.5"]
TEST_PYTHON_VERSION = "3.12"


@pytest.fixture
def temp_venv_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Provides a temporary path for the virtual environment."""
    return tmp_path / ".test_uv_venv"


# --- Tests for get_venv_python_executable ---


@pytest.mark.parametrize(
    "platform, expected_path_segment",
    [
        ("win32", str(pathlib.Path("Scripts") / "python.exe")),
        ("linux", str(pathlib.Path("bin") / "python")),
        ("darwin", str(pathlib.Path("bin") / "python")),
    ],
)
def test_get_venv_python_executable(temp_venv_dir, monkeypatch, platform, expected_path_segment):
    """Test the Python executable path generation for different platforms."""
    monkeypatch.setattr(sys, "platform", platform)
    executable_path = siv.get_venv_python_executable(temp_venv_dir)
    assert executable_path == str(temp_venv_dir / expected_path_segment)


# --- Tests for setup_uv_pip ---


def test_setup_uv_pip_missing_arguments(temp_venv_dir):
    """Test that ValueError is raised for missing required arguments."""
    with pytest.raises(ValueError, match="venv_dir_path must be provided"):
        siv.setup_uv_pip(packages_to_install=TEST_PACKAGES, python_version=TEST_PYTHON_VERSION)
    with pytest.raises(ValueError, match="packages_to_install must be provided"):
        siv.setup_uv_pip(venv_dir_path=temp_venv_dir, python_version=TEST_PYTHON_VERSION)
    with pytest.raises(ValueError, match="python_version must be provided"):
        siv.setup_uv_pip(venv_dir_path=temp_venv_dir, packages_to_install=TEST_PACKAGES)


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_new_venv_success(mock_path_exists, mock_subprocess_run, temp_venv_dir, caplog):
    """Test successful creation of a new venv and package installation."""
    caplog.set_level(logging.INFO)
    # Simulate subprocess.run for uv returning stdout
    mock_subprocess_run.return_value = mock.Mock(returncode=0, stdout="Success from uv", stderr="")
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    def path_exists_side_effect(self_path_instance):
        if self_path_instance == temp_venv_dir:  # Initial check for venv directory
            return False
        if self_path_instance == expected_python_exe_path:  # Check for python exe after venv creation
            return True  # Simulate it exists after uv venv command
        return False

    mock_path_exists.side_effect = path_exists_side_effect

    returned_exe_str = siv.setup_uv_pip(
        venv_dir_path=temp_venv_dir,
        packages_to_install=TEST_PACKAGES,
        python_version=TEST_PYTHON_VERSION,
        overwrite_existing=False,
    )

    assert returned_exe_str == str(expected_python_exe_path)
    assert mock_subprocess_run.call_count == 1 + len(TEST_PACKAGES)

    venv_call = mock.call(
        ["uv", "venv", str(temp_venv_dir), f"--python={TEST_PYTHON_VERSION}"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert venv_call in mock_subprocess_run.call_args_list

    for package in TEST_PACKAGES:
        install_call = mock.call(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(expected_python_exe_path),
                package,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert install_call in mock_subprocess_run.call_args_list

    assert f"Virtual environment '{temp_venv_dir}' created successfully" in caplog.text
    for package in TEST_PACKAGES:
        assert f"Installing/verifying {package}" in caplog.text
        # Corrected assertion: Expect the log message for when stdout is present
        assert f"Output for {package} installation:\nSuccess from uv" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
@mock.patch("coffee_maker.utils.setup_isolated_venv.shutil.rmtree")
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_overwrite_existing_success(
    mock_path_exists, mock_rmtree, mock_subprocess_run, temp_venv_dir, caplog
):
    """Test overwriting an existing venv."""
    caplog.set_level(logging.INFO)
    mock_subprocess_run.return_value = mock.Mock(returncode=0, stdout="Success", stderr="")
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    path_exists_call_log = []

    def path_exists_side_effect(self_path_instance):
        path_exists_call_log.append(self_path_instance)
        if self_path_instance == temp_venv_dir and len(path_exists_call_log) == 1:
            return True  # venv_dir_path.exists() before rmtree
        if self_path_instance == expected_python_exe_path:  # After recreation
            return True
        # If temp_venv_dir is checked again after rmtree but before uv venv command
        if self_path_instance == temp_venv_dir and len(path_exists_call_log) > 1:
            return False  # It would have been deleted by rmtree, before uv venv recreates it
        return False

    mock_path_exists.side_effect = path_exists_side_effect

    returned_exe_str = siv.setup_uv_pip(
        venv_dir_path=temp_venv_dir,
        packages_to_install=TEST_PACKAGES,
        python_version=TEST_PYTHON_VERSION,
        overwrite_existing=True,
    )

    assert returned_exe_str == str(expected_python_exe_path)
    mock_rmtree.assert_called_once_with(str(temp_venv_dir))
    assert mock_subprocess_run.call_count == 1 + len(TEST_PACKAGES)
    assert f"Overwriting as requested" in caplog.text
    assert f"Virtual environment '{temp_venv_dir}' created successfully" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_existing_complete_venv_no_overwrite(mock_path_exists, temp_venv_dir, caplog):
    """Test skipping creation if venv exists, is complete, and not overwriting."""
    caplog.set_level(logging.INFO)
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    def path_exists_side_effect(self_path_instance):
        if self_path_instance == temp_venv_dir or self_path_instance == expected_python_exe_path:
            return True
        return False

    mock_path_exists.side_effect = path_exists_side_effect

    with mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run") as mock_subprocess_run_install:
        mock_subprocess_run_install.return_value = mock.Mock(returncode=0, stdout="Success from uv", stderr="")
        returned_exe_str = siv.setup_uv_pip(
            venv_dir_path=temp_venv_dir,
            packages_to_install=TEST_PACKAGES,
            python_version=TEST_PYTHON_VERSION,
            overwrite_existing=False,
        )

    assert returned_exe_str == str(expected_python_exe_path)
    assert mock_subprocess_run_install.call_count == len(TEST_PACKAGES)
    assert f"Skipping venv creation step" in caplog.text
    for package in TEST_PACKAGES:
        assert f"Installing/verifying {package}" in caplog.text
        assert f"Output for {package} installation:\nSuccess from uv" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
@mock.patch("coffee_maker.utils.setup_isolated_venv.shutil.rmtree")
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_existing_incomplete_venv_recreates(
    mock_path_exists, mock_rmtree, mock_subprocess_run, temp_venv_dir, caplog
):
    """Test recreating venv if it exists but is incomplete."""
    caplog.set_level(logging.INFO)
    mock_subprocess_run.return_value = mock.Mock(returncode=0, stdout="Success", stderr="")
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    call_count_for_path_exists = 0

    def path_exists_side_effect(self_path_instance):
        nonlocal call_count_for_path_exists
        call_count_for_path_exists += 1

        # Call 1: venv_dir_path.exists() -> True
        if self_path_instance == temp_venv_dir and call_count_for_path_exists == 1:
            return True
        # Call 2: pathlib.Path(venv_python_executable).exists() -> False (incomplete)
        if self_path_instance == expected_python_exe_path and call_count_for_path_exists == 2:
            return False
        # After rmtree and recreation, subsequent calls for python exe should be True
        if (
            self_path_instance == expected_python_exe_path and call_count_for_path_exists > 2
        ):  # >2 because first two are specific
            return True
        # For any other calls to temp_venv_dir.exists() after the first one (e.g. if it's checked again after rmtree)
        if self_path_instance == temp_venv_dir and call_count_for_path_exists > 1:
            return False  # It's been removed by rmtree, before uv venv recreates it
        return False

    mock_path_exists.side_effect = path_exists_side_effect

    returned_exe_str = siv.setup_uv_pip(
        venv_dir_path=temp_venv_dir,
        packages_to_install=TEST_PACKAGES,
        python_version=TEST_PYTHON_VERSION,
        overwrite_existing=False,
    )

    assert returned_exe_str == str(expected_python_exe_path)
    mock_rmtree.assert_called_once_with(str(temp_venv_dir))
    assert mock_subprocess_run.call_count == 1 + len(TEST_PACKAGES)
    assert f"incomplete (Python executable missing). Recreating." in caplog.text
    assert f"Virtual environment '{temp_venv_dir}' created successfully" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
def test_setup_uv_pip_venv_creation_fails(mock_subprocess_run, temp_venv_dir, caplog):
    """Test handling of 'uv venv' command failure."""
    caplog.set_level(logging.ERROR)
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["uv", "venv"], stderr="uv venv failed"
    )
    with mock.patch(
        "coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists",
        return_value=False,
        autospec=True,
    ):
        with pytest.raises(
            RuntimeError,
            match=f"Failed to set up or update virtual environment '{temp_venv_dir}'.",
        ):
            siv.setup_uv_pip(
                venv_dir_path=temp_venv_dir,
                packages_to_install=TEST_PACKAGES,
                python_version=TEST_PYTHON_VERSION,
            )
    assert "Error during virtual environment operation" in caplog.text
    assert "uv venv failed" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_package_install_fails(mock_path_exists, mock_subprocess_run, temp_venv_dir, caplog):
    """Test handling of 'uv pip install' command failure."""
    caplog.set_level(logging.ERROR)
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    mock_subprocess_run.side_effect = [
        mock.Mock(returncode=0, stdout="venv created", stderr=""),
        subprocess.CalledProcessError(returncode=1, cmd=["uv", "pip", "install"], stderr="pip install failed"),
    ]

    call_count_for_path_exists = 0

    def path_exists_side_effect(self_path_instance):
        nonlocal call_count_for_path_exists
        call_count_for_path_exists += 1
        if self_path_instance == temp_venv_dir and call_count_for_path_exists == 1:
            return False  # Needs creation
        if self_path_instance == expected_python_exe_path:  # After venv creation
            return True
        return False

    mock_path_exists.side_effect = path_exists_side_effect

    with pytest.raises(
        RuntimeError,
        match=f"Failed to set up or update virtual environment '{temp_venv_dir}'.",
    ):
        siv.setup_uv_pip(
            venv_dir_path=temp_venv_dir,
            packages_to_install=["failing_package"],
            python_version=TEST_PYTHON_VERSION,
        )
    assert "Error during virtual environment operation" in caplog.text
    assert "pip install failed" in caplog.text


def test_setup_uv_pip_uv_not_found(temp_venv_dir, caplog):
    """Test handling when 'uv' command is not found."""
    caplog.set_level(logging.ERROR)
    with mock.patch(
        "coffee_maker.utils.setup_isolated_venv.subprocess.run",
        side_effect=FileNotFoundError("uv not found"),
    ):
        with mock.patch(
            "coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists",
            return_value=False,
            autospec=True,
        ):
            with pytest.raises(FileNotFoundError, match="uv not found"):
                siv.setup_uv_pip(
                    venv_dir_path=temp_venv_dir,
                    packages_to_install=TEST_PACKAGES,
                    python_version=TEST_PYTHON_VERSION,
                )
    assert "`uv` command not found" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.shutil.rmtree", side_effect=OSError("Permission denied"))
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", return_value=True, autospec=True)
def test_setup_uv_pip_rmtree_fails(mock_path_exists_always_true, mock_rmtree_fails, temp_venv_dir, caplog):
    """Test handling of shutil.rmtree failure during overwrite."""
    caplog.set_level(logging.ERROR)
    with pytest.raises(RuntimeError, match=f"Failed to remove existing venv '{temp_venv_dir}'."):
        siv.setup_uv_pip(
            venv_dir_path=temp_venv_dir,
            packages_to_install=TEST_PACKAGES,
            python_version=TEST_PYTHON_VERSION,
            overwrite_existing=True,
        )
    assert f"Error removing existing venv '{temp_venv_dir}': Permission denied" in caplog.text


@mock.patch("coffee_maker.utils.setup_isolated_venv.subprocess.run")
@mock.patch("coffee_maker.utils.setup_isolated_venv.pathlib.Path.exists", autospec=True)
def test_setup_uv_pip_python_exe_missing_before_install(mock_path_exists, mock_subprocess_run, temp_venv_dir, caplog):
    """Test safeguard if Python exe is missing right before package install."""
    caplog.set_level(logging.ERROR)
    # This mock is for the 'uv venv' call if needs_venv_creation becomes true.
    # Or for 'uv pip install' if needs_venv_creation is false but then the exe is missing.
    mock_subprocess_run.return_value = mock.Mock(returncode=0, stdout="venv ok", stderr="")
    expected_python_exe_path = pathlib.Path(siv.get_venv_python_executable(temp_venv_dir))

    # Simulate:
    # 1. venv_dir_path.exists() -> True (initial check)
    # 2. pathlib.Path(venv_python_executable).exists() -> True (initial check, so not incomplete)
    # 3. THEN, when the loop for package install runs, pathlib.Path(venv_python_executable).exists() -> False
    call_count_for_path_exists = 0

    def path_exists_side_effect(self_path_instance):
        nonlocal call_count_for_path_exists
        call_count_for_path_exists += 1

        if self_path_instance == temp_venv_dir:
            return True  # venv dir always exists for this scenario

        if self_path_instance == expected_python_exe_path:
            # First check (in the 'elif not pathlib.Path(venv_python_executable).exists()') should be True
            # Subsequent checks (inside the package install loop) should be False
            return call_count_for_path_exists <= 2  # True for the first two checks on expected_python_exe_path
            # (one for initial venv check, one for the loop's first iteration)
            # This needs to be False for the actual test condition.
            # Let's simplify:
            # Initial check for venv_dir_path.exists() -> True
            # Initial check for venv_python_executable.exists() -> True (so it's not incomplete)
            # Loop check for venv_python_executable.exists() -> False

    # More precise side effect for this specific test:
    # We want to pass the initial checks that would lead to `needs_venv_creation = False`,
    # then fail the check inside the package installation loop.
    def specific_path_exists_side_effect(self_path_instance):
        # First call: venv_dir_path.exists()
        if self_path_instance == temp_venv_dir and mock_path_exists.call_count == 1:
            return True
        # Second call: pathlib.Path(venv_python_executable).exists() (initial check)
        if self_path_instance == expected_python_exe_path and mock_path_exists.call_count == 2:
            return True  # Venv is initially "complete"
        # Subsequent calls for pathlib.Path(venv_python_executable).exists() (inside install loop)
        if self_path_instance == expected_python_exe_path and mock_path_exists.call_count > 2:
            return False  # Now it's missing
        return True  # Default for other potential checks if any

    mock_path_exists.side_effect = specific_path_exists_side_effect

    with pytest.raises(
        RuntimeError,
        match=f"Venv Python executable not found at '{str(expected_python_exe_path)}'.",
    ):
        siv.setup_uv_pip(
            venv_dir_path=temp_venv_dir,
            packages_to_install=["some_package"],
            python_version=TEST_PYTHON_VERSION,
            overwrite_existing=False,  # Venv is initially considered okay
        )
    assert f"Python executable '{str(expected_python_exe_path)}' not found before package installation" in caplog.text
