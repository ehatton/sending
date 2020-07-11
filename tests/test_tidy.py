import pytest
from click.testing import CliRunner

from sending import tidy


@pytest.fixture
def result():
    runner = CliRunner()
    result = runner.invoke(tidy.tidy)
    return result


def test_tidy_return_code(result):
    assert result.exit_code == 0


def test_tidy_error(result):
    assert "There was a problem backing up files" in result.stdout


# test that move works if file already exists
