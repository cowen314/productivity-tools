from datetime import date
from enum import Enum
from typing import Optional
import typer

from toggl.main import DmcTimerImporter, TextDumpImporter, pull_and_import_single_day
from toggl.toggl_secrets import get_toggl_secrets

app = typer.Typer(help="A tool for moving toggl data around")


@app.command()
def pull_and_import_one_day(
        date: str = typer.Argument(...,
                                   help="A string with the format YYYY-MM-DD"),
        api_key: str = typer.
    Argument(
        None,
        help=
        "Toggl API key. If none is provided, this command attempts to load one from a file called toggl_secrets.json."
    ),
        import_type: str = typer.
    Argument(
        "text-dump",
        help=
        "The type of importer to use. Possible values are 'text-dump' and 'dmc-timer'"
    )):
    """
    Pulls one day of data from the Toggl API, then moves it somewhere else. Where and how it's moved depends on `import-type`
    """
    if api_key is None:
        toggl_secrets = get_toggl_secrets()
        api_key = toggl_secrets.api_key
        if not api_key:
            print()

    if import_type == 'text-dump':
        importer = TextDumpImporter()
    elif import_type == 'dmc-timer':
        importer = DmcTimerImporter()
    else:
        raise ValueError(f"Unsupported importer ('{import_type}') specified")

    pull_and_import_single_day(date, api_key, importer=importer)


@app.command()
def generate_invoice_model(
        start_date: str = typer.Argument(
            ...,
            help="Start date for the invoice model with the format YYYY-MM-DD"
        ),
        end_date: str = typer.Argument(
            ...,
            help="End date for the invoice model with the format YYYY-MM-DD"),
        api_key: str = typer.
    Argument(
        None,
        help=
        "Toggl API key. If none is provided, this command attempts to load one from a file called toggl_secrets.json."
    )):
    """
    Generate an invoice model
    """
    if api_key is None:
        toggl_secrets = get_toggl_secrets()
        api_key = toggl_secrets.api_key


if __name__ == "__main__":
    app()