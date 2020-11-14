import argparse
import subprocess
import pathlib
import json
import shutil
import urllib.parse

DEFAULT_CONFIG = {
    "default_namespace": "DMC/labview/",
    "default_template_url": "https://git.dmcinfo.com/DMC/labview/template-project"
    "default_dest_base_url": "https://git.dmcinfo.com/"
}

try:
    config = json.load("cloneconfig.json")
except :
    config = DEFAULT_CONFIG

# set up command line interface
parser = argparse.ArgumentParser()
parser.add_argument('--project-name', help="Name of the new Gitlab project. Required when creating a new project/repo", dest="project_name")
parser.add_argument('--namespace', help="Namespace of the project on Gitlab (default: %s)" % config["default_namespace"], default=config["default_namespace"])
parser.add_argument('--template-url', help="Template repository to copy to the newly created repo (default: %s)" % config["default_template_url"], default=config["default_template_url"], dest="template_url")
# parser.add_argument('--local-path', help="Local path to copy files into", type=pathlib.Path, default=Path("."), dest="local_path")
parser.add_argument('--local-path', help="Local path to copy files into", default=".", dest="local_path")
parser.add_argument('--dest-base-url', help="URL base for the new Gitlab repo / project. This URL should not contain the namespace or project. (default: %s)" % config["default_dest_base_url"], default=config["default_dest_base_url"], dest="dest_base_url")

# parse args
args = parser.parse_args()
target_path = pathlib.Path(args.local_path)

# determine if the user is trying to create a repo from scratch, or just pull the template into an existing repo
# TODO do this later 
# print("Do you want to create a repo from scratch (press '1'), or move template files into an existing repo (press '2')?")
# res = input()
# if res == "1":
#     clone_existing = False
# elif res == "2":
#     clone_existing = True
# else
#     print("Invalid response ('%s') received. Exiting." % res)
if target_path.exists() and len(list(target_path.glob("*"))) != 0:
    print("WARN: Files were found in the target directory. This tool will only work on a blank directory.")
    return  # TODO return with error status
if not target_path.exists():
    target_path.touch()

# clone some template repo into current repo (use subprocess), do it into a temp dir
po = subprocess.run(
    ["git", "clone", args.template_url],
    capture_output=True,
    cwd=target_path.resolve())
    
# TODO check that things were cloned properly?

# remove the git dir, move the files from the main dir into the current dir
shutil.rmtree(target_path / ".git")

# do.... other stuff??

# TODO clone the gitattributes template from the gitattributes template repo
# hit the command to add a new repo to the remote (https://docs.gitlab.com/ee/gitlab-basics/create-project.html#push-to-create-a-new-project)
new_project_url = urllib.parse.urljoin(args.dest_base_url, args.namespace)
new_project_url = urllib.parse.urljoin(new_project_url, args.project_name)

print("Pushing to new URL: %s" % new_project_url)
po = subprocess.run(
    ["git", "push", "--set-upstream", new_project_url, "master"]
    capture_output=True,
    cwd=target_path.resolve())
# if ???:
#     print("WARN: unable to create repo on the remote: %s" % err)

# add and commit code?
# be sure to handle failures here
