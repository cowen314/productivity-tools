from pathlib import Path
import os
import shutil
import subprocess
import traceback
import winreg


# Define to install process
DIST_DIR = Path("./duplicate_repo")
TARGET_DIR = Path(os.environ['APPDATA']) / "productivity-tools" / "duplicate-repo"
EXE_NAME = "duplicate_repo.exe"
USR_VAR_NAME = "DuplicateRepo"


def copy_dist_to_target(source_path: Path, target_path: Path) -> bool:
    if source_path.exists():
        print("Found source/distribution path at %s" % source_path.resolve())
    else:
        print("Unable to find the source/distribution directory, looked at %s" % source_path.resolve())
        return False
    if target_path.exists():
        shutil.rmtree(target_path)
    print("Installing to %s" % target_path)
    shutil.copytree(str(source_path), str(target_path))
    return True


def add_dir_to_usr_var(path: Path, var_name: str):
    print("Saving value to system variable (%s <-- %s)" % (var_name, path))
    subprocess.run(['setx', var_name, str(path.resolve()), '/m'])  # https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/setx
    print("Append this variable to your path variable to call this tool from a command prompt at any working directory")


def add_context_shortcut(shortcut_name: str, command: str):
    """
    @param shortcut_name: the name of the shortcut to show up in the context menu
    @param command: the command to execute (e.g. `C:\Program Files\DoThing.exe --verbose`)
    """
    # Use the python registry editor module to add this thing to the context menu
    # Python Module: https://docs.python.org/3/library/winreg.html
    # https://stackoverflow.com/questions/20449316/how-add-context-menu-item-to-windows-explorer-for-folders
    print("Connecting to the registry...")
    full_path = r"Software\Classes\Directory\Background\shell\%s\command" % shortcut_name
    print(r"Setting the value of registry key HKEY_CURRENT_USER\%s to '%s'" % (full_path, command))
    winreg.SetValue(winreg.HKEY_CURRENT_USER, full_path, winreg.REG_SZ, command)
    print("Set key sucessfully!")


if __name__=="__main__":
    print("setup.exe")
    print("Be sure to run this installer as an admin")
    if input("Ready to start installing? (y/N)") == 'y':
        try:
            success = copy_dist_to_target(DIST_DIR, TARGET_DIR)
            if not success:
                raise RuntimeError("Failed to copy distribution (%s) to target directory (%s)" % (DIST_DIR, TARGET_DIR))
            if success:
                add_context_shortcut("Duplicate Repo", "%s --wizard" % str(Path.resolve(TARGET_DIR / EXE_NAME)))
            # other setup steps can go here
        except Exception as e:
            print("Caught exception:")
            traceback.print_exc()
            success = False
        if success:
            print("Installation successful!")
        else:
            print("Installation failed!")

        input("Press enter to exit")
