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
config_title = "Sinclair ZX Spectrum (Speccymania v5)"
gamebaseBaseDirPath = driveBasePath + "/games/Sinclair ZX Spectrum/gamebases/Speccymania v5/Sinclair ZX Spectrum"
config_databaseFilePath = gamebaseBaseDirPath + "/SpeccyMania_v5.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_photosBaseDirPath = gamebaseBaseDirPath + "/Musician Photos"
config_musicBaseDirPath = gamebaseBaseDirPath + "/C64Music"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithMame(i_machineName, i_gameFilePaths):
    """
    Params:
     i_machineName:
      (str)
      One of
       "spectrum"
       "spec128"
       "specpls3"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["/mnt/ve/prog/c/mame_git/mame64_0240", i_machineName]

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
    print(i_gameFilePaths)
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
        "mame spectrum",
        "mame spec128",
        "mame specpls3",
        "fuse (Spectrum 48K)",
        "fuse (Spectrum 128K)",
        "rezep128emu_zx (Spectrum 48K)",
        "rezep128emu_zx (Spectrum 128K)"
    ])

    if method == "mame spectrum":
        runGameWithMame("spectrum", i_gameFilePaths)

    elif method == "mame spec128":
        runGameWithMame("spec128", i_gameFilePaths)

    elif method == "mame specpls3":
        runGameWithMame("specpls3", i_gameFilePaths)

    elif method == "fuse (Spectrum 48K)":
        executableAndArgs = ["fuse", "--machine", "48"] + i_gameFilePaths
        utils.shellStartTask(executableAndArgs)

    elif method == "fuse (Spectrum 128K)":
        executableAndArgs = ["fuse", "--machine", "128"] + i_gameFilePaths
        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 48K)":
        executableAndArgs = ["ep128emu", "-zx"]

        # Assume a single file
        #  If a snapshot
        if i_gameFilePaths[0].upper().endswith(".SNA") or i_gameFilePaths[0].upper().endswith(".Z80"):
            executableAndArgs += ["-snapshot", i_gameFilePaths[0]]
        #  Else assume it's a tape
        else:
            executableAndArgs += ["tape.imageFile=" + i_gameFilePaths[0]]

        executableAndArgs += ["-cfg", "/home/daniel/.ep128emu/config/zx/ZX_48k.cfg"]

        utils.directStartTask(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 128K)":
        executableAndArgs = ["rezep128emu_zx.py"]

        # Assume a single file
        #  If a snapshot
        if i_gameFilePaths[0].upper().endswith(".SNA") or i_gameFilePaths[0].upper().endswith(".Z80"):
            executableAndArgs += ["-snapshot", i_gameFilePaths[0]]
        #  Else assume it's a tape
        else:
            executableAndArgs += ["tape.imageFile=" + i_gameFilePaths[0]]

        executableAndArgs += ["-cfg", "/home/daniel/.ep128emu/config/zx/ZX_128k.cfg"]

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

def runMusic(i_musicPath, i_gameInfo):
    #print('runMusic(' + pprint.pformat(i_musicPath) + ', ' + pprint.pformat(i_gameInfo) + ')')

    utils.openInDefaultApplication(config_musicBaseDirPath + "/" + i_musicPath)
