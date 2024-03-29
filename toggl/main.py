from datetime import date, datetime
from pydantic import BaseModel
import requests, json, pyautogui, time
from typing import List, Dict, Iterable, Callable, Optional
from abc import abstractmethod


class Toggl:
    _BASE_SUMMARY_URL = "https://api.track.toggl.com/reports/api/v2/summary"
    _WORKSPACES_URL = "https://api.track.toggl.com/api/v8/workspaces"
    _PASSWORD = "api_token"

    def __init__(self,
                 api_key: str,
                 workspace_id: Optional[int] = None,
                 user_agent: str = "api_test"):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.user_agent = user_agent

    def get_available_workspaces(self) -> List[Dict]:
        response_text = requests.get(self._WORKSPACES_URL,
                                     auth=(self.api_key, self._PASSWORD)).text
        return json.loads(response_text)

    def get_entries_1_day(self, date: str) -> Dict:
        """
        @param date: a string in the format 'YYYY-MM-DD'
        """
        response = requests.get(
            "%s?user_agent=%s&workspace_id=%s&since=%s&until=%s" %
            (self._BASE_SUMMARY_URL, self.user_agent, self.workspace_id, date,
             date),
            auth=(self.api_key, self._PASSWORD))
        return json.loads(response.text)

    def get_entries_multiple_days(self, since_date: str,
                                  until_date: str) -> Dict:
        response = requests.get(
            "%s?user_agent=%s&workspace_id=%s&since=%s&until=%s" %
            (self._BASE_SUMMARY_URL, self.user_agent, self.workspace_id,
             since_date, until_date),
            auth=(self.api_key, self._PASSWORD))
        return json.loads(response.text)


class TimeEntry:

    def __init__(self,
                 client_and_project: Optional[str] = None,
                 service_item: Optional[str] = None,
                 task: Optional[str] = None,
                 time_ms: Optional[int] = None,
                 description: Optional[str] = None,
                 date: Optional[date] = None):
        """
        @param client_and_project: the client and project in the form <client>:<project>
        """
        self.client_and_project = client_and_project
        self.service_item = service_item
        self.task = task
        self.time_ms = time_ms
        self.description = description
        self.date = date

    def __str__(self):
        return "c&p: %s; service_item: %s; task: %s; time_hr: %.2f; desc: %s" % (
            self.client_and_project, self.service_item, self.task,
            self.time_ms / 60000 / 60, self.description)


class _EntryParser:

    @abstractmethod
    def parse_summary_entry_data(self,
                                 daily_data: Dict) -> Iterable[TimeEntry]:
        """
        @param daily_data: data for a single day
        """
        raise NotImplementedError


def _merge_entry(entries: Iterable[TimeEntry],
                 new_entry: TimeEntry) -> Iterable[TimeEntry]:
    entries = list(entries)  # make a value copy of entries
    # if new_entry.client_and_project:
    found_matching = False
    for existing_entry in entries:
        if existing_entry.client_and_project == new_entry.client_and_project and \
                existing_entry.service_item == new_entry.service_item and \
                existing_entry.task == new_entry.task and \
                existing_entry.date == new_entry.date:
            existing_entry.time_ms += new_entry.time_ms
            existing_entry.description += " " + new_entry.description
            found_matching = True
            break
        # if not existing_entry.client_and_project and \
        #         not new_entry.client_and_project and \
        #         existing_entry.service_item == new_entry.service_item and \
        #
    if not found_matching:
        entries.append(new_entry)
    # else:
    #     entries.append(new_entry)
    return entries


