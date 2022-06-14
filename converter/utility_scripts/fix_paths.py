#!/usr/bin/env python3

# Given a GameBase database (in SQLite format),
# for all paths to external files recorded within it, specifically those to games, screenshots, music, photos and extras,
# check for the existence of the file on disk with case-insensitive path comparison (even though the file system may be case-sensitive),
# and if found on disk with differing case to the path in the database,
# update the path in the database to match that which exists on disk.
# It will also change all backslashes found in paths to forward slashes.


# Python
import os
import os.path
import sys


def printAndFlush(i_str):
    print(i_str)
    sys.stdout.flush()

#var testRelativeTo = null;
#var testPath = "/mnt/Ve/games/Sinclair ZX Spectrum/Speccymania/SpeccyMania/Screenshots/L/labyrinth(Sinclair).gif";
#var testRelativeTo = "/mnt/ve/games/Commodore Amiga/GameBaseAmiga/Screenshots";
#var testPath = "A/'Allo_'Allo!_Cartoon_Fun!.png";
#var testRelativeTo = "/mnt/ve/games/Commodore Amiga/GameBaseAmiga/Screenshots";
#var testPath = "0\17_+_4.png";
#console.log("test result: " + fixPathCase(testPath, testRelativeTo));

def fixPathCase(i_path, i_relativeTo):
    """
    Correct the case of a path by comparing it to actually existing directory entries in the local filesystem.

    Params:
     i_path:
      (str)
      May be absolute or relative.
      Components must be separated by forward slashes.
     i_relativeTo:
      Either (str)
       If i_path is relative, treat it as relative to this directory.
       If i_path is absolute, this is not used.
      or (None)
       Use default of "."

    Returns:
     If a single filesystem object exists with the given path under case-insensitive comparison,
      (str)
      The value of i_path, with case changed to how it is on the filesystem
     Else if no filesystem object exists with the given path under case-insensitive comparison,
      Throw (RuntimeError) with message "No matches"
     Else if multiple filesystem objects exist with the given path under case-insensitive comparison,
      Throw (RuntimeError) with message "Multiple insensitive matches"
    """
    # Apply default arguments
    if i_relativeTo == None:
        i_relativeTo = "."

    #
    components = i_path.split("/")

    # If the first path component is empty, it's an absolute path,
    # so don't use any relative prefix, to start the filesystem browsing and result path at root ("/")
    if components[0] == "":
        relativeBase = ""
    # Else if the first path component isn't empty, it's a relative path,
    # so use the selected relative-to directory as the relative prefix
    else:
        relativeBase = i_relativeTo
        if relativeBase != "" and relativeBase[-1] != "/":
            relativeBase += "/"

    #
    currentSearchPath = ""
    while len(components) > 0:
        # Get next component from the input path
        component = components.pop(0)
        if component == "":
            # Do nothing
            pass
        else:
            # Get the directory entries from the filesystem
            # and if the input component exists in the filesystem with the correct case,
            # just append it to the result and continue
            dirEntries = os.listdir(relativeBase + currentSearchPath)
            if component in dirEntries:
                #printAndFlush("ok: " + component)
                currentSearchPath += component
            # Else if the input component isn't found in the file system,
            # look for a match (or matches) by case-insensitive comparison
            else:
                upperCasedComponent = component.upper()

                insensitiveMatchCount = 0
                firstMatchingDirEntry = None

                for dirEntry in dirEntries:
                    if dirEntry.upper() == upperCasedComponent:
                        #printAndFlush("insensitively ok: " + component + " (-> " + dirEntries[dirEntryNo] + ")")

                        # If found more than one match, throw
                        if insensitiveMatchCount > 0:
                            raise RuntimeError("Multiple insensitive matches")
                        insensitiveMatchCount += 1
                        firstMatchingDirEntry = dirEntry

                # If found no matches, throw
                if insensitiveMatchCount == 0:
                    raise RuntimeError("No matches")

                #
                currentSearchPath += firstMatchingDirEntry

        #
        if len(components) > 0:
            currentSearchPath += "/"

    return currentSearchPath


# + Module imports {{{

# sqlite
import sqlite3

# + }}}

# + Database {{{

g_db = None

