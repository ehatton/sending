import click

from sending.curation_files import (
    LogFiles,
    NewFiles,
    PepFiles,
    PidFiles,
    SeqFiles,
    SubFiles,
    TrEMBLFiles,
)

TIDY_HELP = "Backs up files in 'old' and cleans submission directories."


@click.command(help=TIDY_HELP)
def tidy():
    """Main entry point for the tidy command.

    Backs up curation files in 'old' directories and cleans submission
    directories."""

    curated_files = [
        LogFiles(),
        TrEMBLFiles(),
        NewFiles(),
        PepFiles(),
        SubFiles(),
        PidFiles(),
        SeqFiles(),
    ]

    for files in curated_files:
        if files:
            try:
                click.secho(f"Moving {str(files)} to old directory.")
                files.backup()
                files.delete()
            except FileNotFoundError as err:
                click.secho("There was a problem backing up files", fg="red")
                click.echo(err)
                click.echo("---")
        else:
            click.secho(f"No {str(files)} subitted, skipping cleanup.")
            click.echo("---")
    click.secho("Backed up all files and cleaned submission directories.", fg="green")