class ExampleParser(_EntryParser):

    def __init__(self,
                 toggl_project_to_client_name_map: Dict[str, str] = {},
                 toggl_project_name_map: Dict[str, str] = {}):
        self._toggl_project_to_client_name_map = toggl_project_to_client_name_map
        self._toggl_project_name_map = toggl_project_name_map

    def parse_summary_entry_data(self,
                                 daily_data: Dict) -> Iterable[TimeEntry]:
        time_entries = []
        for project in daily_data['data']:
            # get client name
            client_name = project['title'][
                'project']  # I store client in toggl project name field
            if client_name and client_name in self._toggl_project_to_client_name_map:  # sometimes, the client name in toggl is slightly different than the actual client name
                client_name = self._toggl_project_to_client_name_map[
                    client_name]

            # loop through entries for that client
            for toggl_info in project['items']:
                entry = TimeEntry()

                entry.date = datetime.fromisoformat(
                    toggl_info['local_start']).date()

                toggl_entry_info = toggl_info['title']['time_entry'].split('|')
                if len(toggl_entry_info) == 3 or len(toggl_entry_info) == 4:
                    if client_name:
                        project_name = toggl_entry_info[0]
                        if project_name in self._toggl_project_name_map:
                            project_name = self._toggl_project_name_map[
                                project_name]
                        if client_name != "":
                            entry.client_and_project = "%s:%s" % (client_name,
                                                                  project_name)
                        else:
                            entry.client_and_project = "%s" % project_name
                    else:
                        entry.client_and_project = toggl_entry_info[0]
                    if len(toggl_entry_info) == 3:
                        entry.service_item = toggl_entry_info[1]
                        entry.description = toggl_entry_info[2]
                    if len(toggl_entry_info) == 4:
                        entry.service_item = toggl_entry_info[1]
                        entry.task = toggl_entry_info[2]
                        entry.description = toggl_entry_info[3]
                elif len(toggl_entry_info) == 2:
                    entry.client_and_project = ""
                    entry.service_item = toggl_entry_info[0]
                    entry.description = toggl_entry_info[1]
                elif len(toggl_entry_info) == 1:
                    entry.description = toggl_entry_info[0]
                entry.time_ms = toggl_info['time']
                time_entries = _merge_entry(time_entries, entry)
        return time_entries


class _EntryImporter:

    @abstractmethod
    def import_entries(self,
                       entries: Iterable[TimeEntry],
                       skip_logic: Callable[[str, str], bool],
                       slowdown_factor: float = 1):
        raise NotImplementedError


class DmcTimerImporter(_EntryImporter):

    def import_entries(self,
                       entries: Iterable[TimeEntry],
                       skip_logic: Callable[[str, str], bool],
                       slowdown_factor: float = 1):
        pyautogui.alert(  # type: ignore
            "Open timer and set the correct date. Press OK when ready to auto import time. Slam mouse into one of the corners of the screen at any point to cancel the sequence."
        )
        time.sleep(slowdown_factor * 1.25)
        for entry in entries:
            if skip_logic(entry.client_and_project, entry.service_item):
                print("Skipped: " + str(entry))
                continue
            time_hrs_rounded = None
            if entry.time_ms:
                time_hrs = entry.time_ms / 1000.0 / 60 / 60
                # time_hrs_rounded = (float(int((time_hrs + 0.125) * 4))) / 4  # convert to hours, round to the nearest 15 minute increment

                # **rounding logic**
                # Anything from 0-15 minutes is billed at 15 minutes (I add a 1 minute buffer to remove tiny entries)
                # 3-minute buffer: 33 minutes gets rounded down to 30, 34 minutes is rounded up to 45 minutes.
                if time_hrs < 0.25 and time_hrs * 60 > 1:
                    time_hrs_rounded = 0.25
                else:
                    nearest_quarter_floor = float(int((time_hrs) * 4)) / 4
                    minutes_over_nearest_floor = (time_hrs -
                                                  nearest_quarter_floor) * 60
                    time_hrs_rounded = nearest_quarter_floor
                    if minutes_over_nearest_floor > 3:
                        time_hrs_rounded += 0.25

                if time_hrs_rounded <= 0:
                    print("Skipped: " + str(entry) + ". Insufficient time.")
                    continue
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(slowdown_factor * 2)
            pyautogui.hotkey('f2')
            time.sleep(slowdown_factor * 1)
            if entry.client_and_project:
                pyautogui.typewrite(entry.client_and_project[0])
                # pyautogui.alert("Press OK when dropdown shows up")
                time.sleep(slowdown_factor * 2)
                pyautogui.typewrite(entry.client_and_project[1:])
                time.sleep(slowdown_factor * 0.6)
            pyautogui.hotkey('tab')
            if entry.service_item and len(entry.service_item) > 0:
                pyautogui.typewrite(entry.service_item)
                time.sleep(slowdown_factor * 0.1)
            pyautogui.hotkey('tab')
            if entry.task and len(entry.task) > 0:
                pyautogui.typewrite(entry.task)
                time.sleep(slowdown_factor * 0.25)
            pyautogui.hotkey('tab')
            if time_hrs_rounded:
                pyautogui.typewrite(str(time_hrs_rounded))
                time.sleep(slowdown_factor * 0.1)
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            pyautogui.hotkey('tab')
            if entry.description:
                pyautogui.typewrite(entry.description)
                time.sleep(slowdown_factor * 2)
            pyautogui.hotkey('enter')
            time.sleep(slowdown_factor * 3)
        pyautogui.alert("Time entry complete")  # type: ignore


