import os
import pytest
import subprocess
from pathlib import Path
from unittest import mock
from sending.syntax_checkers import LogFileChecker, FlatFileChecker, SyntaxChecker


@pytest.fixture
def logfile_checker():
    logfile_checker = LogFileChecker("tests/fixtures/files/test_logfile.log")
    return logfile_checker


@pytest.fixture
def flatfile_checker():
    flatfile_checker = FlatFileChecker("tests/fixtures/files/test_tremblfile_1.new")
    return flatfile_checker


def test_logfile_checker_ok(logfile_checker):
    assert logfile_checker.ok is False


def test_flatfile_checker_ok(flatfile_checker):
    assert flatfile_checker.ok is False


def test_logfile_checker_error_file(logfile_checker):
    expected_error_file = "synerr.tmp"
    assert logfile_checker._error_file == expected_error_file


def test_flatfile_checker_error_file(flatfile_checker):
    expected_error_file = "tests/fixtures/files/test_tremblfile_1.new.log"
    assert flatfile_checker._error_file == expected_error_file


@mock.patch("subprocess.run")
def test_syntax_checker_start_process(mock_run):
    syntax_checker = SyntaxChecker("tests/fixtures/files/logfiles/logfile.log")
    test_cmd = ["echo", "hello"]
    syntax_checker._cmd = test_cmd
    syntax_checker._start_process()
    mock_run.assert_called_once_with(
        test_cmd, capture_output=True, check=True, text=True
    )


def test_logfile_checker_cmd(logfile_checker):
    expected_cmd = ["runplug", logfile_checker.file_to_check, "-check"]
    assert logfile_checker._cmd == expected_cmd


def test_flatfile_checker_cmd(flatfile_checker):
    spsyntax_path = os.path.join(os.environ["BINPROT"], "spsyntax.pl")
    expected_cmd = ["perl", spsyntax_path, "-c", "-a", flatfile_checker.file_to_check]
    assert flatfile_checker._cmd == expected_cmd


def test_logfile_checker_ok_with_error(logfile_checker):
    synerr = Path("tests/fixtures/files/syntax_errors/synerr_with_error.tmp")
    logfile_checker.error_report = synerr.read_text()
    assert logfile_checker.ok is False


def test_logfile_checker_ok_without_error(logfile_checker):
    synerr = Path("tests/fixtures/files/syntax_errors/synerr_without_error.tmp")
    logfile_checker.error_report = synerr.read_text()
    assert logfile_checker.ok is True


def test_flatfile_checker_ok_with_error(flatfile_checker):
    error_file = Path(
        "tests/fixtures/files/syntax_errors/flatfile_check_with_errors.new.log"
    )
    flatfile_checker.error_report = error_file.read_text()
    assert flatfile_checker.ok is False


def test_flatfile_checker_ok_without_error(flatfile_checker):
    error_file = Path(
        "tests/fixtures/files/syntax_errors/flatfile_check_without_errors.new.log"
    )
    flatfile_checker.error_report = error_file.read_text()
    assert flatfile_checker.ok is True
