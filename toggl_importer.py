from datetime import date
from enum import Enum
from typing import Optional
import typer

from toggl.main import DmcTimerImporter, TextDumpImporter, generate_toggl_invoice_model, pull_and_import_single_day
from toggl.toggl_secrets import get_toggl_secrets
from toggl.paths import toggl_secrets_file

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
    ),
        slowdown_factor: float = typer.
    Argument(
        1,
        help=
        "A multiplier applied to import waits. Increase the value of this parameter to run the import process more slowly."
    )):
    """
    Pulls one day of data from the Toggl API, then moves it somewhere else. Where and how it's moved depends on `import-type`
    """
    print(f"Loading secrets from {toggl_secrets_file}")
    toggl_secrets = get_toggl_secrets()
    if api_key is None:
        print(f"No API key provided, attempting to load key from secrets file")
        api_key = toggl_secrets.api_key
        if not api_key:
            print("Invalid / blank API key found in secrets file")
            raise typer.Exit(code=1)

    if import_type == 'text-dump':
        importer = TextDumpImporter()
    elif import_type == 'dmc-timer':
        importer = DmcTimerImporter()
    else:
        raise ValueError(f"Unsupported importer ('{import_type}') specified")

    pull_and_import_single_day(date,
                               api_key,
                               importer=importer,
                               toggl_project_to_client_name_map=toggl_secrets.
                               toggl_project_to_client_name_map,
                               slowdown_factor=slowdown_factor)


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
    print(f"Loading secrets from {toggl_secrets_file}")
    toggl_secrets = get_toggl_secrets()
    if api_key is None:
        print(f"No API key provided, attempting to load key from secrets file")
        api_key = toggl_secrets.api_key
        if not api_key:
            print("Invalid / blank API key found in secrets file")
            raise typer.Exit(code=1)

    generate_toggl_invoice_model()


if __name__ == "__main__":
    app()