def openDb(i_databasePath):
    """
    Params:
     i_databasePath:
      (str)
    """
    global g_db
    g_db = sqlite3.connect(i_databasePath)

def closeDb():
    global g_db
    g_db.close()
    g_db = None

def fixFilename(i_basePath, i_filename):
    """
    Params:
     i_basePath:
      (str)
     i_filename:
      (str)

    Returns:
     (list)
     Array has elements:
      0:
       (str)
       i_filename, possibly with its case corrected.
      1:
       (str)
    """
    fixedFilename = i_filename

    # Replace backslashes with forward slashes
    fixedFilename = fixedFilename.replace("\\", "/")

    #
    errorDescription = ""
    try:
        fixedFilename = fixPathCase(fixedFilename, i_basePath)
    except RuntimeError as e:
        if e.args[0] == "No matches":
            stem, extension = os.path.splitext(fixedFilename)
            filenameWithExtraUnderscore = stem + "_" + extension
            #printAndFlush("trying: " + filenameWithExtraUnderscore)
            if os.path.exists(i_basePath + os.path.sep + filenameWithExtraUnderscore):
                #printAndFlush("found with underscore!")
                fixedFilename = filenameWithExtraUnderscore
            else:
                return [fixedFilename, "Not found"]
        else:
            return [fixedFilename, "Not found, " + e.args]

    #
    if fixedFilename == i_filename:
        return [fixedFilename, "Found, no change"]

    #
    return [fixedFilename, "Found, changed"]

