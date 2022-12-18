from pathlib import Path
from typing import Dict
from pydantic import BaseModel, ValidationError
from toggl.paths import toggl_secrets_file


class TogglSecrets(BaseModel):
    api_key: str
    toggl_project_to_client_name_map: Dict


def get_toggl_secrets() -> TogglSecrets:
    try:
        json_text = toggl_secrets_file.read_text()
        return TogglSecrets.parse_raw(json_text)
    except FileNotFoundError:
        print("Unable to read toggl secrets file. A new one will be created.")
    except ValidationError as ve:
        print("Validation error occurred while reading the secrets file. \
                Determine the differences between what is expected and \
                what is missing and replace. If you want to override the \
                old data, comment out the line below this and run again.")
        raise ve
    toggl_secrets_file.touch(mode=666, exist_ok=True)
    new_secrets = TogglSecrets(api_key="", toggl_project_to_client_name_map={})
    toggl_secrets_file.write_text(new_secrets.json())
    return new_secrets