# Python std
import os.path
import shutil
import pprint

# This program
import utils


config_title = "Commodore C64 (Gamebase64 v18)"
gamebaseBaseDirPath = "/mnt/gear/games/Commodore C64/gamebases/GameBase64_V18/GBC_v18"
config_databaseFilePath = gamebaseBaseDirPath + "/GBC_v18.sqlite"
config_screenshotsBaseDirPath = gamebaseBaseDirPath + "/Screenshots"
config_extrasBaseDirPath = gamebaseBaseDirPath + "/Extras"


def runGameInVice(i_gameDescription, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_gameFilePaths:
      (list of str)
    """
    executableAndArgs = ["rezvice_x64.py"]

    executableAndArgs += ["--region", "pal"]

    #
    if i_gameDescription != None:
        executableAndArgs += ["--game-description", i_gameDescription]

    executableAndArgs += ["--"]

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
    utils.shellExecList(executableAndArgs)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    basePath = gamebaseBaseDirPath + "/Games/"
    tempDirPath = "/tmp/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_zipFilePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(basePath + i_zipFilePath, tempDirPath)
        # Filter non-game files out of zip member list
        gameFiles = [zipMember
                     for zipMember in zipMembers
                     if not (utils.pathHasExtension(zipMember, ".TXT") or utils.pathHasExtension(zipMember, ".NFO") or utils.pathHasExtension(zipMember, ".SCR") or utils.pathHasExtension(zipMember, ".NIB"))]
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(basePath + i_zipFilePath, tempDirPath + "/" + os.path.basename(i_zipFilePath))
        gameFiles = [os.path.basename(i_zipFilePath)]

    #
    if i_zipMemberToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_zipMemberToRun)

    # Get game description
    gameDescription = i_gameInfo["name"]
    if i_gameInfo["publisher"]:
        gameDescription += " (" + i_gameInfo["publisher"] + ")"

    #
    runGameInVice(gameDescription, utils.joinPaths(tempDirPath, gameFiles))

def runExtra(i_path, i_gameInfo = None):
    #print('runExtra(' + pprint.pformat(i_path) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_path, ".ZIP"):
        # Extract it
        tempDirPath = "/tmp/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + i_path, tempDirPath)

        # Get game description
        gameDescription = i_gameInfo["name"]
        if i_gameInfo["publisher"]:
            gameDescription += " (" + i_gameInfo["publisher"] + ")"

        #
        runGameInVice(gameDescription, utils.joinPaths(tempDirPath, zipMembers))
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_path)
