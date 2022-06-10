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
config_title = "Apple II"
gamebaseBaseDirPath = driveBasePath + "/games/Apple II/gamebases/Apple 2 Gamebase"
config_databaseFilePath = gamebaseBaseDirPath + "/Apple 2.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithRezmame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "apple2e"
       "apple2gs"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "apple2e":
        availableDevices = [
            ["floppydisk1", [".mfi", ".dfi", ".dsk", ".do", ".po", ".rti", ".edd", ".woz", ".nib"]],
            ["floppydisk2", [".mfi", ".dfi", ".dsk", ".do", ".po", ".rti", ".edd", ".woz", ".nib"]],
            ["cassette", [".wav"]]
        ]
    elif i_machineName == "apple2gs":
        availableDevices = [
            ["floppydisk1", [".mfi", ".dfi", ".dsk", ".do", ".po", ".rti", ".edd", ".woz", ".nib"]],
            ["floppydisk2", [".mfi", ".dfi", ".dsk", ".do", ".po", ".rti", ".edd", ".woz", ".nib"]],
            ["floppydisk3", [".mfi", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk", ".ima", ".img", ".ufi", ".360", ".ipf", ".dc42", ".woz", ".2mg"]],
            ["floppydisk4", [".mfi", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk", ".ima", ".img", ".ufi", ".360", ".ipf", ".dc42", ".woz", ".2mg"]]
        ]
    executableAndArgs.extend(utils.allocateGameFilesToMameMediaSlots(i_gameFilePaths, availableDevices))

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
        "rezmame apple2e (Apple //e)",
        "rezmame apple2gs (Apple IIgs (ROM03))",
    ])

    if method == "rezmame apple2e (Apple //e)":
        runGameWithRezmame(i_gameDescription, "apple2e", i_gameFilePaths)
    elif method == "rezmame apple2gs (Apple IIgs (ROM03))":
        runGameWithRezmame(i_gameDescription, "apple2gs", i_gameFilePaths)


def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = tempfile.gettempdir() + "/gamebase"

    gameFiles = []
    for gamePath in utils.findFileSequence(gamesBaseDirPath, i_gamePath):
        # If file is a zip
        if utils.pathHasExtension(gamePath, ".ZIP"):
            # Extract it
            zipMembers = utils.extractZip(gamesBaseDirPath + gamePath, tempDirPath)
            # Filter non-game files out of zip member list
            gameFiles += [zipMember
                         for zipMember in zipMembers
                         if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
        # Else if file is not a zip
        else:
            # Copy it
            shutil.copyfile(gamesBaseDirPath + gamePath, tempDirPath + "/" + os.path.basename(gamePath))
            gameFiles += [os.path.basename(gamePath)]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if "Publisher" in i_gameInfo:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGameMenu(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

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
