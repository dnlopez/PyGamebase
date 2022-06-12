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
config_title = "Commodore VIC-20 v03"
gamebaseBaseDirPath = driveBasePath + "/games/Commodore VIC-20/gamebases/Gamebase20_v03/Vic20_v03"
config_databaseFilePath = gamebaseBaseDirPath + "/Vic20_v03.sqlite"
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
    #  ************************
    #  * WinVICE GEMUS Script *
    #  *   (c) The GB Team    *
    #  *   16 December 2009   *
    #  ************************
    # 
    #  PLEASE SET YOUR EMULATOR PROPERTIES AS FOLLOWS:
    # 
    #  Emulator File: XVIC.EXE
    #  Associated File (1): vice.ini
    #  Use Short Filenames: YES
    #  File Types:  D64;T64;G64;G41;TAP;CRT;P00;PRG
    # 
    #  This script was written for WinVICE v2.2 but
    #  may work with other versions too.
    # 
    #  Memory configuration is set through the key=value pair:
    #  memory=x
    #  where x is: none,all,3k,8k,16k,24k,"0,1,2,3,5" or "04,20,40,60,A0"
    #  as specified in the VICE manual section 7.2.2.2
    #  (Note: the Memory Expansion field can not be used by GEMUS)
    # 
    #  If the program requires a SYS call to start, then use:
    #  sys=x
    #  where x is the starting address as entered from BASIC
    #  and it will be displayed in a REM statement in the emulator
    # 
    #  Multipart cartridges must have the memory locations in the file names.
    #  The cartridge memory locations are set in the key=value pairs
    #  cart=A
    #  cart2=B
    #  where A and B are 2000,4000,6000,a000 or b000 (or 20,40,60,a0 or b0).
    #  Single carts may need to have a cart=A value set..


    if not utils.pathHasExtension(i_gameFilePaths[0], [".d64", ".t64", ".g64", ".g41", ".tap", ".crt", ".prg"]):
        # Invalid game file type
        utils.messageBox("GAME_NOT_SUPPORTED\nSupported types: D64, T64, G64/G41, TAP, CRT, PRG, P00")
    else:

        # set paths to file location for possible image swaps
        #Set_INI_Value(1, "VIC20", "InitialDiskDir", "%gamepath%")
        #Set_INI_Value(1, "VIC20", "InitialTapeDir", "%gamepath%")
        #Set_INI_Value(1, "VIC20", "InitialCartDir", "%gamepath%")
        #Set_INI_Value(1, "VIC20", "InitialAutostartDir", "%gamepath%")
        pass

        # Specify ROMs at memory locations
        if gemus.fieldNotEmpty("cart"):
            if gemus.fieldContains("cart", "20"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("20") != -1:
                        args += ["-cart2", gameFilePath]
            elif gemus.fieldContains("cart", "40"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("40") != -1:
                        args += ["-cart4", gameFilePath]
            elif gemus.fieldContains("cart", "60"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("60") != -1:
                        args += ["-cart6", gameFilePath]
            elif gemus.fieldContains("cart", "a0"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("a0") != -1:
                        args += ["-cartA", gameFilePath]
            elif gemus.fieldContains("cart", "b0"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("b0") != -1:
                        args += ["-cartB", gameFilePath]

            if gemus.fieldContains("cart2", "20"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("20") != -1:
                        args += ["-cart2", gameFilePath]
            elif gemus.fieldContains("cart2", "40"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("40") != -1:
                        args += ["-cart4", gameFilePath]
            elif gemus.fieldContains("cart2", "60"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("60") != -1:
                        args += ["-cart6", gameFilePath]
            elif gemus.fieldContains("cart2", "a0"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("a0") != -1:
                        args += ["-cartA", gameFilePath]
            elif gemus.fieldContains("cart2", "b0"):
                for gameFilePath in i_gameFilePaths:
                    if os.path.basename(gameFilePath).find("b0") != -1:
                        args += ["-cartB", gameFilePath]

            # Type a SYS command to load the game if needed
            if i_gameInfo["V_Comment"].index("load manually") != -1:  # [find no examples in database of V_Comment containing "load manually"]
                if gemus.fieldNotEmpty("sys"):
                    args += ["-keybuf", "REM LOAD MANUALLY THEN START WITH SYS" + gemus.get("sys") + "\n"]
                else:
                    args += ["-keybuf", "REM LOAD MANUALLY THEN SOFT RESET TO START\n"]
            else:
                if gemus.fieldNotEmpty("sys"):
                    args += ["-keybuf", "SYS" + gemus.get("sys") + "\n"]
        """
        else:
            pass
            ;autostart or 'manual load' the game image (with SYS call messages)
            If ImageName CONTAINS(*)
                If VersionComment CONTAINS(*load manually*)
                    ;check if a SYS call is needed to start
                    If Key_sys CONTAINS(*)
                        Add_CLP( -keybuf "REM LOAD MANUALLY THENSTART WITH SYS%sys_value%%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%:%c64imagename%")
                    Else
                        Add_CLP( -keybuf "REM YOU MUST LOAD AND START MANUALLY%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%:%c64imagename%")
                    End If
                Else
                    ;check if a SYS call is needed to start
                    If Key_sys CONTAINS(*)
                        Add_CLP( -keybuf "%crlfx2%%crlfx2%SYS%sys_value% PRESS ENTER%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%:%c64imagename%")
                    Else
                        Add_CLP2( -autostart "%gamepathfile%:%c64imagename%")
                    End If
                End If
            Else
                If VersionComment CONTAINS(*load manually*)
                    ;check if a SYS call is needed to start
                    If Key_sys CONTAINS(*)
                        Add_CLP( -keybuf "REM LOAD MANUALLY THENSTART WITH SYS%sys_value%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%)
                    Else
                        Add_CLP( -keybuf "REM YOU MUST LOAD AND START MANUALLY%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%)
                    End If
                Else
                    ;check if a SYS call is needed to start
                    If Key_sys CONTAINS(*)
                        Add_CLP( -keybuf "%crlf%%crlfx2%%crlfx2%%crlfx2%SYS%sys_value% PRESS ENTER%crlf%")
                        Add_CLP2( -autoload "%gamepathfile%")
                    Else
                        Add_CLP2( -autostart "%gamepathfile%")
                    End If
                End If
            End If
        """

        # Run in PAL or NTSC
        if i_gameInfo["V_PalNTSC"] == 2:  # NTSC
            args += ["-ntsc"]
        else:
            args += ["-pal"]

        # Use expanded memory
        if gemus.fieldNotEmpty("memory"):
            args += ["-memory", gemus.get("memory")]
        else:
            args += ["-memory", "none"]

        # Set the game controls
        """
        ;0=None, 1=Numpad + RCtrl, 2=Keyset A, 3=Keyset B, 4+ are for real joysticks/pads;
        If %gamefile% CONTAINS(*)
            If Control = JoyPort2
                ;Add_CLP( -joydev2 2)
                If NumPlayers > 1
                    Add_CLP( -joydev1 3)
                Else
                    Add_CLP( -joydev1 0)
                End If
            ElseIf Control = JoyPort1
                ;Add_CLP( -joydev1 2)
                If NumPlayers > 1
                    ;Add_CLP( -joydev2 3)
                Else
                    ;Add_CLP( -joydev2 0)
                End If
            Else
                Add_CLP( -joydev1 0)
                ;Add_CLP( -joydev2 0)
            End If
        End If

        ;unsupported game controls
        If Control = PaddlePort1
            utils.messageBox("Use Vice 2.2 onwards for paddle emulation.\nPress Alt Q to enable paddle control with the mouse.")
        ElseIf Control = PaddlePort2
            utils.messageBox("Use Vice 2.2 onwards for paddle emulation.\nPress Alt Q to enable paddle control with the mouse.")
        End If
        """

        """
        # [V_Comment seems to be empty throughout]
        ;give the user a warning message?
        If VersionComment CONTAINS(*use real Vic20*)
            utils.messageBox("This game may not work properly with this emulator.\nSee Version Comment for more info.")
        End If
        If VersionComment CONTAINS(*not 100%*||*not working*||*doesn't work*)
            utils.messageBox("This game may not work properly.")
        End If
        If VersionComment CONTAINS(*load manually*)
            utils.messageBox("You must load this game manually within the emulator.\nGame file: %gamepathfile%")
        End If
        If VersionComment CONTAINS(*PET Emulator*)
            utils.messageBox("Use PET Emulator to run this game.")
        End If
        """

    return args