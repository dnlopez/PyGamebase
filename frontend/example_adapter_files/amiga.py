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


def runGameWithMame(i_machineName, i_gameFilePaths):
    """
    Params:
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
    executableAndArgs = ["/mnt/ve/prog/c/mame_git/mame64_0240", i_machineName]

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

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameWithFsuae(i_modelName, i_gameFilePaths):
    """
    Params:
     i_modelName:
      (str)
      One of
       "A500"
       "A600"
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["fs-uae"]

    # Choose ROM [so not AROS]
    if i_modelName == "A500":
        executableAndArgs += ["--kickstart_file=/mnt/ve/emulator/Commodore Amiga/roms/System ROMs/Kickstart v1.3 rev 34.5 (1987)(Commodore)(A500-A1000-A2000-CDTV)[!].rom"]
    elif i_modelName == "A600":
        executableAndArgs += ["--kickstart_file=/mnt/ve/emulator/Commodore Amiga/roms/System ROMs/Kickstart v2.04 rev 37.175 (1991)(Commodore)(A500+)[!].rom"]
    else:
        executableAndArgs += ["--kickstart_file=/mnt/ve/emulator/Commodore Amiga/roms/System ROMs/Kickstart v2.04 rev 37.175 (1991)(Commodore)(A500+)[!].rom"]
        #print('model name "' + i_modelName + '" not recognised')
        #sys.exit(1)
    executableAndArgs += ["--amiga_model=" + i_modelName]

    executableAndArgs += ["--base_dir=/home/daniel/Documents/FS-UAE"]

    # For up to 4 floppy disks,
    # add floppy drives with those disks
    floppyDiskFilePathNo = 0
    while floppyDiskFilePathNo < 4 and floppyDiskFilePathNo < len(i_gameFilePaths):
        executableAndArgs += ["--floppy_drive_" + str(floppyDiskFilePathNo) + "=" + i_gameFilePaths[floppyDiskFilePathNo]]
        floppyDiskFilePathNo += 1
    # Register all disk images for use in swapper regardless
    for floppyDiskFilePathNo, floppyDiskFilePath in enumerate(i_gameFilePaths):
        executableAndArgs += ["--floppy_image_" + str(floppyDiskFilePathNo) + "=" + floppyDiskFilePath]

    executableAndArgs += ["--fullscreen=1"]
    executableAndArgs += ["--joystick_port_0=Mouse"]
    executableAndArgs += ["--joystick_port_0_mode=mouse"]
    executableAndArgs += ["--joystick_port_1=HID 6666:0667"]
    executableAndArgs += ["--joystick_port_1_mode=joystick"]
    executableAndArgs += ["--joystick_port_2=none"]
    executableAndArgs += ["--joystick_port_2_mode=none"]
    executableAndArgs += ["--joystick_port_3=none"]
    executableAndArgs += ["--joystick_port_3_mode=none"]
    #executableAndArgs += executableAndArgs  # [maybe belongs at end, but currently may only consist of --kickstart_file]
    executableAndArgs += ["--maximized=1"]
    executableAndArgs += ["--state_dir=/home/daniel/Documents/FS-UAE/Save States/GameBase"]
    executableAndArgs += ["--video_sync=1"]
    executableAndArgs += ["--video_sync_method=swap"]
    executableAndArgs += ['--bezel=0']
    executableAndArgs += ['--scanlines=1']
    executableAndArgs += ['--stretch=1']

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
        "rezfsuae A500",
        "rezfsuae A600",
        "mame a500 (Amiga 500 (PAL))",
        "mame a500 (Amiga 500 (PAL))",
        "mame a500n (Amiga 500 (NTSC))",
        "mame a600 (Amiga 600 (PAL))",
        "mame a600n (Amiga 600 (NTSC))",
        "mame a1200 (Amiga 1200 (PAL))",
        "mame a1200n (Amiga 1200 (NTSC))",
    ])

    if method == "rezfsuae A500":
        runGameWithFsuae("A500", i_gameFilePaths)
    elif method == "rezfsuae A600":
        runGameWithFsuae("A600", i_gameFilePaths)
    elif method == "mame a500 (Amiga 500 (PAL))":
        runGameWithMame("a500", i_gameFilePaths)
    elif method == "mame a500 (Amiga 500 (PAL))":
        runGameWithMame("a500", i_gameFilePaths)
    elif method == "mame a500n (Amiga 500 (NTSC))":
        runGameWithMame("a500n", i_gameFilePaths)
    elif method == "mame a600 (Amiga 600 (PAL))":
        runGameWithMame("a600", i_gameFilePaths)
    elif method == "mame a600n (Amiga 600 (NTSC))":
        runGameWithMame("a600n", i_gameFilePaths)
    elif method == "mame a1200 (Amiga 1200 (PAL))":
        runGameWithMame("a1200", i_gameFilePaths)
    elif method == "mame a1200n (Amiga 1200 (NTSC))":
        runGameWithMame("a1200n", i_gameFilePaths)

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

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        #
        runGameMenu(utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
