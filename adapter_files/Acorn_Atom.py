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


def runGameWithRezmame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "atom"
       "atomeb"
       "atombb"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "atom":
        availableDevices = [
            ['printout', ['.prn']],
            ['cassette', ['.wav', '.tap', '.csw', '.uef']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.40t']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.40t']],
            ['quickload', ['.atm']],
            ['cartridge', ['.bin', '.rom']]
        ]
    elif i_machineName == "atomeb":
        availableDevices = [
            ['printout', ['.prn']],
            ['cassette', ['.wav', '.tap', '.csw', '.uef']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.40t']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.40t']],
            ['quickload', ['.atm']],
            ['romimage1', ['.bin', '.rom']],
            ['romimage2', ['.bin', '.rom']],
            ['romimage3', ['.bin', '.rom']],
            ['romimage4', ['.bin', '.rom']],
            ['romimage5', ['.bin', '.rom']],
            ['romimage6', ['.bin', '.rom']],
            ['romimage7', ['.bin', '.rom']],
            ['romimage8', ['.bin', '.rom']],
            ['romimage9', ['.bin', '.rom']],
            ['romimage10', ['.bin', '.rom']],
            ['romimage11', ['.bin', '.rom']],
            ['romimage12', ['.bin', '.rom']],
            ['romimage13', ['.bin', '.rom']],
            ['romimage14', ['.bin', '.rom']],
            ['romimage15', ['.bin', '.rom']],
            ['romimage16', ['.bin', '.rom']],
            ['romimage17', ['.bin', '.rom']],
            ['romimage18', ['.bin', '.rom']]
        ]
    elif i_machineName == "atombb":
        availableDevices = [
            ['printout', ['.prn']],
            ['cassette', ['.wav', '.tap', '.csw', '.uef']]
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
        "rezmame atom (Atom)",
        "rezmame atomeb (Atom with Eprom Box)",
        "rezmame atombb (Atom with BBC Basic)"
    ])

    if method == "rezmame atom (Atom)":
        runGameWithRezmame(i_gameDescription, "atom", i_gameFilePaths)
    elif method == "rezmame atomeb (Atom with Eprom Box)":
        runGameWithRezmame(i_gameDescription, "atomeb", i_gameFilePaths)
    elif method == "rezmame atombb (Atom with BBC Basic)":
        runGameWithRezmame(i_gameDescription, "atombb", i_gameFilePaths)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = tempfile.gettempdir() + "/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(gamesBaseDirPath + i_gamePath, tempDirPath)
        # Filter non-game files out of zip member list
        gameFiles = [zipMember
                     for zipMember in zipMembers
                     if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(gamesBaseDirPath + i_gamePath, tempDirPath + "/" + os.path.basename(i_gamePath))
        gameFiles = [os.path.basename(i_gamePath)]

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
