import sys
from os import path

# the same folder where this program is stored
if getattr(sys, 'frozen', False):
	mainFolder = path.dirname(sys.executable) # EXE (executable) file
else:
	mainFolder = path.dirname(path.realpath(__file__)) # PY (source) file
sys.path.append(mainFolder)

driveLetter = path.splitdrive(mainFolder)[0]+"\\"

########################
# EDIT BELOW THIS LINE #
########################

# These are only examples; make sure you replace them with your own directories.

"""
A directory can be an absolute path (make sure you put the path in quotes and use two back-slashes to separate folders):
romsetFolder = "D:\\My Files\\Romsets"
... or a joined path:
romsetFolder = path.join("D:\\", "My Files", "Romsets")

driveLetter is the drive where this program is stored (example: "C:\\")
"""

# The folder when your current romsets are stored.
romsetFolder = path.join(driveLetter, "Roms", "Romsets")

# The folder containing roms that aren't part of a set (rom hacks, homebrew, etc.).
# If you don't have an Other folder, leave this as ""
otherFolder = path.join(driveLetter, "Roms", "Other")

# The folder that will be updated with new files from your target device's rom folder.
# You can set this to be the same as romsetFolder (not recommended) or otherFolder if you'd like.
# If you don't want to copy new files from your device to your main drive, leave this as ""
updateFromDeviceFolder = path.join(driveLetter, "Roms", "Copy To Other")

# The folder containing your XMDB files.
xmdbDir = path.join(mainFolder, "No-Intro Database")

# The folder containing profiles for each device (these tell the program which merged/1G1R sets to generate).
profilesFolder = path.join(mainFolder, "Romset Profiles")

# The folder containing generated log files.
# If you don't want to generate log files, leave this as ""
logFolder = path.join(mainFolder, "Logs")