def fixFilenames(i_basePathForGames, i_basePathForScreenshots, i_basePathForSids, i_basePathForPhotos, i_basePathForExtras, i_verbose, i_dryRun):
    """
    Params:
     i_basePathForGames:
      Either (str)
       Base path for values in Games.Filename
      or (None)
       Don't try and correct this field
     i_basePathForScreenshots:
      Either (str)
       Base path for values in Games.ScrnshotFilename
      or (None)
       Don't try and correct this field
     i_basePathForSids:
      Either (str)
       Base path for values in Games.SidFilename
      or (None)
       Don't try and correct this field
     i_basePathForPhotos:
      Either (str)
       Base path for values in Musicians.Photo
      or (None)
       Don't try and correct this field
     i_basePathForExtras:
      Either (str)
       Base path for values in Extras.Path
      or (None)
       Don't try and correct this field
     i_verbose:
      (bool)
      True: Print details of progress.
     i_dryRun:
      (bool)
      False: Don't make any actual changes, only print the SQL that would normally be executed.

    Returns:
     (Promise)
     Resolved when the operation is complete.
    """
    combinedSql = ""

    combinedSql += "BEGIN TRANSACTION;\n"

    def fixFilenameAndUpdateDb(i_columnNames, i_row, i_tableName, i_tableKeyFieldName, i_filenameFieldName, i_basePath):
        """
        Returns:
         (str)
         SQL UPDATE statement, if needed, else "".
        """
        # If this database row doesn't list a filename,
        # bail because there's nothing we can fix
        if i_row[i_columnNames.index(i_filenameFieldName)] == None:
            return ""

        #
        fixedFilename, errorDescription = fixFilename(i_basePath, i_row[i_columnNames.index(i_filenameFieldName)])
        if errorDescription[0:9] == "Not found":
            printAndFlush(errorDescription + ", for file: " + i_row[i_columnNames.index(i_filenameFieldName)])

        if (fixedFilename == i_row[i_columnNames.index(i_filenameFieldName)]):
            return ""

        #printAndFlush("changing to: " + fixedFilename)
        return "UPDATE " + i_tableName + " SET " + i_filenameFieldName + " = '" + fixedFilename.replace("'", "''") + "' WHERE " + i_tableKeyFieldName + " = " + str(i_row[i_columnNames.index(i_tableKeyFieldName)]) + ';\n'

    # Fix fields Games.Filename, Games.ScrnshotFilename and Games.SidFilename
    if i_basePathForGames != None or i_basePathForScreenshots != None or i_basePathForSids != None:
        if i_verbose:
            printAndFlush("Reading table 'Games'")
        cursor = g_db.execute("SELECT * FROM Games")
        columnNames = [column[0]  for column in cursor.description]
        rows = cursor.fetchall()

        if i_basePathForGames != None:
            if i_verbose:
                printAndFlush("Fixing up field 'Games.Filename'")
            for rowNo, row in enumerate(rows):
                combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "Filename", i_basePathForGames)
                if i_verbose and rowNo % 100 == 0:
                    printAndFlush("Done " + str(rowNo) + "/" + str(len(rows)) + "...")

        if i_basePathForScreenshots != None:
            if i_verbose:
                printAndFlush("Fixing up field 'Games.ScrnshotFilename'")
            for rowNo, row in enumerate(rows):
                combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "ScrnshotFilename", i_basePathForScreenshots)
                if i_verbose and rowNo % 100 == 0:
                    printAndFlush("Done " + str(rowNo) + "/" + str(len(rows)) + "...")

        if i_basePathForSids != None:
            if i_verbose:
                printAndFlush("Fixing up field 'Games.SidFilename'")
            for rowNo, row in enumerate(rows):
                combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "SidFilename", i_basePathForSids)
                if i_verbose and rowNo % 100 == 0:
                    printAndFlush("Done " + str(rowNo) + "/" + str(len(rows)) + "...")

    # Fix field Musicians.Photo
    if i_basePathForPhotos != None:
        if i_verbose:
            printAndFlush("Reading table 'Musicians'")
        cursor = g_db.execute("SELECT * FROM Musicians")
        columnNames = [column[0]  for column in cursor.description]
        rows = cursor.fetchall()

        if i_verbose:
            printAndFlush("Fixing up field 'Musicians.Photo'")
        for rowNo, row in enumerate(rows):
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Musicians", "MU_Id", "Photo", i_basePathForPhotos)
            if i_verbose and rowNo % 100 == 0:
                printAndFlush("Done " + str(rowNo) + "/" + str(len(rows)) + "...")

    # Fix field Extras.Path
    if i_basePathForExtras != None:
        if i_verbose:
            printAndFlush("Reading table 'Extras'")
        cursor = g_db.execute("SELECT * FROM Extras")
        columnNames = [column[0]  for column in cursor.description]
        rows = cursor.fetchall()

        if i_verbose:
            printAndFlush("Fixing up field 'Extras.Path'")
        for rowNo, row in enumerate(rows):
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Extras", "EX_Id", "Path", i_basePathForExtras)
            if i_verbose and rowNo % 100 == 0:
                printAndFlush("Done " + str(rowNo) + "/" + str(len(rows)) + "...")

    #
    combinedSql += "COMMIT TRANSACTION;";

    #
    if i_verbose:
        printAndFlush("SQL to be executed: ---")
        printAndFlush(combinedSql)
        printAndFlush("---")

    # Execute
    if not i_dryRun:
        if i_verbose:
            printAndFlush("Executing SQL...")
        g_db.executescript(combinedSql)

#openDb(g_config.databasePath);

#openDb("databases/SpeccyMania.sqlite");
#var basePathForScreenshots = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania/SpeccyMania/Screenshots";

#openDb("databases/SpeccyMania_v4.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v4/zx_up_dax_PL/ZX Spectrum";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/MSX.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/MSX/gamebase";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras");

#openDb("/mnt/gear/games/Atari 800/Gamebase Atari 800XL (v9 DAX)/Atari 800XL/Atari 800XL.sqlite");
#var gamebaseRootDirPath = "/mnt/gear/games/Atari 800/Gamebase Atari 800XL (v9 DAX)/Atari 800XL";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/GameBase Amiga 2.0.sqlite");
#openDb("databases/GameBase Amiga 2.1.sqlite");
#openDb("databases/GameBase Amiga 2.1_new.sqlite");
#openDb("databases/Amiga 2.3.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Commodore Amiga/gamebase_new/Gamebase Amiga 2.3";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/Amstrad CPC.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Amstrad CPC/[CPC]AmstradMania_v7_upload_by_DAX_0714/Amstrad CPC";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/gameboy.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Nintendo GameBoy/gamebase-Archive-d8e2";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/music",
#             null);

