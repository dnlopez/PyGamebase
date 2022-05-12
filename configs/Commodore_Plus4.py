# Python std
import os.path
import pprint

# This program
import utils


config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/Commodore Plus4.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4/Extras/"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (string)
      One of
       "plus4"
     i_gameFilePaths:
      (array of string)
    """
    executableAndArgs = ["rezvice_xplus4.py"]

    executableAndArgs += ["--region", "pal"]

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--"]

    executableAndArgs += i_gameFilePaths

    print(executableAndArgs)
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
    runGameOnMachine(i_gameDescription, "plus4", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4/Games/"

    if utils.pathHasExtension(i_zipFilePath, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)

        # Filter non-game files out of zip member list
        gameFilePaths = [zipMember
                         for zipMember in zipMembers
                         if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR"))]

        gameFileBasePath = tempDirPath
    else:
        gameFilePaths = [i_zipFilePath]
        gameFileBasePath = basePath

    #
    if i_zipMemberToRun == None:
        gameFilePaths = utils.moveElementToFront(gameFilePaths, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(gameFileBasePath, gameFilePaths))

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    extrasBasePath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4/Extras/"

    # If zip file
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(extrasBasePath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(extrasBasePath + "/" + i_path)
