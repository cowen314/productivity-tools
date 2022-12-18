from pathlib import Path
from pydantic import BaseModel, ValidationError
from toggl.paths import toggl_secrets_file


class TogglSecrets(BaseModel):
    api_key: str


def get_toggl_secrets() -> TogglSecrets:
    try:
        json_text = toggl_secrets_file.read_text()
        return TogglSecrets.parse_raw(json_text)
    except (FileNotFoundError, ValidationError):
        print("Unable to read toggl secrets file. A new one will be created.")
    toggl_secrets_file.touch(mode=666, exist_ok=True)
    new_secrets = TogglSecrets(api_key="")
    toggl_secrets_file.write_text(new_secrets.json())
    return new_secrets