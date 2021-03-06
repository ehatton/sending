import datetime
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import List, Union

import click
import paramiko

from sending.curation_files import (
    LogFiles,
    NewFiles,
    PepFiles,
    PidFiles,
    SeqFiles,
    SubFiles,
    TrEMBLFiles,
)

REMOTE_HOST_NAME = os.environ.get("REMOTE_HOST_NAME", "remote host")


SEND_HELP = "Sends all curated files to the remote FTP server."


@click.command(help=SEND_HELP)
def send() -> None:
    """Main entry point for send command.

    Sends all curated files to the remote FTP server.
    """

    # Load curation files objects
    trembl_files = TrEMBLFiles()
    new_files = NewFiles()
    pep_files = PepFiles()
    sub_files = SubFiles()
    logfiles = LogFiles()
    pid_files = PidFiles()
    seq_files = SeqFiles()

    # Load FTP credentials
    try:
        remote_server = os.environ["REMOTE_SERVER"]
        remote_user = os.environ["REMOTE_USER"]
        remote_key = os.environ["REMOTE_KEY"]
        known_hosts = os.environ["KNOWN_HOSTS"]
    except KeyError as err:
        raise click.ClickException(
            f"Could not detect an environment variable for {err}s."
        )

    # Create SFTP connection and do the transfers
    try:
        key = paramiko.Ed25519Key.from_private_key_file(remote_key)
    except FileNotFoundError as err:
        raise click.ClickException(
            f"There was a problem loading the remote key file, please check your configuration:\n{err}"
        )

    try:
        hostkeys = paramiko.HostKeys(filename=known_hosts)
        hkey = hostkeys[remote_server]["ecdsa-sha2-nistp256"]
    except FileNotFoundError as err:
        raise click.ClickException(
            f"There was a problem loading the known hosts file, please check your configuration:\n{err}"
        )
    except KeyError as err:
        raise click.ClickException(f"Host {str(err)} not found in known_hosts file.")

    transport = paramiko.Transport((remote_server, 22))
    transport.connect(username=remote_user, pkey=key, hostkey=hkey)
    with paramiko.SFTPClient.from_transport(transport) as sftp:
        new_entries = [trembl_files, new_files, pep_files, sub_files]
        _send_new_entries(new_entries, sftp)
        for updates in [logfiles, pid_files, seq_files]:
            _send_updates(updates, sftp)
    transport.close()


def _send_updates(
    files: Union[LogFiles, PidFiles, SeqFiles], sftp: paramiko.SFTPClient
) -> None:
    """Sends update files to the remote FTP server.
    
    This function is used for logfiles, pid update files and seq update files
    (*.log, *.pid, *.seq) which can be transferred directly with no further
    processing needed.
    
    Args:
        files: list of CurationFiles objects (LogFiles, PidFiles, SeqFiles).
        sftp: paramiko SFTPClient object.
    
    """
    if files:
        for f in files:
            localpath = str(f)
            remotepath = str(PurePosixPath(str(files.remote_dir), f.name))
            sftp.put(localpath=localpath, remotepath=remotepath)
            click.echo(f"Sent {f.name} to {files.remote_dir}")
        click.secho(f"Sent all {str(files)} to {REMOTE_HOST_NAME}.", fg="green")
        click.echo("---")
    else:
        click.echo(f"No {str(files)} to send.")
        click.echo("---")


def _send_new_entries(
    files: List[Union[TrEMBLFiles, NewFiles, PepFiles, SubFiles]],
    sftp: paramiko.SFTPClient,
) -> None:
    """Sends new entries to the remote FTP server. 
    
    "New entries" includes curated TrEMBL entries plus other new entries such
    as direct submissions. These files must be concatenated into a single file
    named "allnew" with a date stamp appended to the filename before transfer.

    A temporary directory is used to make the "allnew" file.
    
    Args:
        trembl_files: TrEMBLFiles object
        new_files: NewFiles object
        sftp: paramiko SFTPClient object
    """

    if any(files):
        date_string = datetime.date.today().strftime("%Y%m%d")
        # Remote directory is the same for all new files so just look at the
        # first object in the list
        remote_dir = files[0].remote_dir

        with tempfile.TemporaryDirectory() as tmp:
            # Concatenate new, sub and pep files to allnew
            allnew = Path(tmp, f"allnew_{date_string}.swp")
            for f in files:
                if f:
                    f.write_files(allnew, mode="a")
                    for file in f:
                        click.echo(
                            f"Adding file {file.name} to concatenated file {allnew.name}"
                        )
            # Transfer allnew file to remote server
            localpath = str(allnew)
            remotepath = str(PurePosixPath(str(remote_dir), allnew.name))
            sftp.put(localpath=localpath, remotepath=remotepath)
            click.echo(f"Sent {allnew.name} to {remote_dir}")
            click.secho(f"Sent all new files to {REMOTE_HOST_NAME}.", fg="green")
            click.echo("---")
    else:
        click.echo("No new files to send.")
        click.echo("---")
