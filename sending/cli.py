import os

import click

from sending import __version__
from sending.check import check
from sending.send import send
from sending.info import info
from sending.tidy import tidy

CLI_HELP = "Tools for checking and sending curated files."


@click.version_option(version=__version__)
@click.group(help=CLI_HELP)
def cli():
    """Main entry point for sending program.
    """
    # Quick and dirty check to see if the user has loaded their configuration
    # (environment variables) before running the program.
    if os.getenv("LOG_DIR") is None:
        raise click.UsageError(
            "Environment variables not detected, aborting. Please refer to documentation on Confluence for configuration settings."
        )


cli.add_command(check)
cli.add_command(send)
cli.add_command(info)
cli.add_command(tidy)


if __name__ == "__main__":
    cli()
