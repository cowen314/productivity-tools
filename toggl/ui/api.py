"""

- A simple application that allows the user to pull time from Toggl for import (by gui automation into a timer application)
- Features:
    - allow the user to define their own API key
        - this key should be saved on user side
    - allow user to view their workspaces and to choose one to pull time from
    - allow user to specify their own parser plugin or gui automation tool
- Implementation
    - define controller on python side
    - define single screen for user interaction
- Look into
    - can we make writing the HTML easy? Templating lang? Drag and drop?



"""

from flask import Flask, render_template, request
from typing import List, Tuple, Iterable
from requests import get
from toggl.main import pull_and_import_single_day, Toggl, ExampleParser, DmcTimerImporter
from toggl.private_data import api_key
from random import random

'''
my_toggl = Toggl(api_key)

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
'''

'''Set up the application'''
# TODO figure out how flask apps are usually started and set up, then move this code there
app = Flask(__name__, template_folder='./')
toggl = Toggl(api_key)


@app.route("/")
def home():
    return render_template("ui.html")


@app.route("/workspaces")
def get_workspaces():
    toggl.get_available_workspaces()
    return
    # TODO return some block of HTML


@app.route("/update_component")
def update_component():
    component_id = request.headers.get('componentId')  # it'd be nice if we could define in one place (that'd apply to front and backend stuff)
    if not component_id:
        return "A component header could not be found.", 400

    if component_id == "workspaces":
        return render_template("./templates/components/workspaces.html", test_str=str(random()))
    else:
        return "The component '%s' could not be found." % component_id, 400


"""
Taken from a comment I made on 2020-02-18:
Just a thought here: what if we could add values to container classes on the
 Python side then, when a request came in, we could use those containers to populate
  values in some HTML and respond with the updated HTML? 
  That would solve our problem, right? There'd be control references on the 
  Python side, and the client wouldn't have to do more than request some new information
   for a particular control or group of controls.

TODO : TRY THIS FOR THE WORKSPACES ENDPOINT

"""


@app.route("/apiKey", methods=['GET', 'PUT'])
def api_key():
    if request.method == 'PUT':
        pass  # TODO save the key


if __name__ == "__main__":
    print("about to start the flask app...")
    app.run(host="127.0.0.1", port=5001)