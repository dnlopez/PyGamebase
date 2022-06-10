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
config_title = "Coleco ColecoVision"
gamebaseBaseDirPath = driveBasePath + "/games/Coleco Colecovision/gamebases/Gamebase"
config_databaseFilePath = gamebaseBaseDirPath + "/ColecoVision.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screens"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithMame(i_gameFilePaths):
    """
    Params:
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["/mnt/ve/prog/c/mame_git/mame64_0240", "coleco"]

    # Assign game files to available MAME media slots
    availableDevices = [
        ["cartridge", [".rom", ".col", ".bin"]]
    ]
    executableAndArgs.extend(utils.allocateGameFilesToMameMediaSlots(i_gameFilePaths, availableDevices))

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/Roms/"
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

    #
    runGameWithMame(utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        #
        runGameMenu(utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
