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


def runGameWithMame(i_machineName, i_gameFilePaths):
    """
    Params:
     i_machineName:
      (str)
      One of
       "apple2e"
       "apple2gs"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["/mnt/ve/prog/c/mame_git/mame64_0240", i_machineName]

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

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameMenu(i_gameFilePaths):
    """
    Params:
     i_gameFilePaths:
      (list of str)
    """
    method = utils.popupMenu([
        "mame apple2e (Apple //e)",
        "mame apple2gs (Apple IIgs (ROM03))",
    ])

    if method == "mame apple2e (Apple //e)":
        runGameWithMame("apple2e", i_gameFilePaths)
    elif method == "mame apple2gs (Apple IIgs (ROM03))":
        runGameWithMame("apple2gs", i_gameFilePaths)


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

    #
    runGameMenu(utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_fileToRun, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        #
        runGameMenu(utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
