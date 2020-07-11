import io
import os
from itertools import chain
from typing import List, Optional, Tuple, Union

import requests

from sending.parsers import Entry, parse_flatfile
from sending.curation_files import NewFiles, PepFiles, SubFiles, TrEMBLFiles


class NewAccessionChecker:
    """Checks secondary accessions in NewFiles.

    The file types checked are NewFiles (*.new, excluding curated TrEMBL
    entries), SubFiles (*.sub) and PepFiles (*.pep). For these entries a 
    new UniProt accession is normally created. If the primary accession is
    new, none of the secondary accessions must be present in TrEMBL.

    Attributes:
        entries: list of Entry objects.
        accessions: list of all accessions in the entries.
        trembl_accessions: list of accessions in the entries which are also
            in TrEMBL.
        entries_with_error: list of tuples containing primary accession of
            the failing entry, and a list of the erroneous accessions.

    Methods:
        check: runs the checking procedure.
    """

    def __init__(self, files: Union[NewFiles, PepFiles, SubFiles]):
        self.entries: List[Entry] = files.entries
        self.accessions: List[str] = files.get_accessions()
        self.trembl_accessions: Optional[List[str]] = None
        self.entries_with_error: List[Tuple[str, List[str]]] = []

    @property
    def ok(self) -> bool:
        """Signals whether errors have been detected in the files.

        Returns:
            bool: False if errors are found in the entries, otherwise True.
                Defaults to False if the check method has not been run yet.
        """
        if self.trembl_accessions is None:
            return False  # Default to False if check() has not been run
        elif self.entries_with_error:
            return False
        else:
            return True

    def check(self) -> None:
        """Runs the checking procedure by searching a TrEMBL server for
        entries by accession, and updating the trembl_accessions and
        trembl_pids attributes.
        """
        self.trembl_accessions = _query_trembl(self.accessions, format="list").split()
        self._check_secondary_accessions()

    def _check_secondary_accessions(self) -> None:
        """Checks that secondary accessions in the entries are valid.
        
        If the primary accession is not a TrEMBL accession, none of the
        secondary accessions should be present in TrEMBL either.

        If errors are found, the attribute entries_with_error is updated with
        a tuple of:
        (primary_accession: str, secondary_trembl_accessions: List[str])

        """
        for entry in self.entries:
            if entry.accessions[0] in self.trembl_accessions:
                continue  # Primary accession is in TrEMBL which is fine
            else:
                secondary_accessions = entry.accessions[1:]
                secondary_trembl_accessions = [
                    i for i in secondary_accessions if i in self.trembl_accessions
                ]
                if secondary_trembl_accessions:
                    self.entries_with_error.append(
                        (entry.accessions[0], secondary_trembl_accessions)
                    )


class TrEMBLAccessionChecker:
    """Checks accessions and protein ids in curated TrEMBL entries.

    Attributes:
        accessions: list of accessions in curated TrEMBL entries.
        pids: list of protein ids in curated TrEMBL entries.
        trembl_accessions: list of accessions in original TrEMBL entries.
        trembl_pids: list of EMBL protein ids in original TrEMBL entries.

    Methods:
        check: runs the checking procedure.
    """

    def __init__(self, trembl_files: TrEMBLFiles) -> None:
        self.accessions: List[str] = sorted(trembl_files.get_accessions())
        self.pids: List[str] = sorted(trembl_files.get_pids())
        self.trembl_accessions: List[str] = []
        self.trembl_pids: List[str] = []

    @property
    def ok(self) -> bool:
        """Signals whether errors have been detected in the files.

        Returns:
            bool: False if errors are found in the entries, otherwise True.
                Defaults to False if the check method has not been run yet.
        """
        if self.accessions == self.trembl_accessions and self.pids == self.trembl_pids:
            return True
        else:
            return False

    def check(self) -> None:
        """Runs the checking procedure by searching a TrEMBL server for
        entries by accession, and updating the trembl_accessions and
        trembl_pids attributes.
        """
        trembl_entries = _query_trembl(self.accessions, format="txt")
        self._get_trembl_identifiers(trembl_entries)

    def _get_trembl_identifiers(self, trembl_entries: str) -> None:
        """Gets accessions and protein ids from text of UniProt entries in
        flat-file format.
        
        Args:
            trembl_entries: one or more UniProt entries in text format.
        """
        handle = io.StringIO(trembl_entries)
        entries = list(parse_flatfile(handle))

        accessions = list(chain.from_iterable(x.accessions for x in entries))
        pids = list(chain.from_iterable(x.pids for x in entries))

        self.trembl_accessions = sorted(accessions)
        self.trembl_pids = sorted(pids)


def _query_trembl(accessions: List[str], format: str) -> str:
    """Searches TrEMBL server for UniProt entries based on accession.

    The server to use is set as an environment variable 'TREMBL_SERVER'.
    Normally this would be the internal TrEMBL server which contains the most
    up-to-date version of the database.

    Args:
        accessions: list of UniProt accessions to be passed as query
            parameter.
        format: format of matched UniProt entries (txt, fasta, xml, list are 
            valid formats).

    Returns:
        str: UniProt entries in flat file format.
    """
    server = os.environ["TREMBL_SERVER"]
    url = f"{server}/uniprot/?"
    query = f"id:{' OR id:'.join(i for i in accessions)}"
    params = {"query": query, "format": format}
    uniprot_query = requests.get(url, params=params)
    uniprot_query.raise_for_status()
    return uniprot_query.text
