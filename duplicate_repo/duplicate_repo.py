import argparse
import subprocess
from pathlib import Path
import json
import shutil
import urllib.parse
import posixpath
import datetime
import sys
from version import version

print("---REPO DUPLICATOR v%s---" % version)

TEMP_DIR_NAME = ".repo-duplicator"
CONFIG_FILENAME = "cloneconfig.json"  # FIXME this currently goes into the clone parent dir, not the
DEFAULT_CONFIG = {
    "default_namespace": "DMC/labview/",
    "default_template_url": "https://git.dmcinfo.com/DMC/labview/dmc-templates/labview-template-project.git",
    "default_dest_base_url": "https://git.dmcinfo.com/"
}
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):  # if in the context of a PyInstaller bundled application
    EXE_DIR = Path(sys._MEIPASS)
else:
    EXE_DIR = Path(__file__).parent


def exit_with_error(msg: str, running_as_wizard: bool):
    if not running_as_wizard:
        sys.exit(str)
    else:
        input("FAIL: %s\nPress enter to exit." % msg)
        sys.exit("Exiting...")


def call_cli(command: str, running_as_wizard: bool, cwd: Path, pre_msg: str = None, custom_err_msg: str = None):
    if pre_msg:
        print(" > %s" % pre_msg)
    po = subprocess.run(
        command.split(" "),
        capture_output=True,
        cwd=cwd)
    if po.returncode > 0:
        if custom_err_msg:
            exit_with_error(" > ERROR: %s\n > %s" % (po.stderr.decode('ascii'), custom_err_msg), running_as_wizard)
        else:
            exit_with_error(" > ERROR: " + po.stderr.decode('ascii'), running_as_wizard)
    elif len(po.stdout) > 0:
        print(po.stdout.decode('ascii'))
    print("---")


# read in config file, create a new one if none exists
CONFIG_PATH = Path.cwd() / EXE_DIR / CONFIG_FILENAME
try:
    with open(CONFIG_PATH) as fh:
        config = json.load(fh)
except Exception as e:
    config = DEFAULT_CONFIG
    try:
        CONFIG_PATH.touch()
        with open(CONFIG_PATH, "w") as fh:
            json.dump(config, fh, indent=4, sort_keys=True)
    except PermissionError:
        print(" > INFO: No permission to create '%s'. This is OK for most cases. Run as an admin if a config file is needed.\n" % CONFIG_PATH)

# set up command line interface
parser = argparse.ArgumentParser()
parser.add_argument('--project-name', help="Name of the new Gitlab project. Required when creating a new project/repo.", dest="project_name")
parser.add_argument('--namespace', help="Namespace of the project on Gitlab (default: %s)" % config["default_namespace"], default=config["default_namespace"])
parser.add_argument('--template-url', help="Template repository to copy to the newly created repo (default: %s)" % config["default_template_url"], default=config["default_template_url"], dest="template_url")
parser.add_argument('--target-path', help="Local path to copy files into", default=".", dest="target_path")
parser.add_argument('--dest-base-url', help="URL base for the new Gitlab repo / project. This URL should not contain the namespace or project. (default: %s)" % config["default_dest_base_url"], default=config["default_dest_base_url"], dest="dest_base_url")
parser.add_argument("--wizard", help="Run this tool with a wizard to walk through setting parameters.", action="store_true")

# parse args
args = parser.parse_args()
if not args.project_name:
    args.wizard = True  # set the wizard true if no project name
    # exit_with_error("Must supply either a project name, or set the --wizard flag to true", args.wizard)

# if the wizard flag was set, run the user through the wizard
if args.wizard:
    args.project_name = input(" > Enter the name of your repo / project: ")  # TODO add check for invalid chars
    if args.project_name.strip() == "":
        exit_with_error(" > Invalid project name", args.wizard)
    ns = input(" > Enter the project namespace (usually this has the format '<customerName>/', for example 'MyGreatCustomer/'; leave blank for default: '%s'): " % config["default_namespace"])
    if ns.strip() != "":
        args.namespace = ns
    tr = input(" > Enter the template repository to copy to the newly created repo (leave blank for default: '%s'): "
               % config["default_template_url"])
    if tr.strip() != "":
        args.template_url = tr
    bu = input(" > Enter the URL base for the new Gitlab repo / project. This URL should not contain the namespace or "
               "project. (default: %s): " % config["default_dest_base_url"])
    if bu.strip() != "":
        args.dest_base_url = bu
    tp = input(" > Enter the local path to copy files into (leave blank for this directory): ")
    if tp.strip() != "":
        args.target_path = tp

