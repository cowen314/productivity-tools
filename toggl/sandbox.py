# import pyautogui
#
# pyautogui.typewrite('akasjhaks')

from pathlib import Path

unique = []
with open(Path("C:/Users/christiano/Downloads/Untitled-AB.txt"), 'r') as f:
    for line in f:
        line = line.strip()
        if line not in unique:
            unique.append(line)
            print(line)
