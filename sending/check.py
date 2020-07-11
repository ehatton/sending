from subprocess import CalledProcessError
from typing import List, Union

import click

from sending.accession_checkers import NewAccessionChecker, TrEMBLAccessionChecker
from sending.curation_files import (
    LogFiles,
    NewFiles,
    PepFiles,
    PidFiles,
    SeqFiles,
    SubFiles,
    TrEMBLFiles,
)
from sending.syntax_checkers import FlatFileChecker, LogFileChecker
from sending.utils import use_tempdir

CHECK_SHORT_HELP = "Runs checks on files."

CHECK_HELP = """Runs syntax checkers on logfiles and flatfiles. Also checks accessions
and PIDs in TrEMBL entries and new files.
"""


@click.command(help=CHECK_HELP, short_help=CHECK_SHORT_HELP)
def check() -> None:
    """Main entry point for the check command.
    """

    # Check logfile (*.log) syntax.
    logfiles = LogFiles()
    _check_logfiles(logfiles)

    # Check flat file (*.new, *.pep, *.sub, *.pid, *.seq) syntax.
    tremblfiles = TrEMBLFiles()
    newfiles = NewFiles()
    pepfiles = PepFiles()
    subfiles = SubFiles()
    pidfiles = PidFiles()
    seqfiles = SeqFiles()

    for flatfiles in (tremblfiles, newfiles, pepfiles, subfiles, pidfiles, seqfiles):
        _check_flatfile(flatfiles)

    # Check accessions and protein IDs in TrEMBL entries
    _check_trembl_accessions(tremblfiles)

    # Check secondary accessions in new entries
    _check_new_accessions([newfiles, pepfiles, subfiles])


@use_tempdir
def _check_logfiles(logfiles: LogFiles) -> None:
    """Runs syntax checker on logfiles and diplays the result to the user.

    Args:
        logfiles: LogFiles object.
    """
    if logfiles:
        click.secho(f"Checking {str(logfiles)}, please wait...")
        logfiles.write_files("all.log", mode="w")

        logfile_checker = LogFileChecker("all.log")
        try:
            logfile_checker.check()
            if logfile_checker.ok:
                click.secho(f"{str(logfiles)} passed syntax checks.", fg="green")
            else:
                click.secho(f"Errors detected in {str(logfiles)}", fg="red")
                click.echo(logfile_checker.error_report)
        except CalledProcessError as err:
            click.secho(
                f"LogFile checker exited with error code {err.returncode}:", fg="red"
            )
            click.echo(f"{err.stderr}")
    else:
        click.secho(f"No {str(logfiles)} to check.")
    click.echo("---")


@use_tempdir
def _check_flatfile(
    flatfiles: Union[TrEMBLFiles, NewFiles, PidFiles, SeqFiles]
) -> None:
    """Runs syntax checker on flatfiles and displays the result to the user.

    Args:
        flatfiles: flatfile-type CurationFiles object (i.e. everything
            except logfiles).
    """
    if flatfiles:
        click.secho(f"Checking {str(flatfiles)}, please wait...")
        flatfiles.write_files("allnew")

        flatfile_checker = FlatFileChecker("allnew")
        try:
            flatfile_checker.check()
            if flatfile_checker.ok:
                click.secho(f"{str(flatfiles)} passed syntax checks.", fg="green")
            else:
                click.secho(
                    f"{str(flatfiles)} failing syntax checks, please review.", fg="red"
                )
                click.echo(flatfile_checker.error_report)
        except CalledProcessError as err:
            click.secho(
                f"FlatFile checker exited with error code {err.returncode}", fg="red"
            )
            click.echo(f"{err.stderr}")
    else:
        click.secho(f"No {str(flatfiles)} to check.")
    click.echo("---")


def _check_trembl_accessions(tremblfiles: TrEMBLFiles) -> None:
    """Runs TrEMBL accession checker on curated TrEMBL entries and displays the
    result to the user.

    Args:
        tremblfiles: TrEMBLFiles object.
    """
    if tremblfiles:
        click.secho(f"Checking accessions and protein ids in {str(tremblfiles)}...")
        trembl_checker = TrEMBLAccessionChecker(trembl_files=tremblfiles)
        trembl_checker.check()
        if trembl_checker.ok:
            click.secho(
                "Correct accessions and protein ids in TrEMBL entries.", fg="green"
            )
        else:
            click.secho(
                "Wrong accessions and/or protein ids in TrEMBL entries.", fg="red"
            )
        click.echo(
            f"Accessions in curated entries:\t{' '.join(i for i in trembl_checker.accessions)}"
        )
        click.echo(
            f"Accessions in TrEMBL entries:\t{' '.join(i for i in trembl_checker.trembl_accessions)}"
        )
        click.echo(
            f"Protein ids in curated entries:\t{' '.join(i for i in trembl_checker.pids)}"
        )
        click.echo(
            f"Protein ids in TrEMBL entries:\t{' '.join(i for i in trembl_checker.trembl_pids)}"
        )
    else:
        click.echo(
            f"No {str(tremblfiles)} submitted, skipping accession and PID checks."
        )
    click.echo("---")


def _check_new_accessions(newfiles: List[Union[NewFiles, PepFiles, SubFiles]]) -> None:
    """Runs new accession checker on new entries and displays the result to the
    user.

    Args:
        newfiles: list of NewFiles, PepFiles and/or SubFiles objects.
    """

    for f in newfiles:
        if f:
            click.echo(f"Checking secondary accessions in {str(f)}...")
            new_checker = NewAccessionChecker(f)
            new_checker.check()
            if new_checker.ok:
                click.secho(f"Valid secondary accessions in {str(f)}.", fg="green")
            else:
                click.secho(
                    f"Found invalid secondary accessions in {str(f)}.", fg="red"
                )
                for error in new_checker.entries_with_error:
                    accession, invalid_accessions = error
                    click.echo(
                        f"{accession}: {' '.join(i for i in invalid_accessions)}"
                    )
            click.echo("---")

        else:
            click.echo(f"No {str(f)} to check, skipping accession checks.")
            click.echo("---")
