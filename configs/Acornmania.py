# Python std
import os.path
import shutil
import pprint

# This program
import utils


config_title = "Acorn BBC Micro and Electron (Acornmania)"
gamebaseBaseDirPath = "/mnt/ve/games/Acorn BBC Micro/gamebases/Acornmania/GB_Acornmania"
config_databaseFilePath = gamebaseBaseDirPath + "/GB_Acornmania.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "tutor"
       "pyuuta"
       "pyuutajr"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    availableDevices = [
        ["printout", [".prn"]],
        ["cassette", [".wav"]],
        ["cartridge", [".bin"]]
    ]
    for gameFilePath in i_gameFilePaths:
        for availableDeviceNo, availableDevice in enumerate(availableDevices):
            deviceName, allowedFileExtensions = availableDevice

            if utils.pathHasExtension(gameFilePath, allowedFileExtensions):
                executableAndArgs.extend(["-" + deviceName, gameFilePath])
                del(availableDevices[availableDeviceNo])
                break

    if i_gameDescription:
        executableAndArgs.extend(["--game-description", i_gameDescription])

    # Execute
    print(executableAndArgs)
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
    method = utils.popupMenu([
        "rezmame tutor",
        "rezmame pyuuta",
        "rezmame pyuutajr"
    ])

    if method == "rezmame tutor":
        runGameOnMachine(i_gameDescription, "tutor", i_gameFilePaths)
    elif method == "rezmame pyuuta":
        runGameOnMachine(i_gameDescription, "pyuuta", i_gameFilePaths)
    elif method == "rezmame pyuutajr":
        runGameOnMachine(i_gameDescription, "pyuutajr", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = gamebaseBaseDirPath + "/Games/"
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
        zipMembers = utils.extractZip(config_extrasBasePath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGameMenu(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBasePath + "/" + i_path)
