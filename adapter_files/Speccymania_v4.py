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
config_title = "Sinclair ZX Spectrum (Speccymania v4)"
gamebaseBaseDirPath = driveBasePath + "/games/Sinclair ZX Spectrum/gamebases/Speccymania v4/zx_up_dax_PL/ZX Spectrum"
config_databaseFilePath = gamebaseBaseDirPath + "/ZX Spectrum.sqlite"
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
       "spectrum"
       "spec128"
       "specpls3"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "spectrum" or i_machineName == "spec128":
        availableDevices = [
            ["snapshot", [".ach", ".frz", ".plusd.prg", ".sem", ".sit", ".sna", ".snp", ".snx", ".sp", ".z80", ".zx"]],
            ["quickload", [".raw", ".scr"]],
            ["cassette", [".wav", ".tzx", ".tap", ".blk"]]
        ]
    elif i_machineName == "specpls3":
        availableDevices = [
            ["snapshot", [".ach", ".frz", ".plusd.prg", ".sem", ".sit", ".sna", ".snp", ".snx", ".sp", ".z80", ".zx"]],
            ["quickload", [".raw", ".scr"]],
            ["cassette", [".wav", ".tzx", ".tap", ".blk"]],
            ["floppydisk1", [".mfi", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk"]],
            ["floppydisk2", [".mfi0", ".dfi", ".hfe", ".mfm", ".td0", ".imd", ".d77", ".d88", ".1dd", ".cqm", ".cqi", ".dsk"]]
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
        "rezmame spectrum",
        "rezmame spec128",
        "rezmame specpls3",
        "fuse (Spectrum 48K)",
        "fuse (Spectrum 128K)",
        "rezep128emu_zx (Spectrum 48K)",
        "rezep128emu_zx (Spectrum 128K)"
    ])

    if method == "rezmame spectrum":
        runGameWithRezmame(i_gameDescription, "spectrum", i_gameFilePaths)

    elif method == "rezmame spec128":
        runGameWithRezmame(i_gameDescription, "spec128", i_gameFilePaths)

    elif method == "rezmame specpls3":
        runGameWithRezmame(i_gameDescription, "specpls3", i_gameFilePaths)

    elif method == "fuse (Spectrum 48K)":
        executableAndArgs = ["fuse", "--machine", "48"] + i_gameFilePaths
        utils.shellStartTask(executableAndArgs)

    elif method == "fuse (Spectrum 128K)":
        executableAndArgs = ["fuse", "--machine", "128"] + i_gameFilePaths
        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 48K)":
        executableAndArgs = ["rezep128emu_zx.py"]

        # assuming a single file
        executableAndArgs += ["--media", i_gameFilePaths[0]]

        executableAndArgs += ["--model", "48"]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 128K)":
        executableAndArgs = ["rezep128emu_zx.py"]

        # assuming a single file
        executableAndArgs += ["--media", i_gameFilePaths[0]]

        executableAndArgs += ["--model", "128"]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    #elif method == "ep128emu (Spectrum 48K)":
    #    # assuming a single file
    #
    #    executableAndArgs = ["ep128emu", "-zx", "-cfg", os.path.expanduser("~") + "/.ep128emu/config/zx/ZX_48k.cfg"]
    #
    #    # If a snapshot
    #    if utils.stringEndsWith(i_gameFilePaths[0], ".sna", False) or utils.stringEndsWith(i_gameFilePaths[0], ".z80", False):
    #        executableAndArgs.append("-snapshot", i_gameFilePaths[0])
    #    # Else assume it's a tape
    #    else:
    #        executableAndArgs.append("tape.imageFile=" + i_gameFilePaths[0])
    #
    #    print(executableAndArgs)
    #    utils.shellStartTask(executableAndArgs)
    #    #dan.process.shellStartString(" ".join(executableAndArgs))
    #
    #elif method == "ep128emu (Spectrum 128K)":
    #    # assuming a single file
    #
    #    executableAndArgs = ["ep128emu", "-zx", "-cfg", os.path.expanduser("~") + "/.ep128emu/config/zx/ZX_128k.cfg"]
    #
    #    # If a snapshot
    #    # [currently here for consistency, though ep128emu doesn't accept snapshots with 128K configurations and will exit with error]
    #    if (utils.stringEndsWith(i_gameFilePaths[0], ".sna", False) or utils.stringEndsWith(i_gameFilePaths[0], ".z80", False)):
    #        executableAndArgs.append("-snapshot", i_gameFilePaths[0])
    #    # Else assume it's a tape
    #    else:
    #        executableAndArgs.append("tape.imageFile=" + i_gameFilePaths[0])
    #
    #    utils.shellStartTask(executableAndArgs)

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
