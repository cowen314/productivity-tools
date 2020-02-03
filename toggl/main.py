import typing, requests


class Toggl:
    _BASE_SUMMARY_URL = "https://toggl.com/reports/api/v2/summary"
    _WORKSPACES_URL = "https://www.toggl.com/api/v8/workspaces"
    _PASSWORD = "api_token"
    def __init__(self, api_key: str, workspace_id: int = None, user_agent: str = "api_test"):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.user_agent = user_agent

    def get_available_workspaces(self):
        return requests.get(self._WORKSPACES_URL, auth=(self.api_key, self._PASSWORD))

    def get_entries_1_day(self, date: str):
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
        return response


def main():
    """
    General strategy:
    - use toggl API to pull report data
        - a summary report that's grouped by project and subgrouped by time_entries should work (see https://github.com/toggl/toggl_api_docs/blob/master/reports/summary.md)
    - use gui automation tool to import time to timer
    """
    pass


if __name__=="__main__":
    main()