#openDb("databases/Commodore Plus4.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Commodore Plus 4/Commodore Plus4_up_dax_Poland/Commodore Plus4";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/music",
#             null);

#openDb("databases/Vic20_v03.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Commodore VIC-20/Gamebase20_v03";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/CBM_PET.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Commodore PET/Gamebase_PET";
#fixFilenames(gamebaseRootDirPath + "/FILES",
#             gamebaseRootDirPath + "/Screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/CoCo.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Tandy Radio Shack TRS-80 CoCo/gamebase beta/CoCo";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             null,
#             gamebaseRootDirPath + "/Games");

#openDb("databases/SpeccyMania_v5.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Sinclair ZX Spectrum/Speccymania v5/Sinclair ZX Spectrum";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/GBC_v16.sqlite");
#var gamebaseRootDirPath = "/mnt/gear/games/Commodore C64/GameBase64_V16/GBC_v16";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/C64Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/Atari 800 v12.sqlite");
#var gamebaseRootDirPath = "/mnt/gear/games/Atari 800/Atari 800 v12";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/Amstrad CPC_v33.sqlite");
#var gamebaseRootDirPath = "/mnt/gear/games/Amstrad CPC/Amstrad CPC";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Pictures",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("databases/ColecoVision.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Coleco Colecovision/Gamebase";
#fixFilenames(gamebaseRootDirPath + "/Roms",
#             gamebaseRootDirPath + "/Screens",
#             null,
#             gamebaseRootDirPath + "/Extras");

#openDb("/mnt/ve/games/Dragon/gamebase/extracted/Dragon.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Dragon/gamebase/extracted";
#fixFilenames(gamebaseRootDirPath + "/games",
#             gamebaseRootDirPath + "/screen",
#             null,
#             gamebaseRootDirPath + "/extras");

#openDb("/mnt/ve/games/Atari ST/Gamebase ST v4/Atari ST/Atari ST.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Atari ST/Gamebase ST v4/Atari ST";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             gamebaseRootDirPath + "/Music",
#             gamebaseRootDirPath + "/Extras");

#openDb("/mnt/ve/games/Tatung Einstein/gamebase/Tatung Einstein/Tatung Einstein.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Tatung Einstein/gamebase/Tatung Einstein";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras").then(endScript);

#openDb("/mnt/ve/games/Epoch Super Cassette Vision/Epoch SCV/Epoch SCV.sqlite");
#var gamebaseRootDirPath = "/mnt/ve/games/Epoch Super Cassette Vision/Epoch SCV";
#fixFilenames(gamebaseRootDirPath + "/Games",
#             gamebaseRootDirPath + "/Screenshots",
#             null,
#             gamebaseRootDirPath + "/Extras");

# + }}}



