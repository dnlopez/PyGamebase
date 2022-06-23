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
config_title = "MSX"
gamebaseBaseDirPath = driveBasePath + "/games/MSX/gamebases/gamebase"
config_databaseFilePath = gamebaseBaseDirPath + "/MSX.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"



# TODO
#  games with Name containing "{ROM}" are actually in Extras/MSX1/ROM or Extras/MSX2/ROM, not in Games/MSX1/ROM or Games/MSX2/ROM


def runGameWithOpenmsx(i_gameFilePaths, i_gemusText):
    """
    Params:
     i_gameFilePaths:
      (list of str)
     i_gemusText:
      (str)
    """
    executableAndArgs = ["openmsx"]

    executableAndArgs.extend(openmsxGemusScript(i_gameFilePaths[0], i_gemusText))

    # Execute
    print(executableAndArgs)
    utils.shellStartTask(executableAndArgs)

def runGameMenu(i_gameFilePaths, i_gemusText=""):
    """
    Params:
     i_gameFilePaths:
      (list of str)
     i_gemusText:
      (str)
    """
    method = utils.popupMenu([
        "openmsx"
    ])

    if method == "openmsx":
        runGameWithOpenmsx(i_gameFilePaths, i_gemusText)

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

    # Don't try and insert more than 2 disks
    gameFiles = gameFiles[:2]

    #
    runGameMenu(utils.joinPaths(tempDirPath, gameFiles), i_gameInfo["Gemus"])

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


