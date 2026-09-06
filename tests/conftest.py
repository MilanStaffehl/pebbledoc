"""Fixtures for tests."""

import importlib
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def patch_open(mocker: MockerFixture) -> Mock:
    """Patch opening files to intercept final write of MD document."""
    patched_open = mocker.mock_open()
    mocker.patch("pebbledoc.cli_logic.open", patched_open)
    return patched_open


@pytest.fixture
def patch_config_discovery(mocker: MockerFixture) -> None:
    """Prevent config file discovery from running."""
    mocker.patch("pebbledoc.config._discover_config_file", return_value=None)


@pytest.fixture
def patch_module_all(mocker: MockerFixture) -> None:
    """Path the stellarium_lite module to have no __all__."""
    sys.path.append(str(Path(__file__).parent / "acceptance" / "resources"))
    package = importlib.import_module("stellarium_lite")
    mocker.patch.object(package, "__all__", None)
    sys.path.pop()
