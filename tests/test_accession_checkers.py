import pytest
import vcr
from sending.parsers import Entry
from sending.curation_files import NewFiles, TrEMBLFiles
from sending.accession_checkers import NewAccessionChecker, TrEMBLAccessionChecker


@pytest.fixture
def trembl_accession_checker() -> TrEMBLAccessionChecker:
    trembl = TrEMBLFiles("tests/fixtures/files/tremblfiles")
    trembl_accession_checker = TrEMBLAccessionChecker(trembl_files=trembl)
    return trembl_accession_checker


@pytest.fixture
def new_accession_checker() -> NewAccessionChecker:
    newfiles = NewFiles("tests/fixtures/files/newfiles")
    new_accession_checker = NewAccessionChecker(files=newfiles)
    return new_accession_checker


@vcr.use_cassette("tests/fixtures/cassettes/trembl_accession_check.yml")
def test_trembl_accession_checker_check(
    trembl_accession_checker: TrEMBLAccessionChecker,
):
    assert not trembl_accession_checker.ok
    trembl_accession_checker.check()
    assert trembl_accession_checker.ok


@vcr.use_cassette("tests/fixtures/cassettes/trembl_accession_check_with_error.yml")
def test_trembl_accession_checker_check_error():
    # File trembl.bad in fixtures has a missing DR EMBL line.
    trembl = TrEMBLFiles(
        "tests/fixtures/files/tremblfiles", valid_suffixes=(".bad", ".BAD")
    )
    trembl_accession_checker = TrEMBLAccessionChecker(trembl)
    assert not trembl_accession_checker.ok
    trembl_accession_checker.check()
    assert not trembl_accession_checker.ok


def test_trembl_accession_checker_accessions(
    trembl_accession_checker: TrEMBLAccessionChecker,
):
    assert "Q80WP0" in trembl_accession_checker.accessions


def test_trembl_accession_checker_pids(
    trembl_accession_checker: TrEMBLAccessionChecker,
):
    assert "AAN31172.1" in trembl_accession_checker.pids


@vcr.use_cassette("tests/fixtures/cassettes/trembl_accession_check.yml")
def test_trembl_accession_checker_trembl_accessions(
    trembl_accession_checker: TrEMBLAccessionChecker,
):
    assert trembl_accession_checker.trembl_accessions == []
    trembl_accession_checker.check()
    assert "Q80WP0" in trembl_accession_checker.trembl_accessions


@vcr.use_cassette("tests/fixtures/cassettes/trembl_accession_check.yml")
def test_trembl_accession_checker_trembl_pids(
    trembl_accession_checker: TrEMBLAccessionChecker,
):
    assert trembl_accession_checker.trembl_pids == []
    trembl_accession_checker.check()
    assert "AAN31172.1" in trembl_accession_checker.pids


def test_new_accession_checker_entries(new_accession_checker: NewAccessionChecker):
    expected_entry = Entry(
        accessions=["F1ANB3", "C00000"],
        pids=[
            "ADE27514.1",
            "ADE27515.1",
            "ADE27516.1",
            "ADE27517.1",
            "ADE27518.1",
            "ADE27519.1",
            "ADE27520.1",
            "ADE27521.1",
            "ADE27522.1",
            "ADE27523.1",
            "ADE27524.1",
        ],
    )
    assert expected_entry in new_accession_checker.entries


def test_new_accession_checker_accessions(new_accession_checker: NewAccessionChecker):
    expected_accessions = ["F1ANB3", "C00000"]
    assert new_accession_checker.accessions == expected_accessions


def test_new_accession_checker_trembl_accessions_before_check(
    new_accession_checker: NewAccessionChecker,
):
    assert new_accession_checker.trembl_accessions is None


def test_new_accession_checker_ok_before_check(
    new_accession_checker: NewAccessionChecker,
):
    assert new_accession_checker.ok is False


@vcr.use_cassette("tests/fixtures/cassettes/new_accession_check_without_errors.yml")
def test_new_accession_checker_check(new_accession_checker: NewAccessionChecker):
    new_accession_checker.check()
    expected_trembl_accessions = ["F1ANB3"]
    assert new_accession_checker.trembl_accessions == expected_trembl_accessions


def test_new_accession_checker_ok_without_error(
    new_accession_checker: NewAccessionChecker,
):
    new_accession_checker.trembl_accessions = []
    new_accession_checker.entries_with_error = []
    assert new_accession_checker.ok is True


def test_new_accession_checker_ok_with_error(
    new_accession_checker: NewAccessionChecker,
):
    entry_with_error = Entry(["F1ANB3", "C00000"], [])
    new_accession_checker.accessions = ["F1ANB3", "C00000"]
    new_accession_checker.entries_with_error = [("F1ANB3", ["C00000"])]
    assert new_accession_checker.ok is False


def test_new_accession_checker_check_secondary_accessions(
    new_accession_checker: NewAccessionChecker,
):
    assert not new_accession_checker.entries_with_error
    new_accession_checker.trembl_accessions = ["C00000"]
    new_accession_checker._check_secondary_accessions()
    assert new_accession_checker.entries_with_error


# TODO: handle cases where there are no files to check e.g. raise error

