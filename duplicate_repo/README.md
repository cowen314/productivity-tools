# duplicate-repo

This tool allows quick and easy duplication of a template repository into a new location.

The history of the template repository is preserved in the duplicate, so rebasing in template changes made after the original duplication is possible. 

### Building from scratch

1. build the tool with pyinstaller `pyinstaller build_duplicate_repo.spec`
1. build the setup with pyinstaller `pyinstaller build_setup_script.spec`
    - this will build a very simple installer, `setup_script.exe`

### Installation

Double click `setup_script.exe` and follow the instructions in the console window that appears

### Using the tool
 
 Once installed, the tool can be accessed from the context menu; right-click in a folder, then press the `Duplicate Repo` menu item. Follow the steps in the console window that appears to duplicate an existing repository to a new location.
 
 ### Configuration file
 
 This tool supports persistent configurations. See `cloneConfig.json` in the install directory.