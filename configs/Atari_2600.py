# Python std
import os.path
import shutil
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
config_databaseFilePath = gamebaseBaseDirPath + "/Atari_2600.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (string)
      One of
       "rezmame a2600"
       "rezstella (NTSC)"
       "rezstella (PAL)"
     i_gameFilePaths:
      (array of string)
    """
    if i_machineName == "rezmame a2600":
        executableAndArgs = ["rezmame.py", "a2600", "-cartridge"]
    elif i_machineName == "rezstella (NTSC)":
        executableAndArgs = ["rezstella.py", "--region", "ntsc", "--media"]
    elif i_machineName == "rezstella (PAL)":
        executableAndArgs = ["rezstella.py", "--region", "pal", "--media"]

    executableAndArgs += i_gameFilePaths

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    # Execute
    utils.shellExecList(executableAndArgs)

def runGame2(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    method = utils.popupMenu([
        "rezmame a2600",
        "rezstella (NTSC)",
        "rezstella (PAL)"
    ])

    if method == "rezmame a2600":
        runGameOnMachine(i_gameDescription, "rezmame a2600", i_gameFilePaths)
    elif method == "rezstella (NTSC)":
        runGameOnMachine(i_gameDescription, "rezstella (NTSC)", i_gameFilePaths)
    elif method == "rezstella (PAL)":
        runGameOnMachine(i_gameDescription, "rezstella (PAL)", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    romFilePath = i_zipFilePath

    #
    basePath = gamebaseBaseDirPath + "/roms/"
    tempDirPath = "/tmp/gamebase"

    # Copy ROM file
    if not os.path.exists(tempDirPath):
        os.mkdir(tempDirPath)
    shutil.copyfile(basePath + romFilePath, tempDirPath + "/" + os.path.basename(romFilePath))

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(tempDirPath, [os.path.basename(romFilePath)]))

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If zip file
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_path)
