import shutil
from pathlib import Path
import pytest
from sending.curation_files import CurationFiles


@pytest.fixture
def curation_files(tmp_path: Path) -> CurationFiles:
    old = tmp_path / "old"
    old.mkdir()
    temp = tmp_path / "temp"
    temp.mkdir()
    for f in Path("tests/fixtures/files/tremblfiles").glob("*.new"):
        shutil.copy2(f, tmp_path)
    curation_files = CurationFiles(tmp_path, remote_dir=None)
    return curation_files


def test_submission_dir(curation_files: CurationFiles):
    assert isinstance(curation_files.submission_dir, Path)


def test_iter(tmp_path: Path, curation_files: CurationFiles):
    file_list = list(curation_files)
    expected_file = tmp_path / "trembl1.new"
    assert expected_file in file_list


def test_len(curation_files: CurationFiles):
    assert len(curation_files) == 2


def test_get_entries(curation_files: CurationFiles):
    assert len(curation_files.get_entries()) == 7


def test_get_accessions(curation_files: CurationFiles):
    expected_accessions = [
        "Q8CJC7",
        "Q80WP0",
        "Q80ZC8",
        "Q80ST4",
        "B2KG20",
        "Q5DT35",
        "Q5DT39",
        "E9PTP0",
        "Q5DT36",
        "Q8BS07",
        "Q5DT37",
        "U3JA75",
    ]
    accessions = curation_files.get_accessions()
    assert sorted(accessions) == sorted(expected_accessions)


def test_get_pids(curation_files: CurationFiles):
    expected_pids = [
        "AAM44080.1",
        "AAN31172.1",
        "AAO49444.1",
        "AAO49445.1",
        "AAO49446.1",
        "EDM01724.1",
        "EDM01725.1",
        "AAR00559.1",
        "AAQ20111.1",
        "AAR00558.1",
        "BAC30742.1",
        "AAI32407.1",
        "AAI32409.1",
        "AAR00557.1",
        "AAH91468.1",
    ]
    pids = curation_files.get_pids()
    assert sorted(pids) == sorted(expected_pids)


def test_backup(curation_files: CurationFiles):
    curation_files.backup()
    expected_backup = curation_files.submission_dir / "old" / "trembl1.new"
    assert expected_backup.is_file()
    assert len(curation_files) == 2


def test_delete(curation_files: CurationFiles):
    assert len(curation_files) == 2
    curation_files.delete()
    assert len(curation_files) == 0


def test_write_files(curation_files: CurationFiles, tmp_path: Path):
    test_file = tmp_path / "temp" / "test_file.new"
    curation_files.write_files(test_file)
    assert test_file.exists()


def test_bool_false(tmp_path: Path):
    # Point to empty directory
    no_files = CurationFiles(submission_dir=tmp_path, remote_dir=None)
    assert not no_files


def test_bool_true(curation_files: CurationFiles):
    assert curation_files
