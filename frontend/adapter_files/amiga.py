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
config_title = "Amiga 2.3"
gamebaseBaseDirPath = driveBasePath + "/games/Commodore Amiga/gamebases/Gamebase Amiga 2.3"
config_databaseFilePath = gamebaseBaseDirPath + "/Amiga 2.3.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithMame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
     i_gameFilePaths:
      (list of str)
    """
    mameExecutable = "/mnt/ve/prog/c/mame_git/mame64_0240"
    print(i_gameFilePaths)

    executableAndArgs = [mameExecutable, i_machineName]

    # Get list of MAME media slots for the given machine
    # and assign game files to them
    availableDevices = utils.getMameMediaSlots(mameExecutable, i_machineName)
    executableAndArgs.extend(utils.allocateGameFilesToMameMediaSlots(i_gameFilePaths, availableDevices))

    if i_gameDescription:
        executableAndArgs.extend(["--game-description", i_gameDescription])

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameWithRezmame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "a500"
       "a500n"
       "a600"
       "a600n"
       "a1200"
       "a1200n"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName in ["a500", "a500n"]:
        availableDevices = [
            ["floppydisk", [".mfi", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk", ".adf", ".ipf"]],
            ["printout", [".prn"]],
        ]
    elif i_machineName in ["a600", "a600n", "a1200", "a1200n"]:
        availableDevices = [
            ["floppydisk", [".mfi", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk", ".adf", ".ipf"]],
            ["printout", [".prn"]],
            ["harddisk", [".chd", ".hd", " .hdv", ".2mg", ".hdi"]],
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
        "rezfsuae A500",
        "rezfsuae A600",
        "mame a500 (Amiga 500 (PAL))",
        "rezmame a500 (Amiga 500 (PAL))",
        "rezmame a500n (Amiga 500 (NTSC))",
        "rezmame a600 (Amiga 600 (PAL))",
        "rezmame a600n (Amiga 600 (NTSC))",
        "rezmame a1200 (Amiga 1200 (PAL))",
        "rezmame a1200n (Amiga 1200 (NTSC))",
    ])

    if method == "rezfsuae A500":
        executableAndArgs = ["rezfsuae.py"]

        executableAndArgs += ["--model", "A500"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription:
            executableAndArgs.extend(["--game-description", i_gameDescription])

        utils.shellStartTask(executableAndArgs)

    elif method == "rezfsuae A600":
        executableAndArgs = ["rezfsuae.py"]

        executableAndArgs += ["--model", "A600"]

        executableAndArgs += [i_gameFilePaths]

        if i_gameDescription:
            executableAndArgs.extend(["--game-description", i_gameDescription])

        print(executableAndArgs)
        utils.shellStartTask(executableAndArgs)

    elif method == "mame a500 (Amiga 500 (PAL))":
        runGameWithMame(i_gameDescription, "a500", i_gameFilePaths)
    elif method == "rezmame a500 (Amiga 500 (PAL))":
        runGameWithRezmame(i_gameDescription, "a500", i_gameFilePaths)
    elif method == "rezmame a500n (Amiga 500 (NTSC))":
        runGameWithRezmame(i_gameDescription, "a500n", i_gameFilePaths)
    elif method == "rezmame a600 (Amiga 600 (PAL))":
        runGameWithRezmame(i_gameDescription, "a600", i_gameFilePaths)
    elif method == "rezmame a600n (Amiga 600 (NTSC))":
        runGameWithRezmame(i_gameDescription, "a600n", i_gameFilePaths)
    elif method == "rezmame a1200 (Amiga 1200 (PAL))":
        runGameWithRezmame(i_gameDescription, "a1200", i_gameFilePaths)
    elif method == "rezmame a1200n (Amiga 1200 (NTSC))":
        runGameWithRezmame(i_gameDescription, "a1200n", i_gameFilePaths)

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
