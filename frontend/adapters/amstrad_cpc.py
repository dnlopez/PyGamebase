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
config_title = "Amstrad CPC v7"
gamebaseBaseDirPath = driveBasePath + "/games/Amstrad CPC/gamebases/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC"
config_databaseFilePath = gamebaseBaseDirPath + "/Amstrad CPC_v7.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


## According to MAME, cpc464p requires a cartridge
##executableAndArgs += ["-cart", "sysuk"]
#executableAndArgs += ["-cart", gamebaseBaseDirPath + "/Emulators/WinAPE/ROM/CPC_PLUS.CPR"]

def runGameWithRezmame(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (str)
      One of
       "cpc464"
       "cpc664"
       "cpc6128"
       "gx4000"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    # Assign game files to available MAME media slots
    if i_machineName == "cpc464":
        availableDevices = [
            ['printout', ['.prn']],
            ['snapshot', ['.sna']],
            ['cassette', ['.wav', '.cdt']]
        ]
    elif i_machineName == "cpc664":
        availableDevices = [
            ['printout', ['.prn']],
            ['snapshot', ['.sna']],
            ['cassette', ['.wav', '.cdt']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk']]
        ]
    elif i_machineName == "cpc6128":
        availableDevices = [
            ['printout', ['.prn']],
            ['snapshot', ['.sna']],
            ['cassette', ['.wav', '.cdt']],
            ['floppydisk1', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk']],
            ['floppydisk2', ['.mfi', '.dfi', '.hfe', '.mfm', '.td0', '.imd', '.d77', '.d88', '.1dd', '.cqm', '.cqi', '.dsk']]
        ]
    elif i_machineName == "gx4000":
        availableDevices = [
            ['cartridge', ['.bin', '.cpr']]
        ]
    executableAndArgs.extend(utils.allocateGameFilesToMameMediaSlots(i_gameFilePaths, availableDevices))

    if i_gameDescription:
        executableAndArgs.extend(["--game-description", i_gameDescription])

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameMenu(i_gameDescription, i_gameFilePaths, i_gemusText):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
     i_gemusText:
      (str)
    """
    method = utils.popupMenu([
        "rezmame cpc464 (Amstrad CPC464)",
        "rezmame cpc664 (Amstrad CPC664)",
        "rezmame cpc6128 (Amstrad CPC6128)",
        "rezmame gx4000 (Amstrad GX4000)",
        "Caprice",
        "rezep128emu_cpc (Amstrad CPC 464, with tape)",
        "rezep128emu_cpc (Amstrad CPC 664, with disk)",
        "rezep128emu_cpc (Amstrad CPC 6128, with disk)"
        #"ep128emu (Amstrad CPC 464), tape",
        #"ep128emu (Amstrad CPC 664, with disk)",
        #"ep128emu (Amstrad CPC 6128, with disk)",
    ])


    if method == "rezmame cpc464 (Amstrad CPC464)":
        runGameWithRezmame(i_gameDescription, "cpc464", i_gameFilePaths)
    elif method == "rezmame cpc664 (Amstrad CPC664)":
        runGameWithRezmame(i_gameDescription, "cpc664", i_gameFilePaths)
    elif method == "rezmame cpc6128 (Amstrad CPC6128)":
        runGameWithRezmame(i_gameDescription, "cpc6128", i_gameFilePaths)
    elif method == "rezmame gx4000 (Amstrad GX4000)":
        runGameWithRezmame(i_gameDescription, "gx4000", i_gameFilePaths)
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

    #
    gemus = utils.Gemus(i_gemusText)
    runProgram = gemus.get("run")
    if runProgram != None:
        import time
        time.sleep(5)
        utils.typeOnKeyboard([0.05, "run{shift+}2" + runProgram + "{enter}"])

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
    runGameMenu(gameDescription, utils.joinPaths(tempDirPath, gameFiles), i_gameInfo["Gemus"])

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
        runGameMenu(gameDescription, utils.joinPaths(tempDirPath, zipMembers), i_gameInfo["Gemus"])
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
