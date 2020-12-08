from pathlib import Path
import os
import shutil
import subprocess
import traceback


# Define to install process
DIST_DIR = Path("./MyApp")  # TODO put a RELATIVE path to the distribution folder here
TARGET_DIR = Path(os.environ['PROGRAMFILES']) / "DeveloperName" / "AppName"  # TODO set this to the install path
USR_VAR_NAME = "MyAppUsrVar"  # TODO set this to a unique user variable name (distinct to the application)


def copy_dist_to_target(source_path: Path, target_path: Path) -> bool:
    if source_path.exists():
        print("Found source/distribution path at %s" % source_path.resolve())
    else:
        print("Unable to find the source/distribution directory, looked at %s" % source_path.resolve())
        return False
    if target_path.exists():
        if len(list(target_path.glob("*"))) > 0:
            if input("Files found in install directory (%s). This will be the case if updating from an older version. "
                     "OK to delete these files? (y/N)" % target_path) == 'y':
                shutil.rmtree(target_path)
            else:
                return False
        else:
            target_path.rmdir()  # remove this dir to avoid error from shutil.copytree
    print("Installing to %s" % target_path)
    shutil.copytree(str(source_path), str(target_path))


def add_dir_to_usr_path_var(path: Path, user_var_name: str) -> str:
    print("Saving value to path variable (%s <-- %s). Old values will be overwritten." % (USR_VAR_NAME, TARGET_DIR))
    subprocess.run(['setx', user_var_name, str(path.resolve())])
    path_var_info = subprocess.run(['echo', '%PATH%', str(path.resolve())], capture_output=True)
    if path_var_info.returncode != 0:
        return path_var_info.stderr.decode('ascii')
    path_dirs = path_var_info.stdout.decode('ascii').split(';')
    for path_dir in path_dirs:
        if Path(path_dir).resolve() == path.resolve():
            return "%s already exists in the PATH variable" % path.resolve()

    # TODO add logic to cleanly append to path
    """
    Adding a variable to the path is going to be more difficult than expected. We'll probably just need to do the following:
    - Check to see how long the path variable is.
    - If it will be greater than 1024 characters after appending the new variable:
        - create a new user variable (i.e. an "expansion" variable)
        - move existing paths from the path variable to the new expansion variable to make room for the new expansion variable in the path variable 
        - append the user variable to the path variable
        - add the new dir to the expansion variable
    """
    # subprocess.run(['setx', USR_VAR_NAME, str(TARGET_DIR.resolve()), '/m'])  # https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/setx

    return None


if __name__=="__main__":
    print("setup.exe")
    print("Be sure to run this installer as an admin")
    if input("Ready to start installing? (y/N)") == 'y':
        try:
            success = copy_dist_to_target(DIST_DIR, TARGET_DIR)
        except Exception as e:
            print("Caught exception:")
            traceback.print_exc()
            success = False
        if success:
            print("Installation successful!")
            if input("Add install directory (%s) to the PATH variable automatically? (y/N)") == 'y':
                error = add_dir_to_usr_path_var(TARGET_DIR, USR_VAR_NAME)
                if error:
                    print("Could not add the install directory to the PATH variable: %s" % error)
                else:
                    print("Successfully added install directory to the PATH variable!")
        else:
            print("Installation failed!")

        input("Press enter to exit")
