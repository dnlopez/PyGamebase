# Python std
import os.path
import pprint

# This program
import utils


config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/Amstrad CPC.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Amstrad CPC/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Amstrad CPC/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC/Extras"



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
        executableAndArgs += ["-cart", "/mnt/ve/games/Amstrad CPC/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC/Emulators/WinAPE/ROM/CPC_PLUS.CPR"]
        #
        executableAndArgs.append("-floppydisk1")
        executableAndArgs.append(i_gameFilePaths[0])
        if len(i_gameFilePaths) >= 2:
            executableAndArgs.append("-floppydisk2")
            executableAndArgs.append(i_gameFilePaths[1])

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

    elif method == "rezmame gx4000 cart":
        executableAndArgs = ["rezmame.py"]
        executableAndArgs += ["gx4000"]

        executableAndArgs += ["-cart", i_gameFilePaths[0]]

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

    elif method == "caprice":
        executableAndArgs = ["cap32"]

        executableAndArgs += i_gameFilePaths

        utils.shellExecList(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 464, with tape)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "464"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 664, with disk)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "664"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

    elif method == "rezep128emu_cpc (Amstrad CPC 6128, with disk)":
        executableAndArgs = ["rezep128emu_cpc.py"]

        executableAndArgs += ["--model", "6128"]

        executableAndArgs += i_gameFilePaths

        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        utils.shellExecList(executableAndArgs)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # Extract zip
    basePath = "/mnt/ve/games/Amstrad CPC/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC/Games/"
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

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

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
