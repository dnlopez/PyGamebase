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
config_title = "Atari 2600"
gamebaseBaseDirPath = driveBasePath + "/games/Atari 2600/gamebases/Atari 2600"
config_databaseFilePath = gamebaseBaseDirPath + "/Atari 2600.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameOnMachine(i_machineName, i_gameFilePaths):
    """
    Params:
     i_machineName:
      (string)
      One of
       "mame a2600"
       "stella"
     i_gameFilePaths:
      (array of string)
    """
    if i_machineName == "mame a2600":
        executableAndArgs = ["/mnt/ve/prog/c/mame_git/mame64_0240", "a2600", "-cartridge"]
    elif i_machineName == "stella":
        executableAndArgs = ["stella"]

    executableAndArgs += i_gameFilePaths

    # Execute
    utils.shellStartTask(executableAndArgs)

def runGameMenu(i_gameFilePaths):
    """
    Params:
     i_gameFilePaths:
      (list of str)
    """
    method = utils.popupMenu([
        "mame a2600",
        "stella"
    ])

    if method == "mame a2600":
        runGameOnMachine("mame a2600", i_gameFilePaths)
    elif method == "stella":
        runGameOnMachine("stella", i_gameFilePaths)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    romFilePath = i_gamePath

    #
    gamesBaseDirPath = gamebaseBaseDirPath + "/roms/"
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
    runGameMenu(utils.joinPaths(tempDirPath, gameFiles))

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
        if utils.pathHasExtension(i_extraPath, [".BIN", ".A26"]):
            runGameMenu([config_extrasBaseDirPath + "/" + i_extraPath])
        else:
            utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