target_path = Path(args.target_path) / TEMP_DIR_NAME
args.project_name = args.project_name.replace(" ", "-")  # clean the project name

# check paths
if target_path.exists() and len(list(target_path.glob("*"))) != 0:
    exit_with_error(" > ERROR: Files were found in the target directory. This tool will only work on a blank directory.", args.wizard)
target_path.mkdir(parents=True, exist_ok=True)

# clone some template repo into current repo (use subprocess), do it into a temp dir
call_cli("git clone %s" % args.template_url, args.wizard, target_path.resolve(), pre_msg="Cloning template from %s" % args.template_url)
# print("Cloning template from %s" % args.template_url)
# po = subprocess.run(
#     ["git", "clone", args.template_url],
#     capture_output=True,
#     cwd=target_path.resolve())
# if po.returncode > 0:
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# grab repo dir
repo_dir = list(target_path.glob("*"))[0]  # there should only be one folder at the target path after the clone

# pull lfs content
call_cli("git lfs pull", args.wizard, repo_dir.resolve(), pre_msg="Pulling LFS content")
# print("Pulling LFS content")
# po = subprocess.run(
#     ["git", "lfs", "pull"],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     # shutil.rmtree(repo_dir)
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# fetch deleted lfs content
call_cli("git lfs fetch --all", args.wizard, repo_dir.resolve(), pre_msg="Pulling LFS content")
# print("Pulling LFS content")
# po = subprocess.run(
#     ["git", "lfs", "fetch", "--all"],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# remove the remote ref
call_cli("git remote remove origin", args.wizard, repo_dir.resolve(), pre_msg="Removing original remote")
# po = subprocess.run(
#     ["git", "remote", "remove", "origin"],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     # shutil.rmtree(repo_dir)
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# hit the command to add a new repo to the remote
# (https://docs.gitlab.com/ee/gitlab-basics/create-project.html#push-to-create-a-new-project)
namespace_url = urllib.parse.urljoin(args.dest_base_url, args.namespace)
new_project_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name+".git"))

call_cli("git push --set-upstream %s master" % new_project_url, args.wizard, repo_dir.resolve(),
         pre_msg="Pushing to new project at %s" % new_project_url,
         custom_err_msg="Failed to create new repository (does it already exist? do you have proper permissions to "
                        "push to this group?")
# print("Pushing to new project at %s" % new_project_url)
# po = subprocess.run(
#     ["git", "push", "--set-upstream", new_project_url, "master"],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     # shutil.rmtree(repo_dir)
#     exit_with_error("ERROR: Failed to create new repository (does it already exist? do you have proper permissions to "
#                     "push to this group?)\n" + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# add ref to origin
call_cli("git remote add origin %s" % new_project_url, args.wizard, repo_dir.resolve(), pre_msg="Adding new remote")
# po = subprocess.run(
#     ["git", "remote", "add", "origin", new_project_url],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     # shutil.rmtree(repo_dir)
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

# add "initial" commit
# print("Adding initial commit")
init_file = repo_dir / "README.md"
init_file.touch()
with open(init_file, "a") as fh:
    fh.write("\n\n---\n\nThis project was created %s by copying %s." % (str(datetime.datetime.now()), args.template_url))
# call_cli("git commit -am 'REPO CREATOR (v%s): INIT'" % version, args.wizard, repo_dir.resolve(),
#          pre_msg="Adding initial commit")
po = subprocess.run(
    ["git", "commit", "-am", "REPO CREATOR (v%s): INIT" % version],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))
print("---")

call_cli("git push", args.wizard, repo_dir.resolve(), pre_msg="Pushing")
# print("Pushing")
# po = subprocess.run(
#     ["git", "push"],
#     capture_output=True,
#     cwd=repo_dir.resolve())
# if po.returncode > 0:
#     # shutil.rmtree(repo_dir)
#     exit_with_error("ERROR: " + po.stderr.decode('ascii'), args.wizard)
# elif len(po.stdout) > 0:
#     print(po.stdout.decode('ascii'))

print(" > Moving out of temporary directory")
repo_dir.rename(repo_dir.parent.parent / args.project_name)  # move up a directory, into appropriately named folder
(repo_dir.parent.parent / TEMP_DIR_NAME).rmdir()

new_project_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name))
project_settings_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name, "edit"))
print(" > SUCCESS: Repository created successfully!"
      "\n > URL of new project is %s."
      "\n > Project visibility is currently set to private, navigate to %s to update it."
      "\n > All code sourced from %s" % (new_project_url, project_settings_url, args.template_url))
if args.wizard:
    input(" > Press enter to exit")