if __name__ == "__main__":
    # + Parse command line {{{

    COMMAND_NAME = "fix_paths.py"

    def printUsage(i_outputStream):
        i_outputStream.write('''\
''' + COMMAND_NAME + ''', by Daniel Lopez, 03/05/2022
GameBase fix paths utility.

Given a GameBase database (in SQLite format),
for all paths to external files recorded within it, specifically those to games, screenshots, music, photos and extras,
check for the existence of the file on disk with case-insensitive path comparison (even though the file system may be case-sensitive),
and if found on disk with differing case to the path in the database,
update the path in the database to match that which exists on disk.
Also, change all backslashes found in paths to forward slashes.

Usage:
======
''' + COMMAND_NAME + ''' <database file> [options]

Params:
 database file:
  SQLite database file, to be modified.

Options:
 File locations:
  -g/--games <folder path>
    Base folder that contains game files.
  -s/--screenshots <folder path>
    Base folder that contains screenshot files.
  -m/--music <folder path>
    Base folder that contains music files.
  -p/--photos <folder path>
    Base folder that contains photo files.
  -e/--extras <folder path>
    Base folder that contains extras files.

 Info:
  -h/--help
    Show this help.
  -v/--verbose
    Show details of progress.
  -d/--dry-run
    Don't make any actual changes, only print the SQL that would normally be executed.
''')

    # Parameters, with their default values
    databaseFilePath = None
    gamesFilePath = None
    screenshotsFilePath = None
    musicFilePath = None
    photosFilePath = None
    extrasFilePath = None
    verbose = False
    dryRun = False

    # For each argument
    import sys
    argNo = 1
    while argNo < len(sys.argv):
        arg = sys.argv[argNo]
        argNo += 1

        # If it's an option
        if arg[0] == "-":
            if arg == "-g" or arg == "--games":
                if argNo >= len(sys.argv):
                    printAndFlush("ERROR: -g/--games requires a value.")
                    sys.exit(-1)
                gamesFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-s" or arg == "--screenshots":
                if argNo >= len(sys.argv):
                    printAndFlush("ERROR: -s/--screenshots requires a value.")
                    sys.exit(-1)
                screenshotsFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-m" or arg == "--music":
                if argNo >= len(sys.argv):
                    printAndFlush("ERROR: -m/--music requires a value.")
                    sys.exit(-1)
                musicFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-p" or arg == "--photos":
                if argNo >= len(sys.argv):
                    printAndFlush("ERROR: -m/--photos requires a value.")
                    sys.exit(-1)
                photosFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-e" or arg == "--extras":
                if argNo >= len(sys.argv):
                    printAndFlush("ERROR: -e/--extras requires a value.")
                    sys.exit(-1)
                extrasFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-v" or arg == "--verbose":
                verbose = True

            elif arg == "-d" or arg == "--dry-run":
                dryRun = True

            elif arg == "-h" or arg == "--help":
                printUsage(sys.stdout)
                sys.exit(0)

            else:
                printAndFlush("ERROR: Unrecognised option: " + arg)
                printAndFlush("(Run with --help to show command usage.)")
                sys.exit(-1)

        # Else if it's an argument
        else:
            if databaseFilePath == None:
                databaseFilePath = arg
            elif param_sqliteFilePath == None:
                param_sqliteFilePath = arg
            else:
                printAndFlush("ERROR: Too many arguments.")
                printAndFlush("(Run with --help to show command usage.)")
                sys.exit(-1)

    if databaseFilePath == None:
        printAndFlush("ERROR: Insufficient arguments.")
        printAndFlush("(Run with --help to show command usage.)")
        sys.exit(-1)

    # + }}}



    #    # Convert "--long_opt=value" to "--long_opt value"
    #    if (arg[1] == "-")
    #    {
    #        var equalsPos = arg.indexOf("=")
    #        if (equalsPos != -1)
    #        {
    #            process.argv.splice(argNo, 1, arg.substr(0, equalsPos), arg.substr(equalsPos + 1))
    #            arg = arg.substr(0, equalsPos)
    #        }
    #    }

    # Strip slashes from ends of folder paths
    if gamesFilePath != None and gamesFilePath.endswith("/"):
        gamesFilePath = gamesFilePath[:-1]
    if screenshotsFilePath != None and screenshotsFilePath.endswith("/"):
        screenshotsFilePath = screenshotsFilePath[:-1]
    if musicFilePath != None and musicFilePath.endswith("/"):
        musicFilePath = musicFilePath[:-1]
    if photosFilePath != None and photosFilePath.endswith("/"):
        photosFilePath = photosFilePath[:-1]
    if extrasFilePath != None and extrasFilePath.endswith("/"):
        extrasFilePath = extrasFilePath[:-1]

    #
    if verbose:
        printAndFlush("Option summary:")
        printAndFlush(" databaseFilePath: " + str(databaseFilePath))
        printAndFlush(" gamesFilePath: " + str(gamesFilePath))
        printAndFlush(" screenshotsFilePath: " + str(screenshotsFilePath))
        printAndFlush(" musicFilePath: " + str(musicFilePath))
        printAndFlush(" photosFilePath: " + str(photosFilePath))
        printAndFlush(" extrasFilePath: " + str(extrasFilePath))

    #
    if verbose:
        printAndFlush("Opening database...")
    openDb(databaseFilePath)

    if verbose:
        printAndFlush("Fixing file paths...")
    fixFilenames(gamesFilePath, screenshotsFilePath, musicFilePath, photosFilePath, extrasFilePath, verbose, dryRun)

    if verbose:
        printAndFlush("Closing database...")
    closeDb()

    if verbose:
        printAndFlush("End of script.")
