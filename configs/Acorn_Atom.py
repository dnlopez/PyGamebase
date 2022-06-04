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
config_title = "Acorn Atom"
gamebaseBaseDirPath = driveBasePath + "/games/Acorn Atom/gamebases/Acorn Atom"
config_databaseFilePath = gamebaseBaseDirPath + "/Acorn Atom.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


emulatorCommand = ["rezmame.py", "atom", "-flop1"]#, "$gameFiles"]


def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = tempfile.gettempdir() + "/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(gamesBaseDirPath + i_gamePath, tempDirPath)
        gameFiles = zipMembers
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(gamesBaseDirPath + i_gamePath, tempDirPath + "/" + os.path.basename(i_gamePath))
        gameFiles = [os.path.basename(i_gamePath)]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    #
    command = emulatorCommand[:]
    command.extend(utils.joinPaths(tempDirPath, gameFiles))
    utils.shellStartTask(command)


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
