# Quick Installer

## Description

This is a boilerplate script, written in Python, that performs installation of a simple desktop application.

In the past, I've used PyInstaller to generate an executable from this script (called something like `setup.exe`), then distrubuted that executable along with the application to install. Users then run `setup.exe` to install the application.

## How to use

1. Copy this script to your project
2. Read through the TODOs; make updates as needed
3. Build it into an executable with PyInstaller (e.g. `pyinstaller --onefile --name setup quick_install.py`)
4. Distribute it with your application

## Features

As of 2021 10 11:

- Copy application to install/target directory
- Add target directory to PATH (currently Windows only)
- Add context / right-click shotcut for application (Windows only)
