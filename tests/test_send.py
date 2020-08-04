import pytest
from sending import send
from sending.curation_files import LogFiles, NewFiles, TrEMBLFiles
from unittest import mock


# TODO: add autospec to mock
@pytest.fixture
def mock_connection():
    # Mocks the pysftp Connection object.
    mock_connection = mock.MagicMock()
    return mock_connection


def test_send_send_transfer_updates(mock_connection):
    logfiles = LogFiles("tests/fixtures/files/logfiles", remote_dir="tests")
    send._send_updates(logfiles, mock_connection)
    assert mock_connection.cd.called_with("tests")
    assert mock_connection.put.called_with(
        "tests/fixures/files/logfiles/test_logfile.log"
    )


def test_send_send_newfiles(mock_connection):
    tremblfiles = TrEMBLFiles(
        "tests/fixtures/files/tremblfiles",
        remote_dir="tests",
        valid_suffixes=(".new", ".NEW"),
    )
    newfiles = NewFiles(submission_dir="", remote_dir="")
    send._send_new_entries(files=[tremblfiles, newfiles], sftp=mock_connection)
    assert mock_connection.cd.called_with("tests")
    assert mock_connection.put.called


# @mock.patch("pysftp.Connection")
# def test_send_send_command(mock_connection):
#     runner = CliRunner()
#     result = runner.invoke(send.send)
#     assert mock_connection.called_once()
#     assert result.exit_code == 0
