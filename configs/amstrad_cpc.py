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
config_title = "Amstrad CPC v7"
gamebaseBaseDirPath = driveBasePath + "/games/Amstrad CPC/gamebases/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC"
config_databaseFilePath = gamebaseBaseDirPath + "/Amstrad CPC_v7.sqlite"
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
       "spectrum"
       "spec128"
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
    utils.shellStartTask(executableAndArgs)

def runGame2(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """

    method = utils.popupMenu([
        "rezmame cpc464p floppydiskN",
        "rezmame gx4000 cart",
        "caprice",
        "rezep128emu_cpc (Amstrad CPC 464, with tape)",
        "rezep128emu_cpc (Amstrad CPC 664, with disk)",
        "rezep128emu_cpc (Amstrad CPC 6128, with disk)"
        #"ep128emu (Amstrad CPC 464), tape",
        #"ep128emu (Amstrad CPC 664, with disk)",
        #"ep128emu (Amstrad CPC 6128, with disk)",
    ])


    if method == "rezmame cpc464p floppydiskN":
        executableAndArgs = ["rezmame.py"]
        executableAndArgs += ["cpc464p"]

        # According to MAME, cpc464p requires a cartridge
        #executableAndArgs += ["-cart", "sysuk"]
        executableAndArgs += ["-cart", gamebaseBaseDirPath + "/Emulators/WinAPE/ROM/CPC_PLUS.CPR"]

        #
        executableAndArgs.append("-floppydisk1")
        executableAndArgs.append(i_gameFilePaths[0])
        if len(i_gameFilePaths) >= 2:
            executableAndArgs.append("-floppydisk2")
            executableAndArgs.append(i_gameFilePaths[1])

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    elif method == "rezmame gx4000 cart":
        executableAndArgs = ["rezmame.py"]
        executableAndArgs += ["gx4000"]

        executableAndArgs += ["-cart", i_gameFilePaths[0]]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    elif method == "caprice":
        executableAndArgs = ["cap32"]

        executableAndArgs += i_gameFilePaths

        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 464, with tape)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "464"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 664, with disk)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "664"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 6128, with disk)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "6128"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellStartTask(executableAndArgs)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # Extract zip
    basePath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = "/tmp/gamebase"
    zipMembers = utils.extractZip(basePath + i_gamePath, tempDirPath)

    # Filter non-game files out of zip member list
    gameFiles = [zipMember
                 for zipMember in zipMembers
                 if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".SCR"))]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if i_gameInfo["Publisher"]:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If zip file
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract zip
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["Name"]
        if i_gameInfo["Publisher"]:
            gameDescription += " (" + i_gameInfo["Publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
