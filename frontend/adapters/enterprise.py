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
config_title = "Enterprise"
gamebaseBaseDirPath = driveBasePath + "/games/Elan Enterprise/gamebases/Vicman_GameBase_v1.0/Enterprise"
config_databaseFilePath = gamebaseBaseDirPath + "/Enterprise.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithVice(i_gameDescription, i_gameFilePaths, i_gameInfo):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    print(i_gameFilePaths)
    executableAndArgs = ["xvic"]
    executableAndArgs += xvicGemusScript(i_gameFilePaths, i_gameInfo)
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)
    return

    executableAndArgs = ["rezvice_xvic.py"]

    executableAndArgs += ["--region", "pal"]

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--"]

    if utils.pathHasExtension(i_gameFilePaths[0], ".CRT"):
        executableAndArgs.append("-cartgeneric")

    executableAndArgs += i_gameFilePaths

    # Execute
    print(executableAndArgs)
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

    runGameWithVice(gameDescription, utils.joinPaths(tempDirPath, gameFiles), i_gameInfo)

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
        runGameWithVice(gameDescription, utils.joinPaths(tempDirPath, zipMembers), i_gameInfo)
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)


def xvicGemusScript(i_gameFilePaths, i_gameInfo):
    args = []

    gemus = utils.Gemus(i_gameInfo["Gemus"])

    # Adapted from:
    # GEMUS SCRIPT FOR Enterprise 64/128
    # Version 2.0
    # created by .mad.in Jan.2011

    # Because different config.cfg's are needed for the games, this script uses the 'Set_CFG_Item' function.
    # The gb.cfg will be created in the folder: GameBase/Enterprise/Emulator/ep128emu2/gb.cfg
    # Your %gbgamepath% must be Set to C:/GBGame/0 (where GameBase extracts and runs game files) otherwise you have to edit this script manually

    #---------------------------------------------------------------------------------
    #Setup Working Path = Must be Gamebase Unzip Path.
    #Alternative commands that work, if you want to move the Gamebase path.
    #---------------------------------------------------------------------------------
    # Set_CFG_Item(fileio.workingDirectory, "\t", "C:/gbgame/0")
    # Add_CLP(-fileio.workingDirectory="C:/GBGame/0")

    # Set_CFG_Item(floppy.a.imageFile, "\t", "C:/GBGAME/0/GAMES_01.IMG")
    # Add_CLP(-floppy.a.imageFile="C:/GBGame/0/GAMES_01.IMG")

    # Set_CFG_Item(%emupath%\config-gb\test.cfg, floppy.a.imageFile, "\t", %floppy.a.imageFile_value%)
    # Set_CFG_Item(%emupath%\config-gb\test.cfg, floppy.a.imageFile, "\t", "E:/GBGame/0/GAMES_01.IMG")
    # Add_CLP(-cfg gb.cfg -fileio.workingDirectory="C:/GBGame/0" -floppy.a.imageFile="C:/GBGame/0/GAMES_01.IMG")

    ##--------------------------------------------------
    ## Start of script

    configLines = []
    #configFilePath = node_path.join(tempDirPath, "gb.cfg")

    # Eject any floppy before running
    configLines.append('floppy.a.imageFile ""')

    # + Future use {{{

    #---------------------------------------------------------------------------------
    # Virtual Machine Settings (Clock Speed) ** Future Use **
    #---------------------------------------------------------------------------------
    #configLines.append('vm.cpuClockFrequency 4000000')
    #configLines.append('vm.enableFileIO Yes')
    #configLines.append('vm.enableMemoryTimingEmulation Yes')
    #configLines.append('vm.processPriority 0')
    #configLines.append('vm.soundClockFrequency 500000')
    #configLines.append('vm.speedPercentage 100')
    #configLines.append('vm.videoClockFrequency 889846')

    #---------------------------------------------------------------------------------
    # Default Tape Settings ** Future Use **
    #---------------------------------------------------------------------------------
    #configLines.append('tape.imageFile ')

    #configLines.append('tape.defaultSampleRate 24000')
    #configLines.append('tape.enableSoundFileFilter No')
    #configLines.append('tape.soundFileChannel 0')
    #configLines.append('tape.soundFileFilterMaxFreq 5000')
    #configLines.append('tape.soundFileFilterMinFreq 500')

    #---------------------------------------------------------------------------------
    # Floppy /IDE Disk Settings ** Future Use **
    #---------------------------------------------------------------------------------
    #configLines.append('floppy.a.imageFile ')

    #configLines.append('floppy.a.sectorsPerTrack -1')
    #configLines.append('floppy.a.sides -1')
    #configLines.append('floppy.a.tracks -1')

    #configLines.append('floppy.b.imageFile ')
    #configLines.append('floppy.b.sectorsPerTrack -1')
    #configLines.append('floppy.b.sides -1')
    #configLines.append('floppy.b.tracks -1')

    #configLines.append('floppy.c.imageFile ')
    #configLines.append('floppy.c.sectorsPerTrack -1')
    #configLines.append('floppy.c.sides -1')
    #configLines.append('floppy.c.tracks -1')

    #configLines.append('floppy.d.imageFile ')
    #configLines.append('floppy.d.sectorsPerTrack -1')
    #configLines.append('floppy.d.sides -1')
    #configLines.append('floppy.d.tracks -1')

    #configLines.append('ide.imageFile0 ')
    #configLines.append('ide.imageFile1 ')
    #configLines.append('ide.imageFile2 ')
    #configLines.append('ide.imageFile3 ')

    #---------------------------------------------------------------------------------
    # Default Joystick Settings ** Future Use **
    #---------------------------------------------------------------------------------
    #If Key_Joysick CONTAINS(*)
    #configLines.append('joystick.autoFireFrequency 8')
    #configLines.append('joystick.autoFirePulseWidth 0.5')
    #configLines.append('joystick.axisThreshold 0.5')
    #configLines.append('joystick.enableAutoFire No')
    #configLines.append('joystick.enableJoystick Yes')
    #configLines.append('joystick.enablePWM No')
    #configLines.append('joystick.pwmFrequency 17.5')
    #End IF

    # + }}}

    # Joystick (internal) mapped to cursor keys & Space or Enter for some games
    if i_gameInfo["Control"] == 1:  # JoyPort2
        configLines.append('keyboard.70.0 65465')
        configLines.append('keyboard.70.1 49153')
        configLines.append('keyboard.71.0 65463')
        configLines.append('keyboard.71.1 49152')
        configLines.append('keyboard.72.0 65461')
        configLines.append('keyboard.72.1 49155')
        configLines.append('keyboard.73.0 65455')
        configLines.append('keyboard.73.1 49154')
        configLines.append('keyboard.74.0 65451')
        configLines.append('keyboard.74.1 49168')
        configLines.append('keyboard.75.0 -1')
        configLines.append('keyboard.75.1 -1')
        configLines.append('keyboard.76.0 -1')
        configLines.append('keyboard.76.1 -1')
        configLines.append('keyboard.77.0 -1')
        configLines.append('keyboard.77.1 -1')
        configLines.append('keyboard.78.0 65462')
        configLines.append('keyboard.78.1 49157')
        configLines.append('keyboard.79.0 65460')
        configLines.append('keyboard.79.1 49156')
        configLines.append('keyboard.7A.0 65458')
        configLines.append('keyboard.7A.1 49159')
        configLines.append('keyboard.7B.0 65464')
        configLines.append('keyboard.7B.1 49158')
        configLines.append('keyboard.7C.0 65456')
        configLines.append('keyboard.7C.1 49169')
        configLines.append('keyboard.7D.0 -1')
        configLines.append('keyboard.7D.1 -1')
        configLines.append('keyboard.7E.0 -1')
        configLines.append('keyboard.7E.1 -1')
        configLines.append('keyboard.7F.0 -1')
        configLines.append('keyboard.7F.1 -1')
    # [no Gemus values contain "Joy"]
    elif gemus.fieldContains("Joy", "EXT1"):
        configLines.append('joystick.enableJoystick Yes')

        configLines.append('keyboard.70.0 49153')
        configLines.append('keyboard.70.1 65363')
        configLines.append('keyboard.71.0 49152')
        configLines.append('keyboard.71.1 65361')
        configLines.append('keyboard.72.0 49155')
        configLines.append('keyboard.72.1 65364')
        configLines.append('keyboard.73.0 49154')
        configLines.append('keyboard.73.1 65362')
        configLines.append('keyboard.74.0 49168')
        configLines.append('keyboard.74.1 65508')
    # [no Gemus values contain "Joy"]
    elif gemus.fieldContains("Joy", "EXT2"):
        configLines.append('joystick.enableJoystick Yes')

        configLines.append('keyboard.78.0 49153')
        configLines.append('keyboard.78.1 65363')
        configLines.append('keyboard.79.0 49152')
        configLines.append('keyboard.79.1 65361')
        configLines.append('keyboard.7A.0 49155')
        configLines.append('keyboard.7A.1 65364')
        configLines.append('keyboard.7B.0 49154')
        configLines.append('keyboard.7B.1 65362')
        configLines.append('keyboard.7C.0 49168')
        configLines.append('keyboard.7C.1 65508')


    # Restore SPECIAL mapped keys
    configLines.append('keyboard.07.0 65505')
    configLines.append('keyboard.07.1 -1')
    configLines.append('keyboard.35.0 39')
    configLines.append('keyboard.35.1 -1')
    configLines.append('keyboard.45.0 65506')
    configLines.append('keyboard.45.1 -1')


    # If Hungarian keyboard [only Zork I]
    if gemus.fieldContains("keyboard", "HU") or gemus.fieldContains("keyboard", "Hungarian"):
        configLines.append('keyboard.06.0 121')
        configLines.append('keyboard.12.0 122')
        configLines.append('keyboard.2B.0 47')
        configLines.append('keyboard.2C.0 96')
        configLines.append('keyboard.43.0 45')
        configLines.append('keyboard.4B.0 48')
    # else if USA,
    # reset all keyboard mapped keys
    else:
        configLines.append('keyboard.06.0 122')
        configLines.append('keyboard.12.0 121')
        configLines.append('keyboard.2B.0 45')
        configLines.append('keyboard.2C.0 48')
        configLines.append('keyboard.43.0 47')
        configLines.append('keyboard.4B.0 96')

    """
    # Emulator window size - small, medium, large
    # [no Gemus values contain "window"]
    if gemus.fieldContains("window", "large"):
    {
        configLines.append('display.height 864')
        configLines.append('display.width 1152')
    }
    elif gemus.fieldContains("window", "medium"):
    {
        configLines.append('display.height 576')
        configLines.append('display.width 768')
    }
    # set small as default (384x228)
    else:
    {
        configLines.append('display.height 228')
        configLines.append('display.width 384')
    }
    """

    ep128ConfigDirPath = "/home/daniel/.ep128emu"

    # Run tapes in Spectrum emulator J""
    # [used by
    #   Bugaboo the Flea
    #   Cavern Fighter
    #   Zaxxon]
    if gemus.fieldContains("load", "tape"):
        configLines.append('memory.configFile ""')
        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        #-------------------------------------
        # Swap Left and Right SHIFT Keys
        #-------------------------------------
        configLines.append('keyboard.07.0 65506')
        configLines.append('keyboard.45.0 65505')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[2]{F1}[-1][1]%gamepathfile%[-20]{Enter}[-100][2]jPP{Enter}[1], 50)

    # Run the emulator with 640k RAM instead of 128K (ca. 60 Games)
    elif gemus.fieldContains("config", "EP640k"):
        configLines.append('memory.configFile ""')

        configLines.append('memory.ram.size 640')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([4]{Enter}[2]{F1}[-1][1]%gamepathfile%[-20]{Enter}[1], 50)

    # Run basic-files wich need the "zrom" (ca. 35 Games)
    elif gemus.fieldContains("config", "zrom2"):
        Set_CFG_Item(memory.configFile, "\t", "")

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file "' + ep128ConfigDirPath + '/roms/epdos_z.rom"')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file "' + ep128ConfigDirPath + '/roms/epdos_z.rom"')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file "' + ep128ConfigDirPath + '/roms/epdos_z.rom"')
        configLines.append('memory.rom.21.offset 16384')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[3]{F1}[-1][1]%gamepathfile%[-20]{Enter}[1], 50)

    # Run disk-images (basic prg's wich need zrom and typing run)
    elif gemus.fieldContains("runbasiczrom", "1"):
        configLines.append('floppy.a.imageFile C:/GBGame/0/Games_01.IMG')

        configLines.append('memory.configFile ""')
        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epdos_z.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file "' + ep128ConfigDirPath + '/roms/epdos_z.rom"')
        configLines.append('memory.rom.11.offset 16384')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.21.offset 16384')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[5][-30]load{C34}%gamename_value%{C34}{Enter}[3]run{Enter}, 80)

    # Run tape file with hungarian-config 128k (VIC20-Emulator and Game "Mad Mix 2")
    elif gemus.fieldContains("config", "128k-Hun"):
        configLines.append('memory.configFile ')

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file "' + ep128ConfigDirPath + '/roms/hun.rom"')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[2]{F1}[-1][1]%gamepathfile%[-20]{Enter}[1], 50)

    # Run files wich need the "brd.rom"  (ca. 14 Basic-Games)
    elif gemus.fieldContains("config", "brd"):
        configLines.append('memory.configFile ""')

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file "' + ep128ConfigDirPath + '/roms/brd.rom"')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[3]{F1}[-1][1]%gamepathfile%[-20]{Enter}[1], 50)

    # Run files wich need "EXDOS.rom" (Game Sokoban 1 & Sokoban 2 only)
    elif gemus.fieldContains("config", "exdos"):
        configLines.append('memory.configFile ""')

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.21.offset 16384')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([3]{Enter}[6]{F1}[-1][1]%gamepathfile%[-20]{Enter}[1], 50)

    # Run emulator with ISDOS (Base, Deadline, Island, Seastalker, Sokoban, Zork 1-3)
    elif gemus.fieldContains("config", "isdos"):
        configLines.append('memory.configFile ""')

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file "' + ep128ConfigDirPath + '/roms/exdos13isdos10hun.rom"')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file "' + ep128ConfigDirPath + '/roms/exdos13isdos10hun.rom"')
        configLines.append('memory.rom.21.offset 16384')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        configLines.append('floppy.a.imageFile C:/GBGAME/0/Disk.IMG')

        #* Non UK /USA Keyboard setup will flip Z and Y on Keyboard.
        #* DIR is typed instead of gamename to avoid loading error York, Zork.

        #**********************************************************************
        #German keyboard setting
        #Run_Emulator_Send_Keys([4]{Enter}[5]äisdos{Enter}[4]dir{Enter}[1], 80)
        #
        #USA Keyboard - Emulator default Setting
        #Run_Emulator_Send_Keys([4]{Enter}[5]#isdos{Enter}[4]dir{Enter}[1], 80)
        #
        #Real Machine Keyboard Setting
        #Run_Emulator_Send_Keys([4]{Enter}[5]:isdos{Enter}[4]dir{Enter}[1], 80)
        #**********************************************************************

        #-----------------------------------------------------------
        # Map Keyboard - Left Shift to :Colon: for universal setting
        # settings will reset on next loaded game file.
        #-----------------------------------------------------------
        configLines.append('keyboard.07.0 -1')
        configLines.append('keyboard.07.1 -1')
        configLines.append('keyboard.35.0 65505')
        configLines.append('keyboard.35.1 39')
        configLines.append('keyboard.45.0 65506')
        configLines.append('keyboard.45.1 -1')

        executableAndArgs.push("-cfg", "gb.cfg")
        #Run_Emulator_Send_Keys([4]{Enter}[5]{SHIFT}isdos{Enter}[4]%gamename_value%{Enter}[1], 80)

    # Run disk images (slideshow autostart or Program loader/menue)
    elif utils.pathHasExtension(gameFilePaths[0], ".img"):
        configLines.append('floppy.a.imageFile "' + utils.makePathAbsolute(tempDirPath, gameFilePaths[0]) + '"')

        configLines.append('memory.configFile ""')
        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file ""')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file "' + ep128ConfigDirPath + '/roms/exdos13.rom"')
        configLines.append('memory.rom.21.offset 16384')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        # Write config file
        node_fs.writeFileSync(configFilePath, configLines.join("\n"))
        executableAndArgs.push("-cfg", configFilePath)

        # Run emulator
        utils.shellExecList(executableAndArgs)

        #
        """
        if gemus.fieldContains("auto", ["yes", "1"]):
            #Run_Emulator_Send_Keys([3]{Enter}[5][-30]load{C34}%gamename_value%{C34}{Enter}, 80)
            await utils.wait(4)
            await utils.typeOnKeyboard("{Enter}")
            await utils.typeOnKeyboard("!w")
            await utils.wait(1)
            await utils.typeOnKeyboard("!w")
            await utils.typeOnKeyboard([0.05, 'load "' + adjustForEp128emuKeymap(gameFiles[0]) + '"{Enter}'])
        elif gemus.fieldContains("runbasic", ["yes", "1"]):
            #Run_Emulator_Send_Keys([3]{Enter}[5][-30]load{C34}%gamename_value%{C34}{Enter}[3]run{Enter}, 80)
            await utils.wait(4)
            await utils.typeOnKeyboard("{Enter}")
            await utils.typeOnKeyboard("!w")
            await utils.wait(1)
            await utils.typeOnKeyboard("!w")
            await utils.typeOnKeyboard([0.05, 'load "' + adjustForEp128emuKeymap(gameFiles[0]) + '"{Enter}'])
            await utils.typeOnKeyboard([0.05, 'run{Enter}'])
        else:
            #Run_Emulator_Send_Keys([3]{Enter}, 80)
            await utils.wait(4)
            await utils.typeOnKeyboard("{Enter}")
        """

    # Run Game in Emulator
    # Autorun the games in the 4 EP128 emulators [CPC, VIC20, TVC & ZX81]
    # [no Gemus values contain "emulator"]
    elif gemus.fieldNotEmpty("emulator"):
        #************************************************************************************
        #*      i have decided to use a "Snapshotfile" of the "Emulated Emulator"           *
        #*                                                                                  *
        #*       The Games will be load, by using the %gamename_value% - Function           *
        #************************************************************************************

        configLines.append('memory.configFile ""')

        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')


        # Run game in the Enterprise Amstrad-Emulator
        if gemus.fieldContains("emulator", "cpc"):
            executableAndArgs.push("-cfg", "gb.cfg")
            #Add_CLP(-snapshot %gamepathfile%)  TODO
            #Run_Emulator_Send_Keys([1]%gamename_value%{Enter}, 50)
        # Run game in Enterprise Vic20-Emulator
        elif gemus.fieldContains("emulator", "vic20"):
            executableAndArgs.push("-cfg", "gb.cfg")
            #Add_CLP(-snapshot %gamepathfile%)
            #Run_Emulator_Send_Keys([1]{F6}[1][-1]%gamename_value%[-50]{Enter}[1]run{Enter}, 50)
        # Run game in Enterprise TVC-Emulator
        elif gemus.fieldContains("emulator", "tvc"):
            executableAndArgs.push("-cfg", "gb.cfg")
            #Add_CLP(-snapshot %gamepathfile%)
            #Run_Emulator_Send_Keys([1]%gamename_value%{Enter}, 80)
        # Run game in Enterprise ZX81-Emulator
        elif gemus.fieldContains("emulator", "zx81"):
            executableAndArgs.push("-cfg", "gb.cfg")
            #Add_CLP(-snapshot %gamepathfile%)
            #Run_Emulator_Send_Keys([2]{Enter}[2][-1]%gamename_value%[-80]{Enter}[2]r{Enter}, 80)

    # Run all other files
    else:
        configLines.append('memory.configFile ""')
        configLines.append('memory.ram.size 128')
        configLines.append('memory.rom.00.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.00.offset 0')
        configLines.append('memory.rom.01.file "' + ep128ConfigDirPath + '/roms/exos21.rom"')
        configLines.append('memory.rom.01.offset 16384')
        configLines.append('memory.rom.02.file ""')
        configLines.append('memory.rom.02.offset 0')
        configLines.append('memory.rom.03.file ""')
        configLines.append('memory.rom.03.offset 0')
        configLines.append('memory.rom.04.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.04.offset 0')
        configLines.append('memory.rom.05.file "' + ep128ConfigDirPath + '/roms/asmon15.rom"')
        configLines.append('memory.rom.05.offset 16384')
        configLines.append('memory.rom.06.file "' + ep128ConfigDirPath + '/roms/basic21.rom"')
        configLines.append('memory.rom.06.offset 0')
        configLines.append('memory.rom.07.file ""')
        configLines.append('memory.rom.07.offset 0')
        configLines.append('memory.rom.10.file "' + ep128ConfigDirPath + '/roms/epfileio.rom"')
        configLines.append('memory.rom.10.offset 0')
        configLines.append('memory.rom.11.file ""')
        configLines.append('memory.rom.11.offset 0')
        configLines.append('memory.rom.12.file ""')
        configLines.append('memory.rom.12.offset 0')
        configLines.append('memory.rom.13.file ""')
        configLines.append('memory.rom.13.offset 0')
        configLines.append('memory.rom.20.file ""')
        configLines.append('memory.rom.20.offset 0')
        configLines.append('memory.rom.21.file ""')
        configLines.append('memory.rom.21.offset 0')
        configLines.append('memory.rom.22.file ""')
        configLines.append('memory.rom.22.offset 0')
        configLines.append('memory.rom.23.file ""')
        configLines.append('memory.rom.23.offset 0')
        configLines.append('memory.rom.30.file ""')
        configLines.append('memory.rom.30.offset 0')
        configLines.append('memory.rom.31.file ""')
        configLines.append('memory.rom.31.offset 0')
        configLines.append('memory.rom.32.file ""')
        configLines.append('memory.rom.32.offset 0')
        configLines.append('memory.rom.33.file ""')
        configLines.append('memory.rom.33.offset 0')
        configLines.append('memory.rom.40.file ""')
        configLines.append('memory.rom.40.offset 0')
        configLines.append('memory.rom.41.file ""')
        configLines.append('memory.rom.41.offset 0')
        configLines.append('memory.rom.42.file ""')
        configLines.append('memory.rom.42.offset 0')
        configLines.append('memory.rom.43.file ""')
        configLines.append('memory.rom.43.offset 0')

        # Write config file
        node_fs.writeFileSync(configFilePath, configLines.join("\n"))
        executableAndArgs.push("-cfg", configFilePath)

        # Run emulator
        utils.shellExecList(executableAndArgs)

        #
        """
        await utils.wait(4)
        await utils.typeOnKeyboard("{Enter}")
        await utils.wait(2)
        await utils.typeOnKeyboard([0.05, 'start "' + gameFiles[0] + '"{Enter}'])
        """

    return args
