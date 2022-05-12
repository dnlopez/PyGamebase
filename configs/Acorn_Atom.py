# Python std
import os.path
import shutil
import pprint

# This program
import utils


config_title = "Acorn Atom"
gamebaseBaseDirPath = "/mnt/ve/games/Acorn Atom/gamebases/Acorn Atom"
config_databaseFilePath = gamebaseBaseDirPath + "/Acorn Atom.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


emulatorCommand = ["rezmame.py", "atom", "-flop1"]#, "$gameFiles"]


def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = "/tmp/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_zipFilePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)
        gameFiles = zipMembers
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(basePath + i_zipFilePath, tempDirPath + "/" + os.path.basename(i_zipFilePath))
        gameFiles = [os.path.basename(i_zipFilePath)]

    #
    if i_zipMemberToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_zipMemberToRun)

    #
    command = emulatorCommand[:]
    command.extend(utils.joinPaths(tempDirPath, gameFiles))
    utils.shellExecList(command)


def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract it
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGameMenu(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_path)
