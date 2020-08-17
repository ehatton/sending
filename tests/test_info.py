import pytest
from click.testing import CliRunner

from sending.info import info


@pytest.fixture
def result():
    runner = CliRunner()
    result = runner.invoke(info)
    return result


def test_info_exit_code(result):
    assert result.exit_code == 0


def test_info_logfile_output(result):
    expected_logfile_output = "LogFiles\tfiles: 1\tentries: 1"
    assert expected_logfile_output in result.stdout


def test_info_tremblfile_output(result):
    expected_tremblfile_output = "TrEMBLFiles\tfiles: 2\tentries: 7"
    assert expected_tremblfile_output in result.stdout
