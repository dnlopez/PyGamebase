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
config_title = "Commodore C64 (Gamebase64 v18)"
gamebaseBaseDirPath = driveBasePath + "/games/Commodore C64/gamebases/GameBase64_V18/GBC_v18"
config_databaseFilePath = gamebaseBaseDirPath + "/GBC_v18.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_photosBaseDirPath = gamebaseBaseDirPath + "/Photos"
config_musicBaseDirPath = gamebaseBaseDirPath + "/C64Music"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameWithVice(i_gameFilePaths):
    """
    Params:
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["x64sc"]

    # Seperately collect paths of disks, tapes and other
    diskFilePaths = []
    tapeFilePaths = []
    otherFilePaths = []
    for gameFilePath in i_gameFilePaths:
        if utils.stringEndsWith(gameFilePath, ".D64", False) or utils.stringEndsWith(gameFilePath, ".G64", False):
            diskFilePaths.append(gameFilePath)
        elif utils.stringEndsWith(gameFilePath, ".T64", False):
            tapeFilePaths.append(gameFilePath)
        else:
            otherFilePaths.append(gameFilePath)

    # Fill up to 4 drives with disks
    for diskFilePathNo in range(min(len(diskFilePaths), 4)):
        executableAndArgs.append("-" + str(8 + diskFilePathNo))
        executableAndArgs.append(diskFilePaths[diskFilePathNo])

    # If there is more than one disk, make a flip list
    if len(diskFilePaths) > 0:
        with open("/tmp/gamebase/fliplist.vfl", "w") as f:
            f.write("# Vice fliplist file\n\nUNIT 8\n" + "\n".join(diskFilePaths) + "\n")
        executableAndArgs.append("-flipname")
        executableAndArgs.append("/tmp/gamebase/fliplist.vfl")

    # Fill up to 1 tape device with tapes
    if len(tapeFilePaths) > 0:
        executableAndArgs.append("-1")
        executableAndArgs.append(tapeFilePaths[0])

    # Add "-autostart" with first disk or tape file
    if len(diskFilePaths) > 0:
        executableAndArgs.append("-autostart")
        executableAndArgs.append(diskFilePaths[0])
    elif len(tapeFilePaths) > 0:
        executableAndArgs.append("-autostart")
        executableAndArgs.append(tapeFilePaths[0])

    # Get rid of NIB files
    otherFilePaths = [otherFilePath
                      for otherFilePath in otherFilePaths
                      if not utils.stringEndsWith(otherFilePath, ".NIB", False)]

    #
    executableAndArgs += otherFilePaths

    #
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

    #
    runGameWithVice(utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        #
        runGameWithVice(utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)

def runMusic(i_musicPath, i_gameInfo):
    #print('runMusic(' + pprint.pformat(i_musicPath) + ', ' + pprint.pformat(i_gameInfo) + ')')

    utils.openInDefaultApplication(config_musicBaseDirPath + "/" + i_musicPath)
