# Rom Organizer Deluxe
 
This is a program that uses [No-Intro](https://datomatic.no-intro.org/) and/or [Redump](http://redump.org/) database files to create an organized copy of a local romset. The intent is to keep an unorganized rom collection on one drive, while using this program to create curated sets for each of your individual devices with minimal work required for upkeep. You can create a profile for each device indicating what should/shouldn't be copied so you don't have to remember your preferences every time. Running time is also low in upkeep since files that already exist on the target drive aren't re-copied.

<img src="https://github.com/GateGuy/RomOrganizerDeluxe/blob/master/screenshot.png?raw=true" width="434" height="499" />

It can create merged sets (where a game folder is created containing all versions of a game that you own), 1G1R sets (1 Game 1 Rom; each folder contains only the "best" version of a game; ideally, the latest non-demo/proto USA revision), or 1G1R Priority sets (same as 1G1R, but any games that do not have a version from your region are ignored). It also attempts to rename roms with slightly inaccurate names to match their database counterparts (such as changing "Rev 1" to "Rev A", fixing capitalization, etc.), or can ask you to rename a misnamed rom within the program itself if it can't find a match on its own. Finally, games are also sorted by primary region (e.g. if a USA version of a game exists, the game folder containing all versions will be placed in the USA folder), with the option of putting games from your primary region(s) in the root folder instead of a subfolder. See the bottom of this readme for an example.

After creating a copy of your romset following the preferences you've defined, it can also copy all files from a secondary folder onto your device, which is useful if you have a separate folder for things like rom hacks or homebrew. Additionally, it can also copy any files that only exist in your target device's rom folder (and not in your main drive's romsets or secondary folder) back onto your main drive. This way, you won't have to remember what files you've added to each device individually; they'll all stay up to date.

Finally, while the program is doing all this, it will create logs that track what files are missing from your local romset as indicated by your database files, along with logs of what files were copied to/from your target drive.

I made this program for my own personal use, so some parts of it may not be completely user-friendly. But feel free to use it if you want; it won't break anything (your ROMs are only copied, not moved or deleted, and roms are only renamed according to No-Intro/Redump naming conventions). Just make sure you change the input/output paths in the settings file.

### Device Profile
You can create a device profile that saves settings for that device's curated rom collection. The settings are:
- Which romsets should be copied in Full, 1G1R, 1G1R Primary, or None
- Which folders from your secondary folder should be copied
- Which folders should not be copied (for example, you can ignore any file that was originally in a [Homebrew] folder, or skip any roms in the [Japan] region)
- Which regions are set as primary (any roms from these regions will be saved in the root directory instead of a separate region folder)

### Example Output
For example, your local romset containing:
```
D:/Roms/Sega - Sega Genesis/My Game 1 (USA).zip
D:/Roms/Sega - Sega Genesis/My Game 1 (USA) (Rev 1).zip
D:/Roms/Sega - Sega Genesis/My Game 1 (Europe).zip
D:/Roms/Sega - Sega Genesis/My Game 1 (Japan).zip
D:/Roms/Sega - Sega Genesis/My Game 2 (Europe).zip
D:/Roms/Sega - Sega Genesis/My Game 2 (Japan).zip
```
... provided you have a database file with the same name as the system (plus (optionally) anything in parentheses after the system name):
```
D:/Tools/No-Intro Database/Sega - Sega Genesis (20200102-012345).xmdb
```
... will be copied and sorted as:
```
F:/Roms/Sega - Sega Genesis/USA/My Game 1/My Game 1 (USA).zip
F:/Roms/Sega - Sega Genesis/USA/My Game 1/My Game 1 (USA) (Rev 1).zip
F:/Roms/Sega - Sega Genesis/USA/My Game 1/My Game 1 (Europe).zip
F:/Roms/Sega - Sega Genesis/USA/My Game 1/My Game 1 (Japan).zip
F:/Roms/Sega - Sega Genesis/Europe/My Game 2/My Game 2 (Europe).zip
F:/Roms/Sega - Sega Genesis/Europe/My Game 2/My Game 2 (Japan).zip
```
All versions of My Game 1 are stored in the USA folder since a USA version exists, while all versions of My Game 2 are stored in the Europe folder because a USA version does not exist, but a European version (another English region) does. USA roms are always prioritized, followed by Europe, then other English-speaking regions (and any region where the current rom happens to be in English), then Japan, then everything else.

### Disclaimer
This is not a rom downloader, nor does it include any information on where to obtain roms. You are responsible for legally obtaining your own roms for use with this program.