def openmsxGemusScript(i_gameFilePath, i_gemusText):
    args = []

    gemus = utils.Gemus(i_gemusText)

    # Made to use same GEMUS as BlueMSX.
    # These associated script files must be available and in the correct folder.
    # or the emulator will not run.
    # **The .XML files also contain the screen resolution and graphic modes.
    #   You will need to edit those files for how you like.

    # %dbpath%\scripts\pressctrl.tcl     - holds CTRL key 6 seconds (MSX1) while booting DISK
    # %dbpath%\scripts\pressctrl-15.tcl  - holds CTRL key 15 seconds (MSX2) while booting DISK
    # %dbpath%\scripts\pressshift.tcl    - holds SHIFT key while booting CART
    # %dbpath%\scripts\auto_on.xml       - Type loading command for TAPE (stored in database).
    # %dbpath%\scripts\auto_off.xml      - Disables auto-load command for custom loader on TAPE.
    # %dbpath%\scripts\settings.xml      - OpenMSX settings (how i like it).
    scriptsDirPath = gamebaseBaseDirPath + "/scripts"

    # If game file is a cartridge
    if utils.pathHasExtension(i_gameFilePath, ".ROM"):
        # + Select machine model {{{

        # Japanese
        #  MSX 1
        if gemus.fieldIs("machine", "msx1jp"):
            args.extend(["-machine", "National_CF-3300"])
        #  MSX 2
        elif gemus.fieldIs("machine", "msx2jp"):
            args.extend(["-machine", "Philips_NMS_8245"])
        #  turboR
        elif gemus.fieldIsOneOf("machine", ["turbor", "turbor7", "turbor21"]):
            args.extend(["-machine", "Panasonic_FS-A1GT"])

        # Korean
        #  MSX 1
        elif gemus.fieldIs("machine", "msx1ko"):
            args.extend(["-machine", "Goldstar_FC-80U"])

        # Arabic
        #  MSX 1
        elif gemus.fieldIs("machine", "msx1ar"):
            args.extend(["-machine", "Al_Alamiah_AX170"])
        #  MSX 2
        elif gemus.fieldIs("machine", "msx2ar"):
            args.extend(["-machine", "Yamaha_AX350IIF"])

        # Spanish
        #  MSX 2
        elif gemus.fieldIs("machine", "msx2sp"):
            args.extend(["-machine", "Philips_NMS_8245"])

        # Dooly
        elif gemus.fieldIs("machine", "cbiosmsx1"):
            args.extend(["-machine", "C-BIOS_MSX1"])

        # Else default to European
        #  MSX 1
        else:
            args.extend(["-machine", "Philips_VG_8020"])

        # + }}}

        # Add SCC cart to slot 2
        if gemus.fieldIs("romtype2", "scc"):
            args.extend(["-exta", "scc"])

        # Press SHIFT during boot
        if gemus.fieldIs("startup", "shift"):
            args.extend(["-script", scriptsDirPath + "/pressshift.tcl"])

        # Dual boot carts - R-Type Boot Menu
        if gemus.fieldIs("rom", "boot"):
            args.extend(["-cart", node_path.dirname(i_gameFilePath) + "/" + gemus.properties["boot"], "-cartb", i_gameFilePath])
        else:
            args.extend(["-cart", i_gameFilePath])

        # Select mapper for any unknown/new roms, using BlueMSX mapper number.
        # Most roms will run automatically without any need for this setting.
        # 3: KonamiSCC
        if gemus.fieldIs("mapper", "3"):
            args.extend(["-romtype", "konamiscc"])
        # 4: Konami
        elif gemus.fieldIs("mapper", "4"):
            args.extend(["-romtype", "konami"])
        # 5: ASCII8
        elif gemus.fieldIs("mapper", "5"):
            args.extend(["-romtype", "ascii18"])
        # 6: ASCII16
        elif gemus.fieldIs("mapper", "6"):
            args.extend(["-romtype", "ascii16"])
        # 17: GenericKonami
        elif gemus.fieldIs("mapper", "17"):
            args.extend(["-romtype", "generickonami"])
        # 39: BASICx8000
        elif gemus.fieldIs("mapper", "39"):
            args.extend(["-romtype", "0x8000"])
        # 42: Normalx4000
        elif gemus.fieldIs("mapper", "42"):
            args.extend(["-romtype", "0x4000"])
        # 55: SCC Generic
        elif gemus.fieldIs("mapper", "55"):
            args.extend(["-romtype", "scc"])

        # Add custom settings for GFX mode
        #args.extend(["-setting", scriptsDirPath + "/settings.xml"])

    # If game file is a floppy disk
    if utils.pathHasExtension(i_gameFilePath, ".DSK"):
        # [old comment
        #  AVT_DPF-550
        #  Panasonic_FS-FD1A
        #  Philips_VY-0010_3.5 inch_Disk_Drive
        #  Sanyo_MFD-001
        #  Sharp_HB-3600
        #  Sony_HBD-F1_2DD]

        # + Select machine model {{{

        # Add a floppy drive extension for MSX1; not required for MSX2.

        # European
        #  MSX1
        if gemus.fieldIs("machine", "msx1uk"):
            args.extend(["-machine", "Toshiba_HX-10", "-ext", "Panasonic_FS-FD1A"])
        #  MSX2
        elif gemus.fieldIs("machine", "msx2uk"):
            args.extend(["-machine", "Philips_NMS_8245"])
        #  MSX2 Sony HB-F700D/P
        #  for Vaxol Disk / Mortadelo y Filemon (DSK)
        elif gemus.fieldIs("machine", "HBF700D"):
            args.extend(["-machine", "Sony_HB-F700D"])

        # Arabic
        #  MSX1
        elif gemus.fieldIs("machine", "msx1ar"):
            args.extend(["-machine", "Al_Alamiah_AX170", "-ext", "Panasonic_FS-FD1A"])
        #  MSX2
        elif gemus.fieldIs("machine", "msx2ar"):
            args.extend(["-machine", "Yamaha_AX350IIF"])

        # Korean
        #  MSX1
        elif gemus.fieldIs("machine", "msx1ko"):
            args.extend(["-machine", "Goldstar_FC-80U", "-ext", "Panasonic_FS-FD1A"])

        # Japanese
        #  MSX1
        elif gemus.fieldIs("machine", "msx1jp"):
            args.extend(["-machine", "National_FS-1300", "-ext", "Panasonic_FS-FD1A"])
        #  MSX2
        elif gemus.fieldIs("machine", "msx2jp"):
            # Machine has 256k RAM as default - Metal Gear 2 disk needs 512k for SCC sound to work.
            args.extend(["-machine", "National_FS-5000F2"])
        #  MSX2 2MB
        #  mainly for hacked carts on disk
        elif gemus.fieldIs("machine", "msx2jp2mb"):
            args.extend(["-machine", "National_FS-5000F2", "-ext", "ram2mb"])
        #  turboR
        elif gemus.fieldIs("machine", "turbor"):
            args.extend(["-machine", "Panasonic_FS-A1GT"])

        # Spanish
        #  MSX1
        elif gemus.fieldIs("machine", "msx1sp"):
            args.extend(["-machine", "Talent_DPC-200", "-ext", "Philips_NMS_1200"])
        #  MSX2
        elif gemus.fieldIs("machine", "msx2sp"):
            args.extend(["-machine", "Mitsubishi_ML-G3_ES"])
        #  MSX2 2MB
        elif gemus.fieldIs("machine", "msx2sp2mb"):
            args.extend(["-machine", "Mitsubishi_ML-G3_ES", "-ext", "ram2mb"])
        #  Same as Spanish machine above for Alien2 Rom2Disk
        elif gemus.fieldIs("machine", "MSX2-MLG3"):
            args.extend(["-machine", "Mitsubishi_ML-G3_ES"])

        # Brazilian
        elif gemus.fieldIs("machine", "msx1br"):
            args.extend(["-machine", "Gradiente_Expert_GPC-1", "-ext", "Panasonic_FS-FD1A"])

        # Custom machines
        #  ICE (Magi-cracks Disk version)
        elif gemus.fieldIsOneOf("machine", ["ice", "jvc"]):
            args.extend(["-machine", "JVC_HC-7GB", "-ext", "Mitsubishi_ML-30DC_ML-30FD"])
        #  Breakout!
        elif gemus.fieldIs("machine", "toshiba"):
            args.extend(["-machine", "Toshiba_HX-10D", "-ext", "Sharp_HB-3600"])
        #  Mortadelo y Filemon (DSK)
        elif gemus.fieldIs("machine", "Sony_HB-F1II"):
            args.extend(["-machine", "Sony_HB-F1II", "-ext", "Sony_HBD-F1"])

        # + }}}

        # Insert the disk image
        args.extend(["-diska", i_gameFilePath])

        # Custom extensions
        # "METAL GEAR 2 - SOLID SNAKE"

        # Add SCC cart to slot 1
        if gemus.fieldIs("romtype", "scc"):
            args.extend(["-ext", "scc"])
        # Add SCC cart to slot 2
        elif gemus.fieldIs("romtype2", "scc"):
            args.extend(["-extb", "scc"])

        # Add memory expansion (for MSX2 machine only)
        if gemus.fieldIsOneOf("ram", ["512k", "1mb", "2mb", "4mb"]):
            args.extend(["-ext", "ram" + gemus.properties["ram"]])

        # Press CTRL during boot
        if gemus.fieldIs("startup", "control"):
            if gemus.fieldContains("machine", "msx2"):
                args.extend(["-script", scriptsDirPath + "/pressctrl-15.tcl"])
            else:
                args.extend(["-script", scriptsDirPath + "/pressctrl.tcl"])

        # Set GFX9000 extension for Battle Bomber [f6] to swap gfx mode.
        if gemus.fieldIs("video", "gfx9000"):
            args.extend(["-ext", "gfx9000", "-extb", "moonsound"])

        # Load Emulator with GAMEBASE SETTINGS.
        #  Game folder, GFX MODE, Key Bindings.
        args.extend(["-setting", scriptsDirPath + "/settings.xml"])

    # If game file is a cassette tape
    if utils.pathHasExtension(i_gameFilePath, ".CAS"):
        # ---------------------------------------------------------------
        # Attach gamefile to cassette player - no floppy drive extension.
        # OpenMSX uses a more compatible, slow tape loader.
        # Unlike BlueMSX, it will load Winter Games side A.
        # You can still speedup the loading process by pressing [F9].
        # ---------------------------------------------------------------

        # + Select machine model {{{

        # UK
        #  MSX 1
        if gemus.fieldIsOneOf("machine", ["casuk", "msx1uk"]):
            args.extend(["-machine", "Toshiba_HX-10"])

        # Japanese
        #  MSX 1
        elif gemus.fieldIsOneOf("machine", ["casjap", "msx1jp"]):
            args.extend(["-machine", "Toshiba_HX-22"])
        #  MSX 2
        elif gemus.fieldIsOneOf("machine", ["casmsx2jap", "msx2jp"]):
            args.extend(["-machine", "Sanyo_MPC-25FD"])

        # Spanish
        #  MSX 1
        elif gemus.fieldIsOneOf("machine", ["casspan", "msx1sp"]):
            args.extend(["-machine", "Talent_DPC-200"])

        # Else default to Brazilian
        #  MSX 1
        else:
            args.extend(["-machine", "Gradiente_Expert_GPC-1"])

        # + }}}

        # Insert the cassette image
        args.extend(["-cassetteplayer", i_gameFilePath])

        # Custom cassette settings (pss)
        #  Use setting with Autorun OFF
        if gemus.fieldIsOneOf("cas", ["pss", "off"]):
            args.extend(["-setting", scriptsDirPath + "/auto_off.xml"])

            # type custom load command after emulator boot.
            #Run_Emulator_Send_Keys([6]%sendkeys_value%{enter}||50)
        else:
            args.extend(["-setting", scriptsDirPath + "/auto_on.xml"])

    #
    return args
