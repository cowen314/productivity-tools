import argparse
import subprocess
import pathlib
import json
import shutil
import urllib.parse
import posixpath
import datetime

TEMP_DIR_NAME = ".repo-creator"
CONFIG_FILENAME = "cloneconfig.json"
DEFAULT_CONFIG = {
    "default_namespace": "DMC/labview/",
    "default_template_url": "https://git.dmcinfo.com/DMC/labview/labview-template-project.git",
    "default_dest_base_url": "https://git.dmcinfo.com/"
}

# read in config file, create a new one if none exists
try:
    with open(pathlib.Path(CONFIG_FILENAME)) as fh:
        config = json.load(fh)
except Exception as e:
    config = DEFAULT_CONFIG
    pathlib.Path(CONFIG_FILENAME).touch()
    with open(pathlib.Path(CONFIG_FILENAME), "w") as fh:
        json.dump(config, fh, indent=4, sort_keys=True)

# set up command line interface
parser = argparse.ArgumentParser()
parser.add_argument('--project-name', help="Name of the new Gitlab project. Required when creating a new project/repo.", dest="project_name", required=True)
parser.add_argument('--namespace', help="Namespace of the project on Gitlab (default: %s)" % config["default_namespace"], default=config["default_namespace"])
parser.add_argument('--template-url', help="Template repository to copy to the newly created repo (default: %s)" % config["default_template_url"], default=config["default_template_url"], dest="template_url")
parser.add_argument('--target-path', help="Local path to copy files into", default=".", dest="target_path")
parser.add_argument('--dest-base-url', help="URL base for the new Gitlab repo / project. This URL should not contain the namespace or project. (default: %s)" % config["default_dest_base_url"], default=config["default_dest_base_url"], dest="dest_base_url")

# parse args
args = parser.parse_args()
target_path = pathlib.Path(args.target_path) / TEMP_DIR_NAME
cleaned_project_name = args.project_name.replace(" ", "-")

# check paths
if target_path.exists() and len(list(target_path.glob("*"))) != 0:
    exit("ERROR: Files were found in the target directory. This tool will only work on a blank directory.")
target_path.mkdir(parents=True, exist_ok=True)

# clone some template repo into current repo (use subprocess), do it into a temp dir
print("Cloning template from %s" % args.template_url)
po = subprocess.run(
    ["git", "clone", args.template_url],
    capture_output=True,
    cwd=target_path.resolve())
if po.returncode > 0:
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

# grab repo dir
repo_dir = list(target_path.glob("*"))[0]  # there should only be one folder at the target path after the clone

# pull lfs content
print("Pulling LFS content")
po = subprocess.run(
    ["git", "lfs", "pull"],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

# remove the remote ref
po = subprocess.run(
    ["git", "remote", "remove", "origin"],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

# hit the command to add a new repo to the remote
# (https://docs.gitlab.com/ee/gitlab-basics/create-project.html#push-to-create-a-new-project)
namespace_url = urllib.parse.urljoin(args.dest_base_url, args.namespace)
new_project_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name+".git"))

print("Pushing to new project at %s" % new_project_url)
po = subprocess.run(
    ["git", "push", "--set-upstream", new_project_url, "master"],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: Failed to create new repository (does it already exist?)\n" + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

# add ref to origin
po = subprocess.run(
    ["git", "remote", "add", "origin", new_project_url],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

# add "initial" commit
print("Adding initial commit")
init_file = repo_dir / "README.md"
init_file.touch()
with open(init_file, "a") as fh:
    fh.write("\nThis project was created %s by copying %s." % (str(datetime.datetime.now()), args.template_url))
po = subprocess.run(
    ["git", "commit", "-am", "'REPO CREATOR: INIT'"],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

print("Pushing")
po = subprocess.run(
    ["git", "push"],
    capture_output=True,
    cwd=repo_dir.resolve())
if po.returncode > 0:
    # shutil.rmtree(repo_dir)
    exit("ERROR: " + po.stderr.decode('ascii'))
elif len(po.stdout) > 0:
    print(po.stdout.decode('ascii'))

print("Moving out of temporary directory")
repo_dir.rename(repo_dir.parent.parent / cleaned_project_name)  # move up a directory, into appropriately named folder
(repo_dir.parent.parent / TEMP_DIR_NAME).rmdir()

new_project_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name))
project_settings_url = urllib.parse.urljoin(args.dest_base_url, posixpath.join(args.namespace, args.project_name, "edit"))
print("SUCCESS: Repository created successfully!"
      "\nURL of new project is %s."
      "\nProject visibility is currently set to private, navigate to %s to update it."
      "\nAll code sourced from %s" % (new_project_url, project_settings_url, args.template_url))
