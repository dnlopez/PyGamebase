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
    driveBasePath = "G:"
else:
    driveBasePath = "/mnt/gear"


# Frontend configuration
config_title = "Atari 800 v12"
gamebaseBaseDirPath = driveBasePath + "/games/Atari 800/gamebases/Atari 800 v12"
config_databaseFilePath = gamebaseBaseDirPath + "/Atari 800 v12.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/screenshots"
config_photosBaseDirPath = gamebaseBaseDirPath + "/Photos"
config_musicBaseDirPath = gamebaseBaseDirPath + "/Music"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (string)
      One of
       "rezatari800.py pal"
       "rezatari800.py ntsc"
       "atari++"
     i_gameFilePaths:
      (array of string)
    """
    if i_machineName == "rezatari800.py pal":
        executableAndArgs = ["rezatari800.py"]

        executableAndArgs += ["--region", "pal"]

        #
        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        executableAndArgs += ["--"]
        executableAndArgs += i_gameFilePaths

    elif i_machineName == "rezatari800.py ntsc":
        executableAndArgs = ["rezatari800.py"]

        executableAndArgs += ["--region", "ntsc"]

        #
        if i_gameDescription != None:
            executableAndArgs += ["--game-description", i_gameDescription]

        executableAndArgs += ["--"]
        executableAndArgs += i_gameFilePaths

    elif i_machineName == "atari++":
        executableAndArgs = ["atari++"]
        executableAndArgs += i_gameFilePaths

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
        "rezatari800.py pal",
        "rezatari800.py ntsc",
        "atari++"
    ])

    if method == "rezatari800.py pal":
        runGameOnMachine(i_gameDescription, "rezatari800.py pal", i_gameFilePaths)
    elif method == "rezatari800.py ntsc":
        runGameOnMachine(i_gameDescription, "rezatari800.py ntsc", i_gameFilePaths)
    elif method == "atari++":
        runGameOnMachine(i_gameDescription, "atari++", i_gameFilePaths)

def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    os.environ["AUDIODEV"] = "sysdefault"

    # Extract zip
    gamesBaseDirPath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = tempfile.gettempdir() + "/gamebase"
    zipMembers = utils.extractZip(gamesBaseDirPath + i_gamePath, tempDirPath)

    # Filter non-game files out of zip member list
    gameFiles = [zipMember
                 for zipMember in zipMembers
                 if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR"))]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    # Get game description
    gameDescription = i_gameInfo["Name"]
    if "Publisher" in i_gameInfo:
        gameDescription += " (" + i_gameInfo["Publisher"] + ")"

    #
    runGame2(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If zip file
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract zip
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["Name"]
        if "Publisher" in i_gameInfo:
            gameDescription += " (" + i_gameInfo["Publisher"] + ")"

        #
        runGame2(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)

def runMusic(i_musicPath, i_gameInfo):
    print('runMusic(' + pprint.pformat(i_musicPath) + ', ' + pprint.pformat(i_gameInfo) + ')')

    print(config_musicBaseDirPath + "/" + i_musicPath)
    utils.openInDefaultApplication(config_musicBaseDirPath + "/" + i_musicPath)


"""
def atari800GemusScript(i_gameFilePath, i_gameInfo, i_gemusText):
    args = []

    gemus = utils.Gemus(i_gemusText)

    # From:
    #  "GEMUS SCRIPT FOR ATARI800"
    #  "Version 2.0"
    #  "Created by K.C. January 2010"
    #
    #  "File Types: xex;com;cas;bin;rom;atr;bas"
    #
    #  "This script was written for Atari800Win 2.1.0,"
    #  "but may work with other versions too."

    if gemus.fieldContains("pilotrom", "yes"):
        args += ["-cart", "pilot.rom"]
    elif utils.pathHasExtension(i_gameFilePath, [".XEX", ".COM", ".BAS"]):
        args += ["-run", i_gameFilePath]
    elif utils.pathHasExtension(i_gameFilePath, [".CAS"]):
        if gemus.fieldContains("basic", "yes"):
            if gemus.fieldContains("tape", "manual"):
                args += ["-tape", i_gameFilePath]
            else:
                args += ["-boottape", i_gameFilePath]
        else:
            args += ["-boottape", "-nobasic", i_gameFilePath]
    elif utils.pathHasExtension(i_gameFilePath, [".BIN", ".ROM"]):
        args += ["-cart", i_gameFilePath]
    elif utils.pathHasExtension(i_gameFilePath, [".ATR", ".XFD"]):
        args += [i_gameFilePath]

    if gemus.fieldContainsOneOf("fullscreen", ["true", "on", "yes", "1"]):
        args += ["-fullscreen"]
    elif gemus.fieldContainsOneOf("fullscreen", ["false", "off", "no", "0"]):
        args += ["-windowed"]
    elif gemus.get("fullscreen") != "":
        Show_Message(Invalid value for key=value pair FULLSCREEN entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    else:
        if i_gameInfo["V_TrueDriveEmu"] == "YES":
            args += ["-fullscreen"]
        else:
            args += ["-windowed"]

    args += ["-config", "GB800.TXT"]

;*****************************
; HARDWARE SETTINGS
;*****************************

If Key_model CONTAINS(osa||osb||xl||ramboxe)
    If Key_model CONTAINS(osa)
        Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari OS/A)
    ElseIf Key_model CONTAINS(osb)
        Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari OS/B)
    ElseIf Key_model CONTAINS(xl)
        Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
    ElseIf Key_model CONTAINS(ramboxe)
        Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
        Set_CFG_Value(%emupath%\GB800.TXT||RAM_SIZE||320 (RAMBO))
    End If
Else
    If Key_model CONTAINS(*)
        Show_Message(Invalid value for key=value pair MODEL entered.%crlfx2%Possible values are:%crlfx2%osa,osb, xl, ramboxe.%crlfx2%Default xl is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||RAM_SIZE||64)
    Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
End If

If Key_emuos CONTAINS(true||on||yes||1)
    Add_CLP( -emuos)
