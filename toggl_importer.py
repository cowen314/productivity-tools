from datetime import date
from enum import Enum
from typing import Optional
import typer

from toggl.main import DmcTimerImporter, TextDumpImporter, pull_and_import_single_day
from toggl.toggl_secrets import get_toggl_secrets


class ImportType(Enum):
    TEXT_DUMP = 0
    DMC_TIMER = 1


app = typer.Typer()


@app.command()
def pull_and_import_one_day(date: date, api_key: Optional[str], import_type: ImportType = ImportType.TEXT_DUMP):
    if api_key is None:
        toggl_secrets = get_toggl_secrets()
        api_key = toggl_secrets.api_key

    if import_type is ImportType.TEXT_DUMP:
        importer = TextDumpImporter()
    elif ImportType is ImportType.DMC_TIMER:
        importer = DmcTimerImporter()
    else:
        raise ValueError("Unsupported importer specified")

    pull_and_import_single_day(f"{date.year:04}-{date.month:02}-{date.day:02}", api_key, importer=importer)


@app.command()
def generate_invoice_model(start_date: date, end_date: date, api_key: Optional[str]):
    if api_key is None:
        toggl_secrets = get_toggl_secrets()
        api_key = toggl_secrets.api_key
    
    