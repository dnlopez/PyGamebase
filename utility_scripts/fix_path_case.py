#!/usr/bin/env python

# Given a GameBase database (in SQLite format),
# for all paths to external files recorded within it, specifically those to games, screenshots, music and extras,
# check for the existence of the file on disk with case-insensitive path comparison (even though the file system may be case-sensitive),
# and if found on disk with differing case to the path in the database,
# update the path in the database to match that which exists on disk.


# Python
import os
import os.path


#var testRelativeTo = null;
#var testPath = "/mnt/Ve/games/Sinclair ZX Spectrum/Speccymania/SpeccyMania/Screenshots/L/labyrinth(Sinclair).gif";
#var testRelativeTo = "/mnt/ve/games/Commodore Amiga/GameBaseAmiga/Screenshots";
#var testPath = "A/'Allo_'Allo!_Cartoon_Fun!.png";
#var testRelativeTo = "/mnt/ve/games/Commodore Amiga/GameBaseAmiga/Screenshots";
#var testPath = "0\17_+_4.png";
#console.log("test result: " + fixPathCase(testPath, testRelativeTo));

def fixPathCase(i_path, i_relativeTo):
    """
    Correct the case of a path by comparing to actually existing directory entries in the local filesystem.

    Params:
     i_path:
      (str)
      May be absolute or relative.
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
    components = i_path.split(os.sep)

    # If the first path component is empty, it's an absolute path,
    # so don't use any relative prefix, to start the filesystem browsing and result path at root ("/")
    if components[0] == "":
        relativeBase = ""
    # Else if the first path component isn't empty, it's a relative path,
    # so use the selected relative-to directory as the relative prefix
    else:
        relativeBase = i_relativeTo
        if relativeBase != "" and relativeBase[-1] != os.sep:
            relativeBase += os.sep

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
                #print("ok: " + component)
                currentSearchPath += component
            # Else if the input component isn't found in the file system,
            # look for a match (or matches) by case-insensitive comparison
            else:
                upperCasedComponent = component.upper()

                insensitiveMatchCount = 0
                firstMatchingDirEntry = None

                for dirEntry in dirEntries:
                    if dirEntry.upper() == upperCasedComponent:
                        #print("insensitively ok: " + component + " (-> " + dirEntries[dirEntryNo] + ")")

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
            #print("trying: " + filenameWithExtraUnderscore)
            if os.path.exists(i_basePath + os.path.sep + filenameWithExtraUnderscore):
                #print("found with underscore!")
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

def fixFilenames(i_basePathForGames, i_basePathForScreenshots, i_basePathForSids, i_basePathForExtras, i_dryRun):
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
     i_basePathForExtras:
      Either (str)
       Base path for values in Extras.Path
      or (None)
       Don't try and correct this field
     i_dryRun:
      (bool)
      false: Don't make any actual changes, only print the SQL that would normally be executed.

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
            print(errorDescription + ", for file: " + i_row[i_columnNames.index(i_filenameFieldName)])

        if (fixedFilename == i_row[i_columnNames.index(i_filenameFieldName)]):
            return ""

        #print("changing to: " + fixedFilename)
        return "UPDATE " + i_tableName + " SET " + i_filenameFieldName + " = '" + fixedFilename.replace("'", "''") + "' WHERE " + i_tableKeyFieldName + " = " + str(i_row[i_columnNames.index(i_tableKeyFieldName)]) + ';\n'

    # Fix fields Games.Filename, Games.ScrnshotFilename and Games.SidFilename
    cursor = g_db.execute("SELECT * FROM Games")
    columnNames = [column[0]  for column in cursor.description]
    rows = cursor.fetchall()
    for row in rows:
        if i_basePathForGames != None:
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "Filename", i_basePathForGames)

        if i_basePathForScreenshots != None:
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "ScrnshotFilename", i_basePathForScreenshots)

        if i_basePathForSids != None:
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Games", "GA_Id", "SidFilename", i_basePathForSids)

    # Fix field Extras.Path
    cursor = g_db.execute("SELECT * FROM Extras")
    columnNames = [column[0]  for column in cursor.description]
    rows = cursor.fetchall()
    for row in rows:
        if i_basePathForExtras != None:
            combinedSql += fixFilenameAndUpdateDb(columnNames, row, "Extras", "EX_Id", "Path", i_basePathForExtras)

    #
    combinedSql += "COMMIT TRANSACTION;";

    #
    print("SQL to be executed: ---")
    print(combinedSql)
    print("---")

    # Execute
    if not i_dryRun:
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

    COMMAND_NAME = "fix_path_case.py"

    def printUsage(i_outputStream):
        i_outputStream.write('''\
''' + COMMAND_NAME + ''', by Daniel Lopez, 03/05/2022
GameBase fix path case utility.

Given a GameBase database (in SQLite format),
for all paths to external files recorded within it, specifically those to games, screenshots, music and extras,
check for the existence of the file on disk with case-insensitive path comparison (even though the file system may be case-sensitive),
and if found on disk with differing case to the path in the database,
update the path in the database to match that which exists on disk.

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
  -e/--extras <folder path>
    Base folder that contains extras files.

 Info:
  -h/--help
    Show this help.
  -d/--dry-run
    Don't make any actual changes, only print the SQL that would normally be executed.
''')

    # Parameters, with their default values
    databaseFilePath = None
    gamesFilePath = None
    screenshotsFilePath = None
    musicFilePath = None
    extrasFilePath = None
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
                    print("ERROR: -g/--games requires a value.")
                    sys.exit(-1)
                gamesFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-s" or arg == "--screenshots":
                if argNo >= len(sys.argv):
                    print("ERROR: -s/--screenshots requires a value.")
                    sys.exit(-1)
                screenshotsFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-m" or arg == "--music":
                if argNo >= len(sys.argv):
                    print("ERROR: -m/--music requires a value.")
                    sys.exit(-1)
                musicFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-e" or arg == "--extras":
                if argNo >= len(sys.argv):
                    print("ERROR: -e/--extras requires a value.")
                    sys.exit(-1)
                extrasFilePath = sys.argv[argNo]
                argNo += 1

            elif arg == "-d" or arg == "--dry-run":
                dryRun = True

            elif arg == "-h" or arg == "--help":
                printUsage(sys.stdout)
                sys.exit(0)

            else:
                print("ERROR: Unrecognised option: " + arg)
                print("(Run with --help to show command usage.)")
                sys.exit(-1)

        # Else if it's an argument
        else:
            if databaseFilePath == None:
                databaseFilePath = arg
            elif param_sqliteFilePath == None:
                param_sqliteFilePath = arg
            else:
                print("ERROR: Too many arguments.")
                print("(Run with --help to show command usage.)")
                sys.exit(-1)

    if databaseFilePath == None:
        print("ERROR: Insufficient arguments.")
        print("(Run with --help to show command usage.)")
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
    if extrasFilePath != None and extrasFilePath.endswith("/"):
        extrasFilePath = extrasFilePath[:-1]

    #
    print("databaseFilePath: " + str(databaseFilePath))
    print("gamesFilePath: " + str(gamesFilePath))
    print("screenshotsFilePath: " + str(screenshotsFilePath))
    print("musicFilePath: " + str(musicFilePath))
    print("extrasFilePath: " + str(extrasFilePath))

    #
    openDb(databaseFilePath)
    fixFilenames(gamesFilePath, screenshotsFilePath, musicFilePath, extrasFilePath, dryRun)
    closeDb()
    print("end of script")
