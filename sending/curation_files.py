import io
import os
import shutil
from itertools import chain
from pathlib import Path
from typing import Callable, Iterator, List, Optional, TextIO, Tuple, Union

from sending.parsers import Entry, parse_flatfile, parse_logfile

# All possible curation file suffixes, upper and lower case.
ALL_SUFFIXES = (
    ".log",
    ".LOG",
    ".new",
    ".NEW",
    ".pep",
    ".PEP",
    ".sub",
    ".SUB",
    ".pid",
    ".PID",
    ".seq",
    ".SEQ",
)


class CurationFiles:
    """Base class to represent a directory of curation files ready for submission.

    Attributes:
        submission_dir (str): path to a directory containing the submission
        files.
        remote_dir (str): path to directory on remote FTP server.
    """

    def __init__(
        self,
        submission_dir: Union[str, Path],
        remote_dir: Optional[str],
        valid_suffixes: Tuple[str, ...] = ALL_SUFFIXES,
        parser: Callable[[TextIO], Iterator[Entry]] = parse_flatfile,
    ) -> None:
        self.submission_dir: Path = Path(submission_dir)
        self.remote_dir: Optional[str] = remote_dir
        self._valid_suffixes: Tuple[str, ...] = valid_suffixes
        self._parse: Callable[[TextIO], Iterator[Entry]] = parser

    def __repr__(self) -> str:
        return f"CurationFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "CurationFiles"

    def __bool__(self) -> bool:
        """Returns True if there is one or more files in the submission
        directory, else False.
        """
        return len(self) > 0

    def __len__(self) -> int:
        """Returns the number of files in the submission directory.
        """
        return len([i for i in self])

    def __iter__(self) -> Iterator[Path]:
        """Iterates over all files in the submission directory.
        """
        return (
            x for x in self.submission_dir.iterdir() if x.suffix in self._valid_suffixes
        )

    def backup(self) -> None:
        """Moves all files to the backup directory named 'old', which is within
        the submission directory.
        """
        old = self.submission_dir / "old"

        # Check for existence of "old" dir otherwise shutil will silently
        # rename the file to "old" instead.
        if old.is_dir():
            for i in self:
                backup = old / i.name
                try:
                    shutil.copy2(i, backup)
                # If a file with the same name already exists in the old dir,
                # Windows may throw a PermissionError when trying to overwrite
                # it. Strangely it will delete the file without any problem.
                except PermissionError:
                    backup.unlink()
                    shutil.copy2(i, backup)
        else:
            raise FileNotFoundError(
                f'Could not find "old" directory in {self.submission_dir}'
            )

    def delete(self) -> None:
        """Deletes files in submission directory.
        """
        for i in self:
            i.unlink()

    def write_files(self, filepath: Union[str, Path], mode: str = "w") -> None:
        """Writes all submission files to a single file.
        """
        with open(filepath, mode) as outfile:
            text = self.get_text()
            outfile.write(text)

    def get_accessions(self) -> List[str]:
        """Returns a list of all UniProt accessions found in the entries
        (including secondary accessions).
        """
        accessions = list(chain.from_iterable(x.accessions for x in self.get_entries()))
        return accessions

    def get_pids(self) -> List[str]:
        """Returns a list of all protein ids (EMBL CDS identifiers) found in the
        entries.
        """
        pids = list(chain.from_iterable(x.pids for x in self.get_entries()))
        return pids

    def get_text(self) -> str:
        """Returns a string containing all content of the files.
        """
        text = ""
        for file in self:
            text += file.read_text()
        return text

    def get_entries(self) -> List[Entry]:
        """Returns a list of Entry objects for all entries in the files.
        """
        text = self.get_text()
        filehandle = io.StringIO(text)
        entries = list(self._parse(filehandle))
        return entries


class LogFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("LOG_DIR", default=""),
        remote_dir: str = os.getenv("LOG_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".log", ".LOG"),
        parser: Callable[[TextIO], Iterator[Entry]] = parse_logfile,
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes, parser)

    def __repr__(self) -> str:
        return f"LogFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "LogFiles"

    def get_pids(self) -> NotImplementedError:
        raise NotImplementedError("Method get_pids is not valid for LogFiles class.")


class TrEMBLFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("TREMBL_DIR", default=""),
        remote_dir: str = os.getenv("TREMBL_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".new", ".NEW"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"TrEMBLFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "TrEMBLFiles"


class NewFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("NEW_DIR", default=""),
        remote_dir: str = os.getenv("NEW_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, ...] = (".new", ".NEW,"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"NewFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "NewFiles"


class PepFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("PEP_DIR", default=""),
        remote_dir: str = os.getenv("PEP_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".pep", ".PEP"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"PepFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "PepFiles"

    # TODO: this method can be deleted once curators are used to the new
    # procedure
    def delete(self) -> None:
        """Deletes files in submission directory. Also removes any pep files
        which might be put in the newfiles directory by curators using the old
        procedure.
        """
        super().delete()
        new_dir = Path(os.environ["NEW_DIR"])
        for i in new_dir.iterdir():
            if i.suffix in [".pep", ".PEP"]:
                i.unlink()


class SubFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("SUB_DIR", default=""),
        remote_dir: str = os.getenv("SUB_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".sub", ".SUB"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"SubFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "SubFiles"

    # TODO: this method can be deleted once curators are used to the new
    # procedure
    def delete(self) -> None:
        """Deletes files in submission directory. Also removes any sub files
        which might be put in the newfiles directory by curators using the old
        procedure.
        """
        super().delete()
        new_dir = Path(os.environ["NEW_DIR"])
        for i in new_dir.iterdir():
            if i.suffix in [".sub", ".SUB"]:
                i.unlink()


class PidFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("PID_DIR", default=""),
        remote_dir: str = os.getenv("PID_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".pid", ".PID"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"PidFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "PidFiles"


class SeqFiles(CurationFiles):
    def __init__(
        self,
        submission_dir: Union[str, Path] = os.getenv("SEQ_DIR", default=""),
        remote_dir: str = os.getenv("SEQ_REMOTE_DIR", default=""),
        valid_suffixes: Tuple[str, str] = (".seq", ".SEQ"),
    ) -> None:
        super().__init__(submission_dir, remote_dir, valid_suffixes)

    def __repr__(self) -> str:
        return f"SeqFiles('{str(self.submission_dir)}')"

    def __str__(self) -> str:
        return "SeqFiles"
