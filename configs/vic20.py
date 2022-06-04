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
config_title = "Commodore VIC-20 v03"
gamebaseBaseDirPath = driveBasePath + "/games/Commodore VIC-20/gamebases/Gamebase20_v03/Vic20_v03"
config_databaseFilePath = gamebaseBaseDirPath + "/Vic20_v03.sqlite"
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
      eg.
       "vic20"
     i_gameFilePaths:
      (array of string)
    """
    executableAndArgs = ["rezvice_xvic.py"]

    executableAndArgs += ["--region", "pal"]

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--"]

    if utils.pathHasExtension(i_gameFilePaths[0], ".CRT"):
        executableAndArgs.push("-cartgeneric")

    executableAndArgs += i_gameFilePaths

    print(executableAndArgs)
    # Execute
    utils.shellStartTask(executableAndArgs)


def runGame2(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    runGameOnMachine(i_gameDescription, "vic20", i_gameFilePaths)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/Games/"

    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract zip
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(gamesBaseDirPath + i_gamePath, tempDirPath)

        # Filter non-game files out of zip member list
        gameFilePaths = [zipMember
                         for zipMember in zipMembers
                         if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR"))]

        gameFileBaseDirPath = tempDirPath
    else:
        gameFilePaths = [i_gamePath]
        gameFileBaseDirPath = gamesBaseDirPath

    #
    if i_fileToRun == None:
        gameFilePaths = utils.moveElementToFront(gameFilePaths, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if "Publisher" in i_gameInfo:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(gameFileBaseDirPath, gameFilePaths))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If zip file
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract zip
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["Name"]
        if "Publisher" in i_gameInfo:
            gameDescription += " (" + i_gameInfo["Publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
