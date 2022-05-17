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
config_title = "Atari ST"
gamebaseBaseDirPath = driveBasePath + "/games/Atari ST/gamebases/Gamebase ST v4/Atari ST"
config_databaseFilePath = gamebaseBaseDirPath + "/Atari ST.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGame2(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of string)
    """
    executableAndArgs = ["rezhatari.py"]

    if (i_gameDescription != None):
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--", i_gameFilePaths[0]]

    # Execute
    utils.shellStartTask(executableAndArgs)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # Extract zip
    basePath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = "/tmp/gamebase"
    zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)

    # Filter non-game files out of zip member list
    gameFiles = [zipMember
                 for zipMember in zipMembers
                 if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".SCR"))]

    #
    if i_zipMemberToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If zip file
    if utils.pathHasExtension(i_path, ".ZIP"):
        # [Don't see any extras that are zipped games in this DB]

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
