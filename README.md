# sending

A command-line tool for preparing and sending curated files for integration.

Runs several sanity checks on the files (including syntax checkers), does the FTP transfers, and backs up the files and cleans the submission directories.

## Requirements

- Python 3.7 or higher (the [Anaconda](https://www.anaconda.com/products/individual)/[Miniconda](https://docs.conda.io/en/latest/miniconda.html) python distribution is recommended).
- UniProt curation environment, which includes the syntax checker scripts.
- FTP credentials for connecting to the remote server.

## Installation

Ideally the package should be installed into a clean virtual environment. This command creates a conda environment named "sending":

```cmd
conda create --name sending
```

Activte the new environment:

```cmd
conda activate sending
```

Finally, install the sending package into the environment:

```cmd
conda install --channel ehatton sending
```

## Configuration

Environment variables are used to configure the location of submission directories and other resources. A full list of [required environment variables](#required-environment-variables) can be found in the section below. The easiest way to implement this is to use a batch script to set all the environment variables, activate the python environment and open a cmd shell.

## Usage

There are four commands for the checking, information, sending and backup stages.

1. To run checks on the files, use the __check__ command.

    ```cmd
    sending check
    ```

    This automatically runs the syntax checkers on all files.

    It also checks for valid accessions in newly curated entries.

    For curated TrEMBL entries, it will check that the accessions and protein ids match the original TrEMBL entries in the database.

    For pep and sub files, it checks that none of the secondary accessions are present in TrEMBL.

2. To view summary information about the files, use the __info__ command.

    ```cmd
    sending info
    ```

    This command lists the number of files, and the total number of entries created/updated, for each directory.

3. To execute the FTP transfer, use the __send__ command.

    ```cmd
    sending send
    ```

    This automatically transfers all the files to the remote FTP server. New entries are concatenated into a single file named allnew with a date stamp appended to the filename (e.g. allnew_20200707.swp).

4. To back up files and clean submission directories ready for the following week, use the __tidy__ command.

    ```cmd
    sending tidy
    ```

5. Help documentation is also available:

    ```cmd
    sending --help
    ```

## Required environment variables

Usage examples can be found in the [.env](/tests/.env) file in the tests folder.

### Folder locations

- LOG_DIR
- LOG_REMOTE_DIR
- TREMBL_DIR
- TREMBL_REMOTE_DIR
- NEW_DIR
- NEW_REMOTE_DIR
- PEP_DIR
- PEP_REMOTE_DIR
- SUB_DIR
- SUB_REMOTE_DIR
- PID_DIR
- PID_REMOTE_DIR
- SEQ_DIR
- SEQ_REMOTE_DIR

### Remote FTP server credentials

- REMOTE_HOST_NAME
- REMOTE_USER
- REMOTE_SERVER
- REMOTE_KEY
- KNOWN_HOSTS

### Server for retrieval of TrEMBL entries (required for accession checkers)

- TREMBL_SERVER

### Environment variables required by syntax checkers

- BINPROT
- PERLLIB
- SPROT
