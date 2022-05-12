# Python std
import os.path
import pprint

# This program
import utils


config_databaseFilePath = "/home/daniel/docs/code/js/gamebase/databases/CoCo.sqlite"
config_screenshotsBaseDirPath = "/mnt/ve/games/Tandy Radio Shack TRS-80 CoCo/gamebase beta/CoCo/Screenshots"
config_extrasBaseDirPath = "/mnt/ve/games/Tandy Radio Shack TRS-80 CoCo/gamebase beta/CoCo/Games/"


def runGameOnMachine(i_gameDescription, i_machineName, i_gameFilePaths):
    """
    Params:
     i_gameDescription:
      Either (str)
      or (None)
     i_machineName:
      (string)
      One of
       "coco"
       "coco2"
       "coco3"
     i_gameFilePaths:
      (array of string)
    """
    executableAndArgs = ["rezmame.py", i_machineName]

    nextFloppyDiskNo = 1
    for gameFilePath in i_gameFilePaths:
        # [".plusd" - or is it ".plusd.prg?"]
        if utils.pathHasExtension(gameFilePath, ".wav") or \
           utils.pathHasExtension(gameFilePath, ".cas"):
            executableAndArgs += ["-cassette", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".ccc") or \
             utils.pathHasExtension(gameFilePath, ".rom"):
            executableAndArgs += ["-cartridge", gameFilePath]

        elif utils.pathHasExtension(gameFilePath, ".dmk") or \
             utils.pathHasExtension(gameFilePath, ".jvc") or \
             utils.pathHasExtension(gameFilePath, ".dsk") or \
             utils.pathHasExtension(gameFilePath, ".vdk") or \
             utils.pathHasExtension(gameFilePath, ".sdf") or \
             utils.pathHasExtension(gameFilePath, ".os9") or \
             utils.pathHasExtension(gameFilePath, ".d77") or \
             utils.pathHasExtension(gameFilePath, ".d88") or \
             utils.pathHasExtension(gameFilePath, ".1dd") or \
             utils.pathHasExtension(gameFilePath, ".dfi") or \
             utils.pathHasExtension(gameFilePath, ".hfe") or \
             utils.pathHasExtension(gameFilePath, ".imd") or \
             utils.pathHasExtension(gameFilePath, ".ipf") or \
             utils.pathHasExtension(gameFilePath, ".mfi") or \
             utils.pathHasExtension(gameFilePath, ".mfm") or \
             utils.pathHasExtension(gameFilePath, ".td0") or \
             utils.pathHasExtension(gameFilePath, ".cqm") or \
             utils.pathHasExtension(gameFilePath, ".cqi"):
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
        "rezmame coco",
        "rezmame coco2",
        "rezmame coco3"
    ])

    if method == "rezmame coco":
        runGameOnMachine(i_gameDescription, "coco", i_gameFilePaths)
    elif method == "rezmame coco2":
        runGameOnMachine(i_gameDescription, "coco2", i_gameFilePaths)
    elif method == "rezmame coco3":
        runGameOnMachine(i_gameDescription, "coco3", i_gameFilePaths)

def runGame(i_zipFilePath, i_zipMemberToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_zipFilePath) + ', ' + pprint.pformat(i_zipMemberToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # Extract zip
    basePath = "/mnt/ve/games/Tandy Radio Shack TRS-80 CoCo/gamebase beta/CoCo/Games/"
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

    extrasBasePath = "/mnt/ve/games/Tandy Radio Shack TRS-80 CoCo/gamebase beta/CoCo/Games/"

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
