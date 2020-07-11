import pytest
from sending.parsers import Entry, parse_flatfile, parse_logfile


@pytest.fixture
def flatfile_entries():
    test_flatfile = "tests/fixtures/files/tremblfiles/trembl2.new"
    with open(test_flatfile, "r") as infile:
        entries = list(parse_flatfile(infile))
    return entries


@pytest.fixture
def logfile_entries():
    test_logfile = "tests/fixtures/files/logfiles/logfile.log"
    with open(test_logfile, "r") as infile:
        entries = list(parse_logfile(infile))
    return entries


def test_parse_logfile_contains_specific_accession(logfile_entries):
    test_entry = Entry(["Q6PB30"], [])
    assert test_entry in logfile_entries


def test_parse_logfile_reads_all_entries(logfile_entries):
    assert len(logfile_entries) == 1


def test_parse_flatfile_contains_specific_entry(flatfile_entries):
    test_entry = Entry(["Q5DT39", "E9PTP0"], ["AAQ20111.1"])
    assert test_entry in flatfile_entries


def test_parse_flatfile_reads_all_entries(flatfile_entries):
    assert len(flatfile_entries) == 6