ElseIf Key_emuos CONTAINS(false||off||no||0)
Else
    If Key_emuos CONTAINS(*)
        Show_Message(Invalid value for key=value pair EMUOS entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_blackbox CONTAINS(true||on||yes||1)
    Add_CLP( -bb)
ElseIf Key_blackbox CONTAINS(false||off||no||0)
Else
    If Key_blackbox CONTAINS(*)
        Show_Message(Invalid value for key=value pair BLACKBOX entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_mio CONTAINS(true||on||yes||1)
    Add_CLP( -mio)
ElseIf Key_mio CONTAINS(false||off||no||0)
Else
    If Key_mio CONTAINS(*)
        Show_Message(Invalid value for key=value pair MIO entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_basic CONTAINS(true||on||yes||1)
    Add_CLP( -basic)
ElseIf Key_basic CONTAINS(false||off||no||0)
    Add_CLP( -nobasic)
Else
    If Key_basic CONTAINS(*)
        Show_Message(Invalid value for key=value pair BASIC entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    Add_CLP( -nobasic)
End If

If Key_siopatch CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||1)
ElseIf Key_siopatch CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||0)
Else
    If Key_siopatch CONTAINS(*)
        Show_Message(Invalid value for key=value pair SIOPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||1)
End If

If Key_hpatch CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||1)
ElseIf Key_hpatch CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||0)
Else
    If Key_hpatch CONTAINS(*)
        Show_Message(Invalid value for key=value pair HPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||0)
End If

If Key_ppatch CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||1)
ElseIf Key_ppatch CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||0)
Else
    If Key_ppatch CONTAINS(*)
        Show_Message(Invalid value for key=value pair PPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||0)
End If

If Key_hreadmode CONTAINS(readonly||ro)
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||1)
ElseIf Key_hreadmode CONTAINS(readwrite||rw)
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||0)
Else
    If Key_hreadmode CONTAINS(*)
        Show_Message(Invalid value for key=value pair HREADMODE entered.%crlfx2%Possible values are:%crlfx2%ro, readonly, rw, readwrite.%crlfx2%Default readonly is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||1)
End If

If Key_axlon CONTAINS(*)
    Add_CLP( -axlon %axlon_value%)
End If

If Key_axlon0f CONTAINS(true||on||yes||1)
    Add_CLP( -axlon0f)
ElseIf Key_axlon0f CONTAINS(false||off||no||0)
Else
    If Key_axlon0f CONTAINS(*)
        Show_Message(Invalid value for key=value pair EXLON0F entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_mosaic CONTAINS(*)
    Add_CLP( -mosaic %mosaic_value%)
End If



;*********************************
; EMULATOR SETTINGS
;*********************************

If Key_rtime CONTAINS(true||on||yes||1)
    Add_CLP( -rtime)
ElseIf Key_rtime CONTAINS(false||off||no||0)
    Add_CLP( -nortime)
Else
    If Key_rtime CONTAINS(*)
        Show_Message(Invalid value for key=value pair RTIME entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    Add_CLP( -nortime)
End If

If Key_rdevice CONTAINS(*)
    Add_CLP( -rdevice %rdevice_value%)
End If

;*********************************
; SOUND SETTINGS
;*********************************

If Key_sound CONTAINS(true||on||yes||1)
    Add_CLP( -sound)
ElseIf Key_sound CONTAINS(false||off||no||0)
    Add_CLP( -nosound)
Else
    If Key_sound CONTAINS(*)
        Show_Message(Invalid value for key=value pair SOUND entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End If
    Add_CLP( -sound)
End If

If Key_wavonly CONTAINS(true||on||yes||1)
    Add_CLP( -wavonly)
ElseIf Key_wavonly CONTAINS(false||off||no||0)
Else
    If Key_wavonly CONTAINS(*)
        Show_Message(Invalid value for key=value pair WAVONLY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_dsprate CONTAINS(*)
    Add_CLP( -dsprate %dsprate_value%)
End If

If Key_snddelay CONTAINS(*)
    Add_CLP( -snddelay %snddelay_value%)
End If

If Key_audio16 CONTAINS(true||on||yes||1)
    Add_CLP( -audio16)
ElseIf Key_audio16 CONTAINS(false||off||no||0)
Else
    If Key_audio16 CONTAINS(*)
        Show_Message(Invalid value for key=value pair AUDIO16 entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_quality CONTAINS(*)
    Add_CLP( -quality %quality_value%)
End If

If Key_newpokey CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||1)
ElseIf Key_newpokey CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||0)
Else
    If Key_newpokey CONTAINS(*)
        Show_Message(Invalid value for key=value pair NEWPOKEY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||1)
End If

If Key_speakersound CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||1)
ElseIf Key_speakersound CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||0)
Else
    If Key_speakersound CONTAINS(*)
        Show_Message(Invalid value for key=value pair SPEAKERSOUND entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||1)
End If

If Key_stereo CONTAINS(true||on||yes||1)
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||1)
ElseIf Key_stereo CONTAINS(false||off||no||0)
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||0)
Else
    If Key_stereo CONTAINS(*)
        Show_Message(Invalid value for key=value pair STEREO entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||0)
End If


;************************************
; VIDEO SETTINGS
;************************************
If PalNTSC = PAL
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||PAL)
ElseIf PalNTSC = NTSC
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||NTSC)
Else
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||PAL)
End If



If Key_refresh CONTAINS(1||2||3||4||5||6||7||8||9||10||11||12||13||14||15||16||17||18||19||20||21||22||23||24||25||26||27||28||29||30||31||32||33||34||35||36||37||38||39||40||41||42||43||44||45||46||47||48||49||50||51||52||53||54||55||56||57||58||59||60||61||62||63||64||65||66||67||68||69||70||71||72||73||74||75||76||77||78||79||80||81||82||83||84||85||86||87||88||89||90||91||92||93||94||95||96||97||98||99)
    Set_CFG_Value(%emupath%\GB800.TXT||SCREEN_REFRESH_RATIO||%refresh_value%)
