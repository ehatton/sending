import os

import click

from sending.check import check
from sending.send import send
from sending.tidy import tidy

CLI_HELP = "Tools for checking and sending curated files."


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


# Add the various commands to the group.
cli.add_command(check)
cli.add_command(send)
cli.add_command(tidy)


if __name__ == "__main__":
    cli()
