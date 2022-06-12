# Python std
import os.path
import shutil
import tempfile
import pprint

# This program
import utils


# Dan's local system
import platform
if platform.system() == "Windows":
    driveBasePath = "E:"
else:
    driveBasePath = "/mnt/ve"


# Frontend configuration
config_title = "Dragon"
gamebaseBaseDirPath = driveBasePath + "/games/Dragon/gamebases/gamebase/extracted"
config_databaseFilePath = gamebaseBaseDirPath + "/Dragon.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/screen"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/extras"


def runGameWithRezmame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "dragon32"
       "coco"
       "coco2"
       "coco3"
       "coco3h"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "dragon32":
        availableDevices = [
            ['cassette', ['.wav', '.cas']],
            ['printout', ['.prn']],
            ['cartridge', ['.ccc', '.rom']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']]
        ]
    elif i_machineName == "coco":
        availableDevices = [
            ['cassette', ['.wav', '.cas']],
            ['printout', ['.prn']],
            ['cartridge', ['.ccc', '.rom']]
        ]
    elif i_machineName == "coco2":
        availableDevices = [
            ['cassette', ['.wav', '.cas']],
            ['printout', ['.prn']],
            ['cartridge', ['.ccc', '.rom']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']],
            ['harddisk1', ['.vhd']],
            ['harddisk2', ['.vhd']]
        ]
    elif i_machineName == "coco3":
        availableDevices = [
            ['cassette', ['.wav', '.cas']],
            ['printout', ['.prn']],
            ['harddisk1', ['.vhd']],
            ['harddisk2', ['.vhd']],
            ['cartridge', ['.ccc', '.rom']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']]
        ]
    elif i_machineName == "coco3h":
        availableDevices = [
            ['cassette', ['.wav', '.cas']],
            ['printout', ['.prn']],
            ['harddisk1', ['.vhd']],
            ['harddisk2', ['.vhd']],
            ['cartridge', ['.ccc', '.rom']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.dmk', '.jvc', '.vdk', '.sdf', '.os9']]
        ]
    executableAndArgs.extend(utils.allocateGameFilesToMameMediaSlots(i_gameFilePaths, availableDevices))

    if i_gameDescription:
        executableAndArgs.extend(["--game-description", i_gameDescription])

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameMenu(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    method = utils.popupMenu([
        "rezmame dragon32 (Dragon 32)",
        "rezmame coco (Color Computer)",
        "rezmame coco2 (Color Computer 2)",
        "rezmame coco3 (Color Computer 3 (NTSC))",
        "rezmame coco3h (Color Computer 3 (NTSC; HD6309))"
    ])

    if method == "rezmame dragon32 (Dragon 32)":
        runGameWithRezmame(i_gameDescription, "dragon32", i_gameFilePaths)
    elif method == "rezmame coco (Color Computer)":
        runGameWithRezmame(i_gameDescription, "coco", i_gameFilePaths)
    elif method == "rezmame coco2 (Color Computer 2)":
        runGameWithRezmame(i_gameDescription, "coco2", i_gameFilePaths)
    elif method == "rezmame coco3 (Color Computer 3 (NTSC))":
        runGameWithRezmame(i_gameDescription, "coco3", i_gameFilePaths)
    elif method == "rezmame coco3h (Color Computer 3 (NTSC; HD6309))":
        runGameWithRezmame(i_gameDescription, "coco3h", i_gameFilePaths)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/games/"
    tempDirPath = tempfile.gettempdir() + "/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(gamesBaseDirPath + i_gamePath, tempDirPath)
        # Filter non-game files out of zip member list
        gameFiles = [zipMember
                     for zipMember in zipMembers
                     if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(gamesBaseDirPath + i_gamePath, tempDirPath + "/" + os.path.basename(i_gamePath))
        gameFiles = [os.path.basename(i_gamePath)]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if "Publisher" in i_gameInfo:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGameMenu(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["Name"]
        if "Publisher" in i_gameInfo:
            gameDescription += " (" + i_gameInfo["Publisher"] + ")"

        #
        runGameMenu(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