Else
    If Key_refresh CONTAINS(*)
        Show_Message(Invalid value for key=value pair REFRESH entered.%crlfx2%Possible values are:%crlfx2%1 to 99.%crlfx2%Default 1 is used.)
    End If
    Set_CFG_Value(%emupath%\GB800.TXT||SCREEN_REFRESH_RATIO||1)
End If

If Key_width CONTAINS(*)
    Add_CLP( -width %width_value%)
End If

If Key_height CONTAINS(*)
    Add_CLP( -height %height_value%)
End If

If Key_rotate90 CONTAINS(true||on||yes||1)
    Add_CLP( -rotate90)
ElseIf Key_rotate90 CONTAINS(false||off||no||0)
Else
    If Key_rotate90 CONTAINS(*)
        Show_Message(Invalid value for key=value pair ROTATE90 entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_blt CONTAINS(true||on||yes||1)
    Add_CLP( -blt)
ElseIf Key_blt CONTAINS(false||off||no||0)
Else
    If Key_fullscreen CONTAINS(true||on||yes||1)
        If Key_blt CONTAINS(*)
            Show_Message(Invalid value for key=value pair BLT entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
        End If
        Add_CLP( -blt)
    Else

        If Key_blt CONTAINS(*)
            Show_Message(Invalid value for key=value pair BLT entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End If
    End If
End If

If Key_artif CONTAINS(0||1||2||3||4)
    Add_CLP( -artif %artif_value%)
Else
    If Key_artif CONTAINS(*)
        Show_Message(Invalid value for ARTIF entered.)
    End If
End If

If Key_paletten CONTAINS(*)
    Add_CLP( -paletten %paletten_value%)
End If

If Key_palettep CONTAINS(*)
    Add_CLP( -palettep %palettep_value%)
End If

If Key_blackn CONTAINS(*)
    Add_CLP( -blackn %blackn_value%)
End If

If Key_blackp CONTAINS(*)
    Add_CLP( -blackp %blackp_value%)
End If

If Key_whiten CONTAINS(*)
    Add_CLP( -whiten %whiten_value%)
End If

If Key_whitep CONTAINS(*)
    Add_CLP( -whitep %whitep_value%)
End If

If Key_colorsn CONTAINS(*)
    Add_CLP( -colorsn %colorsn_value%)
End If

If Key_colorsp CONTAINS(*)
    Add_CLP( -colorsp %colorsp_value%)
End If

If Key_genpaln CONTAINS(true||on||yes||1)
    Add_CLP( -genpaln)
ElseIf Key_genpaln CONTAINS(false||off||no||0)
Else
    If Key_genpaln CONTAINS(*)
        Show_Message(Invalid value for key=value pair GENPALN entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_genpalp CONTAINS(true||on||yes||1)
    Add_CLP( -genpalp)
ElseIf Key_genpalp CONTAINS(false||off||no||0)
Else
    If Key_genpalp CONTAINS(*)
        Show_Message(Invalid value for key=value pair GENPALP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_colshiftn CONTAINS(*)
    If Key_genpaln CONTAINS(true||on||yes||1)
        Add_CLP( -colshiftn %colshiftn_value%)
    End If
End If

If Key_colshiftp CONTAINS(*)
    If Key_genpalp CONTAINS(true||on||yes||1)
        Add_CLP( -colshiftp %colshiftp_value%)
    End If
End If

;**********************************
; MISCELLANEOUS SETTINGS
;**********************************

If Key_showversion CONTAINS(true||on||yes||1)
    Add_CLP( -v)
ElseIf Key_showversion CONTAINS(false||off||no||0)
Else
    If Key_showversion CONTAINS(*)
        Show_Message(Invalid value for key=value pair SHOWVERSION entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_devbug CONTAINS(true||on||yes||1)
    Add_CLP( -devbug)
ElseIf Key_devbug CONTAINS(false||off||no||0)
Else
    If Key_devbug CONTAINS(*)
        Show_Message(Invalid value for key=value pair DEVBUG entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_record CONTAINS(*)
    Add_CLP( -record %record_value%)
End If

If Key_playback CONTAINS(*)
    Add_CLP( -playback %playback_value%)
End If

If Key_win32keys CONTAINS(true||on||yes||1)
    Add_CLP( -win32keys)
ElseIf Key_win32keys CONTAINS(false||off||no||0)
Else
    If Key_win32keys CONTAINS(*)
        Show_Message(Invalid value for key=value pair WIN32KEYS entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_screenshots CONTAINS(*)
    Add_CLP( -screenshots %screenshots_value%)
End If

If Key_showspeed CONTAINS(true||on||yes||1)
    Add_CLP( -showspeed)
ElseIf Key_showspeed CONTAINS(false||off||no||0)
Else
    If Key_showspeed CONTAINS(*)
        Show_Message(Invalid value for key=value pair SHOWSPEED entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

;**********************************
; PATH SETTINGS
;**********************************

If Key_osarom CONTAINS(*)
    Add_CLP( -osa_rom %osarom_value%)
End If

If Key_osbrom CONTAINS(*)
    Add_CLP( -osb_rom %osbrom_value%)
End If

If Key_xlxerom CONTAINS(*)
    Add_CLP( -xlxe_rom %xlxerom_value%)
End If

If Key_5200rom CONTAINS(*)
    Add_CLP( -5200_rom %5200rom_value%)
End If

If Key_basicrom CONTAINS(*)
    Add_CLP( -basic_rom %basicrom_value%)
End If

If Key_h1 CONTAINS(*)
    Set_CFG_Value(%emupath%\GB800.TXT||H1_DIR||%h1_value%)
Else
    Set_CFG_Value(%emupath%\GB800.TXT||H1_DIR|| )
End If

If Key_h2 CONTAINS(*)
    Set_CFG_Value(%emupath%\GB800.TXT||H2_DIR||%h2_value%)
Else
    Set_CFG_Value(%emupath%\GB800.TXT||H2_DIR|| )
End If

If Key_h3 CONTAINS(*)
    Set_CFG_Value(%emupath%\GB800.TXT||H3_DIR||%h3_value%)
Else
    Set_CFG_Value(%emupath%\GB800.TXT||H3_DIR|| )
End If

If Key_h4 CONTAINS(*)
    Set_CFG_Value(%emupath%\GB800.TXT||H4_DIR||%h4_value%)
Else
    Set_CFG_Value(%emupath%\GB800.TXT||H4_DIR|| )
End If

If Key_hpath CONTAINS(*)
    Add_CLP( -hpath %hpath_value%)
End If

;****************************************
; INPUT DEVICE SETTINGS
;****************************************

If Key_mouse CONTAINS(off||pad||touch||koala||pen||gun||amiga||st||trak||joy)
    Add_CLP( -mouse %mouse_value%)
Else
    If Key_mouse CONTAINS(*)
        Show_Message(Invalid value for key=value pair MOUSE entered.%crlfx2%Possible values are:%crlfx2%off, pad, touch, koala, pen, gun, amiga, st, trak, joy.%crlfx2%Default off is used.)
    End If
    Add_CLP( -mouse off)
End If

If Key_mouseport CONTAINS(1||2||3||4)
    Add_CLP( -mouseport %mouseport_value%)
Else
    If Key_mouseport CONTAINS(*)
        Show_Message(Invalid value for key=value pair MOUSEPORT entered.%crlfx2%Possible values are:%crlfx2%1, 2, 3, 4.%crlfx2%Default 1 is used.)
    End If
    If Key_mouse CONTAINS(pad||touch||koala||pen||gun||amiga||st||trak||joy)

        Add_CLP( -mouseport 1)
    End If
End If

If Key_mousespeed CONTAINS(1||2||3||4||5||6||7||8||9)
    Add_CLP( -mousespeed %mousespeed_value%)
Else
    If Key_mousespeed CONTAINS(*)
        Show_Message(Invalid value for key=value pair MOUSESPEED entered.%crlfx2%Possible values are:%crlfx2%1, 2, 3, 4, 5, 6, 7, 8, 9.%crlfx2%Default 3 is used.)
    End If
    If Key_mouse CONTAINS(pad||touch||koala||pen||gun||amiga||st||trak||joy)
        Add_CLP( -mousespeed 3)
    End If
End If

If Key_grabmouse CONTAINS(true||on||yes||1)
    Add_CLP( -grabmouse)
ElseIf Key_grabmouse CONTAINS(false||off||no||0)
Else
    If Key_grabmouse CONTAINS(*)
        Show_Message(Invalid value for key=value pair GRABMOUSE entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_directmouse CONTAINS(true||on||yes||1)
    Add_CLP( -directmouse)
ElseIf Key_directmouse CONTAINS(false||off||no||0)
Else
    If Key_directmouse CONTAINS(*)
        Show_Message(Invalid value for key=value pair DIRECTMOUSE entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_cx85 CONTAINS(*)
    Add_CLP( -cx85 %cx85_value%)
End If

If Key_multijoy CONTAINS(true||on||yes||1)
    Add_CLP( -multijoy)
ElseIf Key_multijoy CONTAINS(false||off||no||0)
Else
    If Key_multijoy CONTAINS(*)
        Show_Message(Invalid value for key=value pair MULTIJOY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

If Key_joystick CONTAINS(true||on||yes||1)
ElseIf Key_joystick CONTAINS(false||off||no||0)
    Add_CLP( -nojoystick)
Else
    If Key_joystick CONTAINS(*)
        Show_Message(Invalid value for key=value pair JOYSTICK entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
End If

;----------------------------------------------------
; Show a window with comment or warning message
; if appropriate.
;----------------------------------------------------
If VersionComment CONTAINS(*not 100%*||*not working*||*doesn't work*)
    Show_Message(This game may not work properly.)
End If

If VersionComment CONTAINS(*ATTN:*||*NOTE:*||*ATTN!:*||*NOTE!:*)
    ;point out that critical info is in the version comment
    Show_Message(Read this game's Version Comments for very important information/instructions.)
End If
If Key_message CONTAINS(*)
    Show_Message(%message_value%)
End If

If NumGameFiles > 1
    Show_Message(There is more than one image found for this game.%crlfx2%To mount the next image, press Alt+D in Atari800 and browse to %gbgamepath%.%crlfx2%Look here on in one of its subfolders for supported emulator file types.)
End If

;----------------------------------------------------
;View/edit the Command Line Parameters
;before launching the game
;----------------------------------------------------
If Key_testgame CONTAINS(true||on||yes||1)
    If Key_editclp CONTAINS(true||on||yes||1||false||off||no||0)
    ElseIf Key_editclp CONTAINS(*)
        Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If
    If Key_testclp CONTAINS(true||on||yes||1||false||off||no||0)
    ElseIf Key_testclp CONTAINS(*)
        Show_Message(Invalid value for key=value pair TESTCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If

    Run_Program(%emupath%\GB800.TXT||||nowait)
    Edit_CLP(Game will be started with the following Command Line Parameters)
    If Key_runemu CONTAINS(true||on||yes||1)
        Run_Emulator()
    ElseIf Key_runemu CONTAINS(false||off||no||0)
    Else
        If Key_runemu CONTAINS(*)
            Show_Message(Invalid value for key=value pair RUNEMU entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End If
    End If
Else
    If Key_testgame CONTAINS(false||off||no||0)
    ElseIf Key_testgame CONTAINS(*)
        Show_Message(Invalid value for key=value pair TESTGAME entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End If

    ;----------------------------------------------------
    ;View/edit the Command Line Parameters
    ;before launching the game
    ;----------------------------------------------------
    If Key_testclp CONTAINS(true||on||yes||1)
        Edit_CLP(Game will be started with the following Command Line Parameters)
    ElseIf Key_testclp CONTAINS(false||off||no||0)
        If Key_editclp CONTAINS(true||on||yes||1||false||off||no||0)
        ElseIf Key_editclp CONTAINS(*)
            Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End If
    Else
        If Key_editclp CONTAINS(true||on||yes||1)
            Edit_CLP(Game will be started with the following Command Line Parameters)
        ElseIf Key_editclp CONTAINS(false||off||no||0)
        Else
            If Key_editclp CONTAINS(*)
                Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
            End If
        End If
        If Key_testclp CONTAINS(*)
            Show_Message(Invalid value for key=value pair TESTCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End If
    End If

    ;---------------------------
    ;Run the emulator

    ;---------------------------

End If

If GameType CONTAINS(cas)
    If Key_tape CONTAINS(manual)

        Run_Emulator_Send_Keys([3]run"c:{enter}"[1]||50)
    Else
        Run_Emulator()
    End If

End If
If GameType CONTAINS(atr||xex||bin||rom||com||bas||atx||xfd)
    Run_Emulator()
End If

"""


"""
    if (GameType CONTAINS(cas))
    {
        if i_gemus.fieldIs("basic", "yes"):
        {
            if i_gemus.fieldIs("tape", "manual"):
                args = args.concat("-tape", %gamepathfile%)
            else
                args = args.concat("-boottape", %gamepathfile%)
        }
        else
        {
            args = args.concat("-boottape", "-nobasic", %gamepathfile%)
        }
    }


    if (GameType CONTAINS(bin||rom))
        args = args.concat("-cart", %gamepathfile%)

    if (GameType CONTAINS(atr||xfd))
        args = args.concat(%gamepathfile%)

    if i_gemus.fieldIsOneOf("fullscreen", ["true", "on", "yes", "1"]):
        args = args.concat("-fullscreen")
    elif i_gemus.fieldIsOneOf("fullscreen", ["false", "off", "no", "0"]):
        args = args.concat("-windowed")
    elif i_gemus.get("fullscreen") != "":
        Show_Message(Invalid value for key=value pair FULLSCREEN entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    else
    {
        if (TrueDriveEmu = YES)
            args = args.concat("-fullscreen")
        else
            args = args.concat("-windowed")
    }

    args = args.concat("-config", "GB800.TXT")

    // *****************************
    //  HARDWARE SETTINGS
    // *****************************

    if i_gemus.fieldIsOneOf("model", ["osa", "osb", "xl", "ramboxe"]):
    {
        if i_gemus.fieldIs("model", "osa"):
        {
            Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari OS/A)
        }
        elif i_gemus.fieldIs("model", "osb"):
        {
            Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari OS/B)
        }
        elif i_gemus.fieldIs("model", "xl"):
        {
            Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
        }
        elif i_gemus.fieldIs("model", "ramboxe"):
        {
            Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
            Set_CFG_Value(%emupath%\GB800.TXT||RAM_SIZE||320 (RAMBO))
        }
    }
    else
    {
        if i_gemus.get("model") != "":
        Show_Message(Invalid value for key=value pair MODEL entered.%crlfx2%Possible values are:%crlfx2%osa,osb, xl, ramboxe.%crlfx2%Default xl is used.)

        Set_CFG_Value(%emupath%\GB800.TXT||RAM_SIZE||64)
        Set_CFG_Value(%emupath%\GB800.TXT||MACHINE_TYPE||Atari XL/XE)
    }

    if i_gemus.fieldIsOneOf("emuos", "true||on||yes||1"):
    {
        args = args.concat("-emuos")
    }
    elif i_gemus.fieldIsOneOf("emuos", "false||off||no||0"):
    {
    }
    else
    {
        if i_gemus.get("emuos") != "":
            Show_Message(Invalid value for key=value pair EMUOS entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    }

    // TODO continue here
    if i_gemus.fieldIs("blackbox", "true||on||yes||1"):
        args = args.concat("-bb")
    elif (i_gemus.fieldIs("blackbox", "false||off||no||0"))
else
    if (i_gemus.fieldIs("blackbox", "*"))
        Show_Message(Invalid value for key=value pair BLACKBOX entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("mio", "true||on||yes||1"))
    args = args.concat("-mio")
    elif (i_gemus.fieldIs("mio", "false||off||no||0"))
else
    if (i_gemus.fieldIs("mio", "*"))
        Show_Message(Invalid value for key=value pair MIO entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("basic", "true||on||yes||1"))
    args = args.concat("-basic")
    elif (i_gemus.fieldIs("basic", "false||off||no||0"))
    args = args.concat("-nobasic")
else
    if (i_gemus.fieldIs("basic", "*"))
        Show_Message(Invalid value for key=value pair BASIC entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
    args = args.concat("-nobasic")
End if

    if (i_gemus.fieldIs("siopatch", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||1)
    elif (i_gemus.fieldIs("siopatch", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||0)
else
    if (i_gemus.fieldIs("siopatch", "*"))
        Show_Message(Invalid value for key=value pair SIOPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_SIO_PATCH||1)
End if

    if (i_gemus.fieldIs("hpatch", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||1)
    elif (i_gemus.fieldIs("hpatch", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||0)
else
    if (i_gemus.fieldIs("hpatch", "*"))
        Show_Message(Invalid value for key=value pair HPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_H_PATCH||0)
End if

    if (i_gemus.fieldIs("ppatch", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||1)
    elif (i_gemus.fieldIs("ppatch", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||0)
else
    if (i_gemus.fieldIs("ppatch", "*"))
        Show_Message(Invalid value for key=value pair PPATCH entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_P_PATCH||0)
End if

    if (i_gemus.fieldIs("hreadmode", "readonly||ro"))
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||1)
    elif (i_gemus.fieldIs("hreadmode", "readwrite||rw"))
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||0)
else
    if (i_gemus.fieldIs("hreadmode", "*"))
        Show_Message(Invalid value for key=value pair HREADMODE entered.%crlfx2%Possible values are:%crlfx2%ro, readonly, rw, readwrite.%crlfx2%Default readonly is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||HD_READ_ONLY||1)
End if

    if (i_gemus.fieldIs("axlon", "*"))
    args = args.concat("-axlon" %axlon_value%)
End if

    if (i_gemus.fieldIs("axlon0f", "true||on||yes||1"))
    args = args.concat("-axlon0f")
    elif (i_gemus.fieldIs("axlon0f", "false||off||no||0"))
else
    if (i_gemus.fieldIs("axlon0f", "*"))
        Show_Message(Invalid value for key=value pair EXLON0F entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("mosaic", "*"))
    args = args.concat("-mosaic", %mosaic_value%)
End if



// *********************************
//  EMULATOR SETTINGS
// *********************************

    if (i_gemus.fieldIs("rtime", "true||on||yes||1"))
    args = args.concat("-rtime")
    elif (i_gemus.fieldIs("rtime", "false||off||no||0"))
    args = args.concat("-nortime")
else
    if (i_gemus.fieldIs("rtime", "*"))
        Show_Message(Invalid value for key=value pair RTIME entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
    args = args.concat("-nortime")
End if

    if (i_gemus.fieldIs("rdevice", "*"))
    args = args.concat("-rdevice", %rdevice_value%)
End if

// *********************************
//  SOUND SETTINGS
// *********************************

    if (i_gemus.fieldIs("sound", "true||on||yes||1"))
    args = args.concat("-sound")
    elif (i_gemus.fieldIs("sound", "false||off||no||0"))
    args = args.concat("-nosound")
else
    if (i_gemus.fieldIs("sound", "*"))
        Show_Message(Invalid value for key=value pair SOUND entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End if
    args = args.concat("-sound")
End if

    if (i_gemus.fieldIs("wavonly", "true||on||yes||1"))
    args = args.concat("-wavonly")
    elif (i_gemus.fieldIs("wavonly", "false||off||no||0"))
else
    if (i_gemus.fieldIs("wavonly", "*"))
        Show_Message(Invalid value for key=value pair WAVONLY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("dsprate", "*"))
    args = args.concat("-dsprate", %dsprate_value%)
End if

    if (i_gemus.fieldIs("snddelay", "*"))
    args = args.concat("-snddelay", %snddelay_value%)
End if

    if (i_gemus.fieldIs("audio16", "true||on||yes||1"))
    args = args.concat("-audio16")
    elif (i_gemus.fieldIs("audio16", "false||off||no||0"))
else
    if (i_gemus.fieldIs("audio16", "*"))
        Show_Message(Invalid value for key=value pair AUDIO16 entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("quality", "*"))
    args = args.concat("-quality", %quality_value%)
End if

    if (i_gemus.fieldIs("newpokey", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||1)
    elif (i_gemus.fieldIs("newpokey", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||0)
else
    if (i_gemus.fieldIs("newpokey", "*"))
        Show_Message(Invalid value for key=value pair NEWPOKEY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||ENABLE_NEW_POKEY||1)
End if

    if (i_gemus.fieldIs("speakersound", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||1)
    elif (i_gemus.fieldIs("speakersound", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||0)
else
    if (i_gemus.fieldIs("speakersound", "*"))
        Show_Message(Invalid value for key=value pair SPEAKERSOUND entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||SPEAKER_SOUND||1)
End if

    if (i_gemus.fieldIs("stereo", "true||on||yes||1"))
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||1)
    elif (i_gemus.fieldIs("stereo", "false||off||no||0"))
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||0)
else
    if (i_gemus.fieldIs("stereo", "*"))
        Show_Message(Invalid value for key=value pair STEREO entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||STEREO_POKEY||0)
End if


// ************************************
//  VIDEO SETTINGS
// ************************************
if PalNTSC = PAL
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||PAL)
elif PalNTSC = NTSC
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||NTSC)
else
    Set_CFG_Value(%emupath%\GB800.TXT||DEFAULT_TV_MODE||PAL)
End if



    if (i_gemus.fieldIs("refresh", "1||2||3||4||5||6||7||8||9||10||11||12||13||14||15||16||17||18||19||20||21||22||23||24||25||26||27||28||29||30||31||32||33||34||35||36||37||38||39||40||41||42||43||44||45||46||47||48||49||50||51||52||53||54||55||56||57||58||59||60||61||62||63||64||65||66||67||68||69||70||71||72||73||74||75||76||77||78||79||80||81||82||83||84||85||86||87||88||89||90||91||92||93||94||95||96||97||98||99"))
    Set_CFG_Value(%emupath%\GB800.TXT||SCREEN_REFRESH_RATIO||%refresh_value%)
else
    if (i_gemus.fieldIs("refresh", "*"))
        Show_Message(Invalid value for key=value pair REFRESH entered.%crlfx2%Possible values are:%crlfx2%1 to 99.%crlfx2%Default 1 is used.)
    End if
    Set_CFG_Value(%emupath%\GB800.TXT||SCREEN_REFRESH_RATIO||1)
End if

    if (i_gemus.fieldIs("width", "*"))
    args = args.concat("-width", %width_value%)
End if

    if (i_gemus.fieldIs("height", "*"))
    args = args.concat("-height", %height_value%)
End if

    if (i_gemus.fieldIs("rotate90", "true||on||yes||1"))
    args = args.concat("-rotate90")
    elif (i_gemus.fieldIs("rotate90", "false||off||no||0"))
else
    if (i_gemus.fieldIs("rotate90", "*"))
        Show_Message(Invalid value for key=value pair ROTATE90 entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("blt", "true||on||yes||1"))
    args = args.concat("-blt")
    elif (i_gemus.fieldIs("blt", "false||off||no||0"))
else
    if (i_gemus.fieldIs("fullscreen", "true||on||yes||1"))
        if (i_gemus.fieldIs("blt", "*"))
            Show_Message(Invalid value for key=value pair BLT entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default true is used.)
        End if
        args = args.concat("-blt")
    else

        if (i_gemus.fieldIs("blt", "*"))
            Show_Message(Invalid value for key=value pair BLT entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End if
    End if
End if

    if (i_gemus.fieldIs("artif", "0||1||2||3||4"))
    args = args.concat("-artif", %artif_value%)
else
    if (i_gemus.fieldIs("artif", "*"))
        Show_Message(Invalid value for ARTIF entered.)
    End if
End if

    if (i_gemus.fieldIs("paletten", "*"))
    args = args.concat("-paletten", %paletten_value%)
End if

    if (i_gemus.fieldIs("palettep", "*"))
    args = args.concat("-palettep", %palettep_value%)
End if

    if (i_gemus.fieldIs("blackn", "*"))
    args = args.concat("-blackn", %blackn_value%)
End if

    if (i_gemus.fieldIs("blackp", "*"))
    args = args.concat("-blackp", %blackp_value%)
End if

    if (i_gemus.fieldIs("whiten", "*"))
    args = args.concat("-whiten", %whiten_value%)
End if

    if (i_gemus.fieldIs("whitep", "*"))
    args = args.concat("-whitep", %whitep_value%)
End if

    if (i_gemus.fieldIs("colorsn", "*"))
    args = args.concat("-colorsn", %colorsn_value%)
End if

    if (i_gemus.fieldIs("colorsp", "*"))
    args = args.concat("-colorsp", %colorsp_value%)
End if

    if (i_gemus.fieldIs("genpaln", "true||on||yes||1"))
    args = args.concat("-genpaln")
    elif (i_gemus.fieldIs("genpaln", "false||off||no||0"))
else
    if (i_gemus.fieldIs("genpaln", "*"))
        Show_Message(Invalid value for key=value pair GENPALN entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("genpalp", "true||on||yes||1"))
    args = args.concat("-genpalp")
    elif (i_gemus.fieldIs("genpalp", "false||off||no||0"))
else
    if (i_gemus.fieldIs("genpalp", "*"))
        Show_Message(Invalid value for key=value pair GENPALP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("colshiftn", "*"))
        if (i_gemus.fieldIs("genpaln", "true||on||yes||1"))
        args = args.concat("-colshiftn", %colshiftn_value%)
    End if
End if

    if (i_gemus.fieldIs("colshiftp", "*"))
        if (i_gemus.fieldIs("genpalp", "true||on||yes||1"))
        args = args.concat("-colshiftp", %colshiftp_value%)
    End if
End if

// **********************************
//  MISCELLANEOUS SETTINGS
// **********************************

    if (i_gemus.fieldIs("showversion", "true||on||yes||1"))
    args = args.concat("-v")
    elif (i_gemus.fieldIs("showversion", "false||off||no||0"))
else
    if (i_gemus.fieldIs("showversion", "*"))
        Show_Message(Invalid value for key=value pair SHOWVERSION entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("devbug", "true||on||yes||1"))
    args = args.concat("-devbug")
    elif (i_gemus.fieldIs("devbug", "false||off||no||0"))
else
    if (i_gemus.fieldIs("devbug", "*"))
        Show_Message(Invalid value for key=value pair DEVBUG entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("record", "*"))
    args = args.concat("-record", %record_value%)
End if

    if (i_gemus.fieldIs("playback", "*"))
    args = args.concat("-playback", %playback_value%)
End if

    if (i_gemus.fieldIs("win32keys", "true||on||yes||1"))
    args = args.concat("-win32keys")
    elif (i_gemus.fieldIs("win32keys", "false||off||no||0"))
else
    if (i_gemus.fieldIs("win32keys", "*"))
        Show_Message(Invalid value for key=value pair WIN32KEYS entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("screenshots", "*"))
    args = args.concat("-screenshots", %screenshots_value%)
End if

    if (i_gemus.fieldIs("showspeed", "true||on||yes||1"))
    args = args.concat("-showspeed")
    elif (i_gemus.fieldIs("showspeed", "false||off||no||0"))
else
    if (i_gemus.fieldIs("showspeed", "*"))
        Show_Message(Invalid value for key=value pair SHOWSPEED entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

// **********************************
//  PATH SETTINGS
// **********************************

    if (i_gemus.fieldIs("osarom", "*"))
    args = args.concat("-osa_rom", %osarom_value%)
End if

    if (i_gemus.fieldIs("osbrom", "*"))
    args = args.concat("-osb_rom", %osbrom_value%)
End if

    if (i_gemus.fieldIs("xlxerom", "*"))
    args = args.concat("-xlxe_rom", %xlxerom_value%)
End if

    if (i_gemus.fieldIs("5200rom", "*"))
    args = args.concat("-5200_rom", %5200rom_value%)
End if

    if (i_gemus.fieldIs("basicrom", "*"))
    args = args.concat("-basic_rom", %basicrom_value%)
End if

    if (i_gemus.fieldIs("h1", "*"))
    Set_CFG_Value(%emupath%\GB800.TXT||H1_DIR||%h1_value%)
else
    Set_CFG_Value(%emupath%\GB800.TXT||H1_DIR|| )
End if

    if (i_gemus.fieldIs("h2", "*"))
    Set_CFG_Value(%emupath%\GB800.TXT||H2_DIR||%h2_value%)
else
    Set_CFG_Value(%emupath%\GB800.TXT||H2_DIR|| )
End if

    if (i_gemus.fieldIs("h3", "*"))
    Set_CFG_Value(%emupath%\GB800.TXT||H3_DIR||%h3_value%)
else
    Set_CFG_Value(%emupath%\GB800.TXT||H3_DIR|| )
End if

    if (i_gemus.fieldIs("h4", "*"))
    Set_CFG_Value(%emupath%\GB800.TXT||H4_DIR||%h4_value%)
else
    Set_CFG_Value(%emupath%\GB800.TXT||H4_DIR|| )
End if

    if (i_gemus.fieldIs("hpath", "*"))
    args = args.concat("-hpath", %hpath_value%)
End if

// ****************************************
//  INPUT DEVICE SETTINGS
// ****************************************

    if (i_gemus.fieldIs("mouse", "off||pad||touch||koala||pen||gun||amiga||st||trak||joy"))
    args = args.concat("-mouse", %mouse_value%)
else
    if (i_gemus.fieldIs("mouse", "*"))
        Show_Message(Invalid value for key=value pair MOUSE entered.%crlfx2%Possible values are:%crlfx2%off, pad, touch, koala, pen, gun, amiga, st, trak, joy.%crlfx2%Default off is used.)
    End if
    args = args.concat("-mouse", "off")
End if

    if (i_gemus.fieldIs("mouseport", "1||2||3||4"))
    args = args.concat("-mouseport", %mouseport_value%)
else
    if (i_gemus.fieldIs("mouseport", "*"))
        Show_Message(Invalid value for key=value pair MOUSEPORT entered.%crlfx2%Possible values are:%crlfx2%1, 2, 3, 4.%crlfx2%Default 1 is used.)
    End if
        if (i_gemus.fieldIs("mouse", "pad||touch||koala||pen||gun||amiga||st||trak||joy"))

        args = args.concat("-mouseport", "1")
    End if
End if

    if (i_gemus.fieldIs("mousespeed", "1||2||3||4||5||6||7||8||9"))
    args = args.concat("-mousespeed", %mousespeed_value%)
else
    if (i_gemus.fieldIs("mousespeed", "*"))
        Show_Message(Invalid value for key=value pair MOUSESPEED entered.%crlfx2%Possible values are:%crlfx2%1, 2, 3, 4, 5, 6, 7, 8, 9.%crlfx2%Default 3 is used.)
    End if
        if (i_gemus.fieldIs("mouse", "pad||touch||koala||pen||gun||amiga||st||trak||joy"))
        args = args.concat("-mousespeed", "3")
    End if
End if

    if (i_gemus.fieldIs("grabmouse", "true||on||yes||1"))
    args = args.concat("-grabmouse")
    elif (i_gemus.fieldIs("grabmouse", "false||off||no||0"))
else
    if (i_gemus.fieldIs("grabmouse", "*"))
        Show_Message(Invalid value for key=value pair GRABMOUSE entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("directmouse", "true||on||yes||1"))
    args = args.concat("-directmouse")
    elif (i_gemus.fieldIs("directmouse", "false||off||no||0"))
else
    if (i_gemus.fieldIs("directmouse", "*"))
        Show_Message(Invalid value for key=value pair DIRECTMOUSE entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("cx85", "*"))
    args = args.concat("-cx85", %cx85_value%)
End if

    if (i_gemus.fieldIs("multijoy", "true||on||yes||1"))
    args = args.concat("-multijoy")
    elif (i_gemus.fieldIs("multijoy", "false||off||no||0"))
else
    if (i_gemus.fieldIs("multijoy", "*"))
        Show_Message(Invalid value for key=value pair MULTIJOY entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

    if (i_gemus.fieldIs("joystick", "true||on||yes||1"))
        elif (i_gemus.fieldIs("joystick", "false||off||no||0"))
    args = args.concat("-nojoystick")
else
    if (i_gemus.fieldIs("joystick", "*"))
        Show_Message(Invalid value for key=value pair JOYSTICK entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
End if

// ----------------------------------------------------
//  Show a window with comment or warning message
//  if appropriate.
// ----------------------------------------------------
if VersionComment CONTAINS(*not 100%*||*not working*||*doesn't work*)
    Show_Message(This game may not work properly.)
End if

if VersionComment CONTAINS(*ATTN:*||*NOTE:*||*ATTN!:*||*NOTE!:*)
    // point out that critical info is in the version comment
    Show_Message(Read this game's Version Comments for very important information/instructions.)
End if
    if (i_gemus.fieldIs("message", "*"))
    Show_Message(%message_value%)
End if

if NumGameFiles > 1
    Show_Message(There is more than one image found for this game.%crlfx2%To mount the next image, press Alt+D in Atari800 and browse to %gbgamepath%.%crlfx2%Look here on in one of its subfolders for supported emulator file types.)
End if

// ----------------------------------------------------
// View/edit the Command Line Parameters
// before launching the game
// ----------------------------------------------------
    if (i_gemus.fieldIs("testgame", "true||on||yes||1"))
        if (i_gemus.fieldIs("editclp", "true||on||yes||1||false||off||no||0"))
            elif (i_gemus.fieldIs("editclp", "*"))
        Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if
        if (i_gemus.fieldIs("testclp", "true||on||yes||1||false||off||no||0"))
            elif (i_gemus.fieldIs("testclp", "*"))
        Show_Message(Invalid value for key=value pair TESTCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if

    Run_Program(%emupath%\GB800.TXT||||nowait)
    Edit_CLP(Game will be started with the following Command Line Parameters)
    if (i_gemus.fieldIs("runemu", "true||on||yes||1"))
        Run_Emulator()
    elif (i_gemus.fieldIs("runemu", "false||off||no||0"))
    else
        if (i_gemus.fieldIs("runemu", "*"))
            Show_Message(Invalid value for key=value pair RUNEMU entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End if
    End if
else
    if (i_gemus.fieldIs("testgame", "false||off||no||0"))
        elif (i_gemus.fieldIs("testgame", "*"))
        Show_Message(Invalid value for key=value pair TESTGAME entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
    End if

    // ----------------------------------------------------
    // View/edit the Command Line Parameters
    // before launching the game
    // ----------------------------------------------------
    if (i_gemus.fieldIs("testclp", "true||on||yes||1"))
        Edit_CLP(Game will be started with the following Command Line Parameters)
    elif (i_gemus.fieldIs("testclp", "false||off||no||0"))
    if (i_gemus.fieldIs("editclp", "true||on||yes||1||false||off||no||0"))
        elif (i_gemus.fieldIs("editclp", "*"))
            Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End if
    else
        if (i_gemus.fieldIs("editclp", "true||on||yes||1"))
            Edit_CLP(Game will be started with the following Command Line Parameters)
    elif (i_gemus.fieldIs("editclp", "false||off||no||0"))
        else
            if (i_gemus.fieldIs("editclp", "*"))
                Show_Message(Invalid value for key=value pair EDITCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
            End if
        End if
            if (i_gemus.fieldIs("testclp", "*"))
            Show_Message(Invalid value for key=value pair TESTCLP entered.%crlfx2%Possible values are:%crlfx2%true, false, on, off, yes, no, 1, 0.%crlfx2%Default false is used.)
        End if
    End if

    // ---------------------------
    // Run the emulator

    // ---------------------------

End if

if GameType CONTAINS(cas)
    if (i_gemus.fieldIs("tape", "manual"))

        Run_Emulator_Send_Keys("run@c:{enter}"||600)
    else
        Run_Emulator()
    End if

End if
if GameType CONTAINS(atr||xex||bin||rom||com||bas||atx||xfd)
    Run_Emulator()
End if

`
"""
