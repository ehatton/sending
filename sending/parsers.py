from dataclasses import dataclass
from typing import IO, Iterator, List


@dataclass
class Entry:
    """Simple representation of a UniProt entry.

    Attributes:
        accessions: list of UniProt accessions.
        pids: list of EMBL protein IDs.

    """

    accessions: List[str]
    pids: List[str]


def parse_flatfile(filehandle: IO) -> Iterator[Entry]:
    """Iterator which converts UniProt flatfile text into Entry objects.

    Args:
        filehandle: a file-like object which streams UniProt entries in text
                      format.

    Yields:
        Entry: object representing UniProt entries.
    """
    acs, pids = [], []
    for line in filehandle:
        if line.startswith("AC"):
            tokens = line[5:].strip(";\n").split("; ")
            acs += tokens
        elif line.startswith("DR   EMBL"):
            tokens = line[5:].strip(";\n").split("; ")
            pid = tokens[2]
            if pid != "-":
                pids.append(pid)
        elif line == "//\n":
            yield Entry(acs, pids)
            acs, pids = [], []


def parse_logfile(filehandle: IO) -> Iterator[Entry]:
    """Iterator which converts UniProt logfile text into Entry objects.

    Since logfiles do not contain the full text of a UniProt entry, the 
    accessions field of the entry object only contains the primary
    accession and the pids field is an empty list.

    Args:
        filehandle: a file-like object which streams text of a logfile.
    
    Yields:
        Entry: an Entry object.
    """
    accessions = []
    for line in filehandle:
        if line.startswith("AC:"):
            # The accession is in the next line.
            acc = next(filehandle).strip()
            accessions.append(acc)
        elif line == "//\n":
            yield Entry(accessions, [])
            accessions = []
