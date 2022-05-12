# Python std
import os.path
import pprint

# This program
import utils


config_title = "Spectrum v4"
config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/SpeccyMania_v4.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v4/zx_up_dax_PL/ZX Spectrum/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v4/zx_up_dax_PL/ZX Spectrum/Extras"

#config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/SpeccyMania.sqlite"
#config_screenshotBasePath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania/SpeccyMania/Screenshots"
#config_screenshotBasePath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania/SpeccyMania/Extras"



def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
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

    nextFloppyDiskNo = 1
    for gameFilePath in i_gameFilePaths:
        # [".plusd" - or is it ".plusd.prg?"]
        if utils.pathHasExtension(gameFilePath, ".ach") or \
           utils.pathHasExtension(gameFilePath, ".frz") or \
           utils.pathHasExtension(gameFilePath, ".plusd") or \
           utils.pathHasExtension(gameFilePath, ".prg") or \
           utils.pathHasExtension(gameFilePath, ".sem") or \
           utils.pathHasExtension(gameFilePath, ".sit") or \
           utils.pathHasExtension(gameFilePath, ".sna") or \
           utils.pathHasExtension(gameFilePath, ".snp") or \
           utils.pathHasExtension(gameFilePath, ".snx") or \
           utils.pathHasExtension(gameFilePath, ".sp") or \
           utils.pathHasExtension(gameFilePath, ".z80") or \
           utils.pathHasExtension(gameFilePath, ".zx"):
            executableAndArgs += ["-snapshot", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".raw") or \
             utils.pathHasExtension(gameFilePath, ".scr"):
            executableAndArgs += ["-quickload", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".tzx") or \
             utils.pathHasExtension(gameFilePath, ".tap") or \
             utils.pathHasExtension(gameFilePath, ".blk"):
            executableAndArgs += ["-cassette", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".bin") or \
             utils.pathHasExtension(gameFilePath, ".rom"):
            executableAndArgs += ["-cartridge", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".d77") or \
             utils.pathHasExtension(gameFilePath, ".d88") or \
             utils.pathHasExtension(gameFilePath, ".1dd") or \
             utils.pathHasExtension(gameFilePath, ".dfi") or \
             utils.pathHasExtension(gameFilePath, ".imd") or \
             utils.pathHasExtension(gameFilePath, ".ipf") or \
             utils.pathHasExtension(gameFilePath, ".mfi") or \
             utils.pathHasExtension(gameFilePath, ".mfm") or \
             utils.pathHasExtension(gameFilePath, ".td0") or \
             utils.pathHasExtension(gameFilePath, ".cqm") or \
             utils.pathHasExtension(gameFilePath, ".cqi") or \
             utils.pathHasExtension(gameFilePath, ".dsk"):
            executableAndArgs += ["-floppydisk" + str(nextFloppyDiskNo), gameFilePath]
            nextFloppyDiskNo += 1

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    # Execute
    utils.shellExecList(executableAndArgs)

def runGame2(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    #"rezmame.py", "spectrum", "-snapshot", %f
    #"rezmame.py", "spectrum", "-cartridge", %f
    #"rezmame.py", "spectrum", "-cassette", %f

    method = utils.popupMenu([
        "rezmame spectrum",
        "rezmame spec128",
        "rezmame specpls3",
        "fuse (Spectrum 48K)",
        "fuse (Spectrum 128K)",
        "rezep128emu_zx (Spectrum 48K)",
        "rezep128emu_zx (Spectrum 128K)"
    ])
    #method = "ep128emu (Spectrum 48K)"

    if method == "rezmame spectrum":
        runGameOnMachine(i_gameDescription, "spectrum", i_gameFilePaths)

    elif method == "rezmame spec128":
        runGameOnMachine(i_gameDescription, "spec128", i_gameFilePaths)

    elif method == "rezmame specpls3":
        runGameOnMachine(i_gameDescription, "specpls3", i_gameFilePaths)

    elif method == "fuse (Spectrum 48K)":
        executableAndArgs = ["fuse", "--machine", "48"] + i_gameFilePaths
        utils.shellExecList(executableAndArgs)

    elif method == "fuse (Spectrum 128K)":
        executableAndArgs = ["fuse", "--machine", "128"] + i_gameFilePaths
        utils.shellExecList(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 48K)":
        executableAndArgs = ["rezep128emu_zx.py"]

        # assuming a single file
        executableAndArgs += ["--media", i_gameFilePaths[0]]

        executableAndArgs += ["--model", "48"]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

    elif method == "rezep128emu_zx (Spectrum 128K)":
        executableAndArgs = ["rezep128emu_zx.py"]

        # assuming a single file
        executableAndArgs += ["--media", i_gameFilePaths[0]]

        executableAndArgs += ["--model", "128"]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

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
    #    utils.shellExecList(executableAndArgs)
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
    #    utils.shellExecList(executableAndArgs)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # Extract zip
    basePath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v4/zx_up_dax_PL/ZX Spectrum/Games/"
    tempDirPath = "/tmp/gamebase"
    zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)

    # Filter non-game files out of zip member list
    gameFiles = [zipMember
                 for zipMember in zipMembers
                 if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".SCR"))]

    #
    if i_zipMemberToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_name, i_path, i_gameInfo = None):
    #print('runExtra("' + i_name + '", "' + i_path + '", ...)')

    extrasBasePath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v4/zx_up_dax_PL/ZX Spectrum/Extras/"

    # If zip file
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(extrasBasePath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(extrasBasePath + "/" + i_path)
