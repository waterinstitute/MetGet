import sys
from unittest.mock import patch

import pytest

from metget.metget_client import metget_client_cli


def test_cli():
    """
    **TEST PURPOSE**: Validates CLI argument parser initialization and help functionality
    **MODULE**: metget_client.metget_client_cli
    **SCENARIO**: Launch CLI with --help flag to test argparse setup
    **INPUT**: Command line arguments ['metget', '--help']
    **EXPECTED**: CLI displays help message and exits with code 0 (success)
    **COVERAGE**: Tests CLI entry point, argument parser setup, and help message generation
    """
    # Mock sys.argv to avoid conflicts with pytest arguments
    with patch.object(sys, "argv", ["metget", "--help"]):
        # Help command exits with code 0, which is expected
        with pytest.raises(SystemExit) as exc_info:
            metget_client_cli()
        assert exc_info.value.code == 0