class TextDumpImporter(_EntryImporter):

    def import_entries(self,
                       entries: Iterable[TimeEntry],
                       skip_logic: Callable[[str, str], bool],
                       slowdown_factor: float = 1):
        i = 1
        for entry in entries:
            time_hrs_rounded = 0
            if entry.time_ms:
                time_hrs = entry.time_ms / 1000.0 / 60 / 60
                # **rounding logic**
                # Anything from 0-15 minutes is billed at 15 minutes (I add a 1 minute buffer to remove tiny entries)
                # 3-minute buffer: 33 minutes gets rounded down to 30, 34 minutes is rounded up to 45 minutes.
                if time_hrs < 0.25 and time_hrs * 60 > 1:
                    time_hrs_rounded = 0.25
                else:
                    nearest_quarter_floor = float(int((time_hrs) * 4)) / 4
                    minutes_over_nearest_floor = (time_hrs -
                                                  nearest_quarter_floor) * 60
                    time_hrs_rounded = nearest_quarter_floor
                    if minutes_over_nearest_floor > 3:
                        time_hrs_rounded += 0.25
                if time_hrs_rounded <= 0:
                    # print("Skipped: " + str(entry) + ". Insufficient time.")
                    continue
            entry_str = "%s -- %s\t%s\t%s\t%.2f\n\t%s" % (
                i, entry.client_and_project, entry.service_item, entry.task,
                time_hrs_rounded, entry.description)
            print(entry_str)
            i += 1


# classes to support invoicing... these should stay in sync with the classes in the invoicing repo


class TimeItem(BaseModel):
    description: str
    hours: float
    date: date


class MaterialItem(BaseModel):
    description: str
    cost: float
    date: date


class InvoiceModel(BaseModel):
    time_items: List[TimeItem]
    date: date
    # material_items: List[MaterialItem]  # can add this later


def dump_entries_to_invoice_model(
        entries: Iterable[TimeEntry],
        skip_logic: Callable[[str, str], bool] = lambda x, y: False):
    '''
    - Dump entries to a model that can be imported by an invoice generator
    - by default, no entries are be skipped. To automatically skip entries, provide a value for skip_logic
    '''
    i = 1
    invoice_model = InvoiceModel(time_items=[], date=date.today())
    for entry in entries:
        if skip_logic(entry.client_and_project, entry.service_item):
            print("Skipped: " + str(entry))
            continue
        time_hrs_rounded = 0
        if entry.time_ms:
            time_hrs = entry.time_ms / 1000.0 / 60 / 60
            # **rounding logic**
            # Anything from 0-15 minutes is billed at 15 minutes (I add a 1 minute buffer to remove tiny entries)
            # 3-minute buffer: 33 minutes gets rounded down to 30, 34 minutes is rounded up to 45 minutes.
            if time_hrs < 0.25 and time_hrs * 60 > 1:
                time_hrs_rounded = 0.25
            else:
                nearest_quarter_floor = float(int((time_hrs) * 4)) / 4
                minutes_over_nearest_floor = (time_hrs -
                                              nearest_quarter_floor) * 60
                time_hrs_rounded = nearest_quarter_floor
                if minutes_over_nearest_floor > 3:
                    time_hrs_rounded += 0.25
            if time_hrs_rounded <= 0:
                # print("Skipped: " + str(entry) + ". Insufficient time.")
                continue
            invoice_model.time_items.append(
                TimeItem(description=entry.description,
                         hours=time_hrs_rounded,
                         date=entry.date))
    return invoice_model

    # for entry in entries:

    #     entry_str = "%s -- %s\t%s\t%s\t%.2f\n\t%s" % (
    #         i, entry.client_and_project, entry.service_item, entry.task,
    #         time_hrs_rounded, entry.description)
    #     print(entry_str)
    #     i += 1


