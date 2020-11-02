import os

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

INFO_HELP = "Shows the number of files and entries in each folder."


@click.command(help=INFO_HELP)
def info():
    files = [
        LogFiles(),
        NewFiles(),
        PepFiles(),
        PidFiles(),
        SeqFiles(),
        SubFiles(),
        TrEMBLFiles(),
    ]

    for f in files:
        click.echo(f"{str(f)}\tfiles: {len(f)}\tentries: {len(f.get_entries())}")

    if jira_url := os.environ.get("JIRA_URL"):
        click.echo()
        click.echo(f"Don't forget to update the JIRA issue: {jira_url}")
