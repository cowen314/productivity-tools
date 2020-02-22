import requests, json, pyautogui, time
from typing import List, Dict
from abc import abstractmethod


class Toggl:
    _BASE_SUMMARY_URL = "https://toggl.com/reports/api/v2/summary"
    _WORKSPACES_URL = "https://www.toggl.com/api/v8/workspaces"
    _PASSWORD = "api_token"

    def __init__(self, api_key: str, workspace_id: int = None, user_agent: str = "api_test"):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.user_agent = user_agent

    def get_available_workspaces(self) -> List[Dict]:
        response_text = requests.get(self._WORKSPACES_URL, auth=(self.api_key, self._PASSWORD)).text
        return json.loads(response_text)

    def get_entries_1_day(self, date: str) -> Dict:
        """
        @param date: a string in the format 'YYYY-MM-DD'
        """
        response = requests.get(
            "%s?user_agent=%s&workspace_id=%s&since=%s&until=%s" % (
                self._BASE_SUMMARY_URL,
                self.user_agent,
                self.workspace_id,
                date,
                date
            ),
            auth=(self.api_key, self._PASSWORD)
        )
        return json.loads(response.text)


class TimeEntry:
    def __init__(self, client_and_project: str = None, service_item: str = None, task: str = None, time_ms: int = None, description: str = None):
        """
        @param client_and_project: the client and project in the form <client>:<project>
        """
        self.client_and_project = client_and_project
        self.service_item = service_item
        self.task = task
        self.time_ms = time_ms
        self.description = description


class _EntryParser:
    @abstractmethod
    def parse_summary_entry_data(self, daily_data: Dict):
        """
        @param daily_data: data for a single day
        """
        raise NotImplementedError


class ExampleParser(_EntryParser):
    def __init__(self, toggl_project_to_client_name_map: Dict[str, str] = {}):
        self._toggl_project_to_client_name_map = toggl_project_to_client_name_map

    def parse_summary_entry_data(self, daily_data: Dict):
        time_entries = []
        for project in daily_data['data']:
            # get client name 
            client_name = project['title']['project']  # I store client in toggl project name field
            if client_name and client_name in self._toggl_project_to_client_name_map:  # sometimes, the client name in toggl is slightly different than the actual client name
                client_name = self._toggl_project_to_client_name_map[client_name]

            # loop through entries for that client
            # for now, I'll just add a new entry for each entry in toggl
            # at some point, might want to intelligently combine entries
            for toggl_info in project['items']:
                entry = TimeEntry()

                toggl_entry_info = toggl_info['title']['time_entry'].split('|')
                if len(toggl_entry_info) == 3:
                    if client_name:
                        entry.client_and_project = "%s:%s" % (client_name, toggl_entry_info[0])
                    else:
                        entry.client_and_project = toggl_entry_info[0]
                    entry.service_item = toggl_entry_info[1]
                    entry.description = toggl_entry_info[2]
                elif len(toggl_entry_info) == 2:
                    entry.client_and_project = ""
                    entry.service_item = toggl_entry_info[0]
                    entry.description = toggl_entry_info[1]
                elif len(toggl_entry_info) == 1:
                    entry.description = toggl_entry_info[0]
                entry.time_ms = toggl_info['time']
                time_entries.append(entry)
        return time_entries


class _EntryImporter:
    @abstractmethod
    def import_entries(self, entries: List[TimeEntry]):
        raise NotImplementedError


class ExampleEntryImporter(_EntryImporter):
    def import_entries(self, entries: List[TimeEntry]):
        pyautogui.alert("Open timer and set the correct date. Press OK when ready to auto import time. Slam mouse into one of the corners of the screen at any point to cancel the sequence.")
        time.sleep(3)
        for entry in entries:
            pyautogui.hotkey('ctrl', 'n')
            # pyautogui.alert("Click into `Project` field of newly created entry then press OK.")
            pyautogui.hotkey('f2')
            time.sleep(0.5)
            pyautogui.typewrite(entry.client_and_project, pause=0.01)
            time.sleep(0.5)
            pyautogui.hotkey('tab')
            pyautogui.typewrite(entry.service_item)
            pyautogui.hotkey('tab')
            if entry.task:
                pyautogui.typewrite(entry.task)
            pyautogui.hotkey('tab')
            if entry.time_ms:
                time_hrs = entry.time_ms / 1000.0 / 60 / 60
                time_hrs_rounded = ((float)((int) (time_hrs + 0.125) * 4)) / 4
                pyautogui.typewrite(str(time_hrs_rounded))
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.typewrite(entry.description)
            # pyautogui.hotkey('tab')
            pyautogui.hotkey('enter')
            # pyautogui.hotkey('tab')


def pull_and_import_single_day(date, api_key):
    """
    @param date: a string in the format 'YYYY-MM-DD'
    @param api_key: a Toggl API key

    General strategy:
    - use toggl API to pull report data
        - a summary report that's grouped by project and subgrouped by time_entries should work (see https://github.com/toggl/toggl_api_docs/blob/master/reports/summary.md)
    - use some automation tool to import time to timer
    """
    # grab raw data from the Toggl
    my_toggl = Toggl(api_key)
    workspaces = my_toggl.get_available_workspaces()
    print(workspaces)
    time.sleep(1)  # max 1 request per second to toggl's API
    my_toggl.workspace_id = workspaces[0]["id"]
    data = my_toggl.get_entries_1_day(date)
    print(data)

    # parse it to nicely formatted structure
    e = ExampleParser()
    parsed_data = e.parse_summary_entry_data(data)
    print(parsed_data)

    # import it
    importer = ExampleEntryImporter()
    importer.import_entries(parsed_data)


def main():
    # an example: 
    api_key = ""  # SET THIS TO YOUR API KEY (e.g. "4b5c6d7e8b8c8e9e8e7b7a6a1a3c5b4a"). Find it at https://toggl.com/app/profile.
    pull_and_import_single_day("2020-02-05", api_key)


if __name__ == "__main__":
    main()