def pull_and_import_single_day(
        date,
        api_key,
        importer: _EntryImporter = DmcTimerImporter(),
        # importer: _EntryImporter = TextDumpImporter(),
        toggl_project_to_client_name_map: Dict[str, str] = {},
        toggl_project_name_map: Dict[str, str] = {},
        skip_logic: Callable[[str, str], bool] = lambda cp, ser_it: False,
        slowdown_factor: float = 1):
    """
    @param date: a string in the format 'YYYY-MM-DD'
    @param api_key: a Toggl API key
    @param toggl_project_to_client_name_map: map of toggl project names to official client names, in case they are different
    @param toggl_project_name_map: map of toggl project name to official project name
    @param skip_logic: a function that takes parameters (client_and_project: str, service_item: str) and returns
        True if the any item meeting those conditions should be skipped and False otherwise
    @param slowdown_factor: a multiplier applied to import waits. Increase the value of this parameter to run the import process more slowly.
    @param importer: an importer to use to output parsed data

    General strategy:
    - use toggl API to pull report data
        - a summary report that's grouped by project and subgrouped by time_entries should work (see https://github.com/toggl/toggl_api_docs/blob/master/reports/summary.md)
    - use some automation tool to import time to timer

    """

    # grab raw data from the Toggl
    my_toggl = Toggl(api_key)
    workspaces = my_toggl.get_available_workspaces()
    # print(workspaces)
    time.sleep(1)  # max 1 request per second to toggl's API
    my_toggl.workspace_id = workspaces[0]["id"]
    data = my_toggl.get_entries_1_day(date)
    # print(data)

    # parse it to nicely formatted structure
    e = ExampleParser(toggl_project_to_client_name_map, toggl_project_name_map)
    parsed_data = e.parse_summary_entry_data(data)
    for day in parsed_data:
        print(day)
    print("---")
    # import it
    if type(importer) is not TextDumpImporter:
        ti = TextDumpImporter()
        ti.import_entries(parsed_data,
                          skip_logic,
                          slowdown_factor=slowdown_factor)
    importer.import_entries(parsed_data,
                            skip_logic,
                            slowdown_factor=slowdown_factor)


def generate_toggl_invoice_model(
        since_date: str,
        until_date: str,
        api_key,
        toggl_project_to_client_name_map: Dict[str, str] = {},
        toggl_project_name_map: Dict[str, str] = {},
        skip_logic: Callable[[str, str], bool] = lambda x, y: False):
    """
    @param date: a string in the format 'YYYY-MM-DD'
    @param api_key: a Toggl API key
    @param toggl_project_to_client_name_map: map of toggl project names to official client names, in case they are different
    @param toggl_project_name_map: map of toggl project name to official project name
    @param skip_logic: a function that takes parameters (client_and_project: str, service_item: str) and returns
        True if the any item meeting those conditions should be skipped and False otherwise

    General strategy:
    - use toggl API to pull report data
        - a summary report that's grouped by project and subgrouped by time_entries should work (see https://github.com/toggl/toggl_api_docs/blob/master/reports/summary.md)
    - use importer to generate a model for invoices

    """
    # grab raw data from the Toggl
    my_toggl = Toggl(api_key)
    workspaces = my_toggl.get_available_workspaces()
    print(workspaces)
    time.sleep(1)  # max 1 request per second to toggl's API
    my_toggl.workspace_id = workspaces[0]["id"]
    data = my_toggl.get_entries_multiple_days(since_date, until_date)
    print(data)

    # parse it to nicely formatted structure
    e = ExampleParser(toggl_project_to_client_name_map, toggl_project_name_map)
    parsed_data = e.parse_summary_entry_data(data)
    for day in parsed_data:
        print(day)
    print("---")
    # import it
    return dump_entries_to_invoice_model(entries=parsed_data)
    # importer.import_entries(parsed_data,
    #                         skip_logic,
    #                         slowdown_factor=slowdown_factor)


def main():
    # an example:
    api_key = ""  # SET THIS TO YOUR API KEY (e.g. "4b5c6d7e8b8c8e9e8e7b7a6a1a3c5b4a"). Find it at https://toggl.com/app/profile.
    pull_and_import_single_day("2020-02-05", api_key)


if __name__ == "__main__":
    main()
