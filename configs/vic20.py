# Python std
import os.path
import pprint

# This program
import utils


config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/Vic20_v03.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Commodore VIC-20/Gamebase20_v03/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4/Extras/"


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
    runGameOnMachine(i_gameDescription, "vic20", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = "/mnt/ve/games/Commodore VIC-20/Gamebase20_v03/Games/"

    if utils.pathHasExtension(i_zipFilePath, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)

        # Filter non-game files out of zip member list
        gameFilePaths = [zipMember
                         for zipMember in zipMembers
                         if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR"))]

        gameFileBaseDirPath = tempDirPath
    else:
        gameFilePaths = [i_zipFilePath]
        gameFileBaseDirPath = basePath

    #
    if i_zipMemberToRun == None:
        gameFilePaths = utils.moveElementToFront(gameFilePaths, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(gameFileBaseDirPath, gameFilePaths))

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    extrasBaseDirPath = "/mnt/ve/games/Commodore VIC-20/Gamebase20_v03/Extras/"

    # If zip file
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(extrasBaseDirPath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(extrasBaseDirPath + "/" + i_path)
