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
config_title = "Acorn BBC Micro and Electron (Acornmania)"
gamebaseBaseDirPath = driveBasePath + "/games/Acorn BBC Micro/gamebases/Acornmania/GB_Acornmania"
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
    utils.shellStartTask(executableAndArgs)

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

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = "/tmp/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(basePath + i_gamePath, tempDirPath)
        # Filter non-game files out of zip member list
        gameFiles = [zipMember
                     for zipMember in zipMembers
                     if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(basePath + i_gamePath, tempDirPath + "/" + os.path.basename(i_gamePath))
        gameFiles = [os.path.basename(i_gamePath)]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if i_gameInfo["Publisher"]:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGameMenu(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + i_extraPath, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["Name"]
        if i_gameInfo["Publisher"]:
            gameDescription += " (" + i_gameInfo["Publisher"] + ")"

        #
        runGameMenu(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
