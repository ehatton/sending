import pytest
from sending.curation_files import LogFiles


@pytest.fixture(scope="session")
def logfiles():
    logfiles = LogFiles(
        submission_dir="tests/fixtures/files/logfiles", valid_suffixes=(".log", ".LOG")
    )
    return logfiles


def test_str(logfiles):
    assert str(logfiles) == "LogFiles"


def test_get_accessions(logfiles):
    expected_accessions = ["Q6PB30"]
    accessions = logfiles.get_accessions()
    assert accessions == expected_accessions
