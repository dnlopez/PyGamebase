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
config_title = "Acorn BBC Micro and Electron (Acornmania)"
gamebaseBaseDirPath = driveBasePath + "/games/Acorn BBC Micro/gamebases/Acornmania/GB_Acornmania"
config_databaseFilePath = gamebaseBaseDirPath + "/GB_Acornmania.sqlite"
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
       "bbcb"
       "bbcm"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "bbcb":
        availableDevices = [
            ['cassette', ['.wav', '.csw', '.uef']],
            ['romimage1', ['.rom', '.bin']],
            ['romimage2', ['.rom', '.bin']],
            ['romimage3', ['.rom', '.bin']],
            ['romimage4', ['.rom', '.bin']],
            ['printout', ['.prn']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.ima', '.img', '.ufi', '.360', '.ipf', '.ssd', '.bbc', '.dsd', '.adf', '.ads', '.adm', '.adl', '.fsd']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.ima', '.img', '.ufi', '.360', '.ipf', '.ssd', '.bbc', '.dsd', '.adf', '.ads', '.adm', '.adl', '.fsd']]
        ]
    elif i_machineName == "bbcm":
        availableDevices = [
            ['printout', ['.prn']],
            ['cassette', ['.wav', '.csw', '.uef']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.ima', '.img', '.ufi', '.360', '.ipf', '.ssd', '.bbc', '.dsd', '.adf', '.ads', '.adm', '.adl', '.dds', '.fsd']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk', '.ima', '.img', '.ufi', '.360', '.ipf', '.ssd', '.bbc', '.dsd', '.adf', '.ads', '.adm', '.adl', '.dds', '.fsd']],
            ['cartridge1', ['.rom', '.bin']],
            ['cartridge2', ['.rom', '.bin']],
            ['romimage1', ['.rom', '.bin']]
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
        "rezmame bbcb (BBC Micro Model B)",
        "rezmame bbcm (BBC Master 128)",
        "BeebEm",
    ])

    if method == "rezmame bbcb (BBC Micro Model B)":
        runGameWithRezmame(i_gameDescription, "bbcb", i_gameFilePaths)
    elif method == "rezmame bbcm (BBC Master 128)":
        runGameWithRezmame(i_gameDescription, "bbcm", i_gameFilePaths)
    elif method == "BeebEm":
        # The following command line options can be passed to BeebEm:
        #   -Model <0=Model B, 1=B+IntegraB, 2=B Plus, 3=Master>
        #   -Tube <0=off, 1=on>
        #   -EcoStn <Econet station number>
        #   -EcoFF <Econet flag fill timeout, see the econet section>
        #   <disk image file name>
        #   <state file name>
        executableAndArgs = ["beebem"]

        executableAndArgs.append(i_gameFilePaths[0])

        #if (i_gameDescription)
        #    executableAndArgs.push("--game-description", i_gameDescription)

        utils.shellStartTask(executableAndArgs)

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
