from pathlib import Path
import os
import shutil
import subprocess
import traceback


# Define to install process
DIST_PATH = Path("./link_reqs")  # TODO put a path to the distribution folder here
TARGET_DIR = Path(os.environ['PROGRAMFILES']) / "DeveloperName" / "AppName"  # TODO set this to the install path
USR_VAR_NAME = "MyAppUsrVar"  # TODO update this, if the item should be added to a path variable


def install() -> bool:
    if DIST_PATH.exists():
        print("Found tool path at %s" % DIST_PATH.resolve())
    else:
        print("Unable to find the specified install directory, looked at %s" % DIST_PATH.resolve())
        return False
    if TARGET_DIR.exists():
        if len(list(TARGET_DIR.glob("*"))) > 0:
            if input("Files found in install directory (%s). This will be the case if updating from an older version. "
                     "OK to delete these files? (y/N)" % TARGET_DIR) == 'y':
                shutil.rmtree(TARGET_DIR)
            else:
                return False
        else:
            TARGET_DIR.rmdir()  # remove this dir to avoid error from shutil.copytree
    print("Installing to %s" % TARGET_DIR)
    shutil.copytree(DIST_PATH, TARGET_DIR)
    print("Saving value to path variable (%s <-- %s)" % (USR_VAR_NAME, TARGET_DIR))
    # TODO add logic to cleanly append to path
    """
    Adding a variable to the path is going to be more difficult than expected. We'll probably just need to do the following:
    - Check to see how long the path variable is.
    - If it will be greater than 1024 characters after appending the new dir:
        - create a new user variable (i.e. an "expansion" variable)
        - append the user variable to the path variable, moving existing paths from the path variable to the user variable to make room for the new expansion variable in the path variable 
        - then add the new dir to the expansion variable
    """
    # subprocess.run(['setx', USR_VAR_NAME, str(TARGET_DIR.resolve()), '/m'])  # https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/setx
    subprocess.run(['setx', USR_VAR_NAME, str(TARGET_DIR.resolve())])

    return True


if __name__=="__main__":
    print("setup.exe")
    print("Be sure to run this installer as an admin")
    if input("Ready to start installing? (y/N)") == 'y':
        try:
            success = install()
        except Exception as e:
            print("Caught exception:")
            traceback.print_exc()
            success = False
        if success:
            print("Installation successful!")
        else:
            print("Installation failed!")
        input("Press enter to exit")
