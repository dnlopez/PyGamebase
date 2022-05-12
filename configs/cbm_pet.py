# Python std
import os.path
import shutil
import pprint

# This program
import utils


config_title = "Commodore PET"
config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/CBM_PET.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Commodore PET/Gamebase_PET/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Commodore PET/Gamebase_PET/Extras/"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "pet"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezvice_xpet.py"]

    executableAndArgs += ["--region", "pal"]

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--"]

    executableAndArgs += i_gameFilePaths

    print(executableAndArgs)
    # Execute
    utils.shellExecList(executableAndArgs)


def runGameMenu(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    runGameOnMachine(i_gameDescription, "pet", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = "/mnt/ve/games/Commodore PET/Gamebase_PET/FILES/"
    tempDirPath = "/tmp/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_zipFilePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)
        # Filter non-game files out of zip member list
        gameFiles = [zipMember
                     for zipMember in zipMembers
                     if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(basePath + i_zipFilePath, tempDirPath + "/" + os.path.basename(i_zipFilePath))
        gameFiles = [os.path.basename(i_zipFilePath)]

    #
    if i_zipMemberToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGameMenu(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

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
