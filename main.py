#!/usr/bin/python
# -*- coding: utf-8 -*-


# Python std
import sys
import sqlite3
import functools
import os.path
import re
import copy
import pprint

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import frontend
import utils


# + Parse command line {{{

COMMAND_NAME = "gamebase"

def printUsage(i_outputStream):
    i_outputStream.write('''\
''' + COMMAND_NAME + ''' by Daniel Lopez, 03/05/2022
GameBase frontend

Usage:
======
''' + COMMAND_NAME + ''' <config module file> [options...]

Params:
 config module file:
  Path of Python config file.
  eg. "configs/c64.py"

Options:
 --help
  Show this help.
''')

#
param_configModuleFilePath = None

import sys
argNo = 1
while argNo < len(sys.argv):
    arg = sys.argv[argNo]
    argNo += 1

    if arg[0] == "-":

        if arg == "--help":
            printUsage(sys.stdout)
            sys.exit(0)

        # TODO pass through QT options
        else:
            print("ERROR: Unrecognised option: " + arg)
            print("(Run with --help to show command usage.)")
            #sys.exit(-1)

    else:
        # Collect command-line arguments
        if param_configModuleFilePath == None:
            param_configModuleFilePath = arg
        else:
            print("ERROR: Too many arguments.")
            print("(Run with --help to show command usage.)")
            #sys.exit(-1)

#param_configModuleFilePath = "/mnt/gear/dan/docs/code/c/gamebase/c64.py"
if param_configModuleFilePath == None:
    print("ERROR: Insufficient arguments.")
    print("(Run with --help to show command usage.)")
    sys.exit(-1)

# + }}}


# Import specified module config file
param_configModuleFilePath = os.path.abspath(param_configModuleFilePath)
sys.path.append(os.path.dirname(param_configModuleFilePath))
import importlib
gamebase = importlib.import_module(os.path.splitext(os.path.basename(param_configModuleFilePath))[0])



# + Columns {{{

# + + Usable {{{

g_usableColumns = [
    {
        "id": "detail",
        "screenName": "Show detail (+)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "play",
        "screenName": "Start game (▶)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
    },
    {
        "id": "pic",
        "screenName": "Picture",
        "defaultWidth": 320,
        "sortable": False,
        "filterable": False,
    },
    {
        "id": "id",
        "screenName": "ID",
        "dbTableName": "Games",
        "dbFieldName": "GA_Id",
        "dbType": "Long Integer",
        "defaultWidth": 50,
        "sortable": False,
        "filterable": False,
        "textAlignment": "left",
        "comment": "Unique ID"
    },
    {
        "id": "name",
        "screenName": "Name",
        "dbTableName": "Games",
        "dbFieldName": "Name",
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game Name"
    },
    {
        "id": "year",
        "screenName": "Year",
        "dbTableName": "Years",
        "dbFieldName": "Year",
        "dbType": "Long Integer",
        "defaultWidth": 75,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "The Year (9999 = Unknown year)"
    },
    {
        "id": "publisher",
        "screenName": "Publisher",
        "dbTableName": "Publishers",
        "dbFieldName": "Publisher",
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "developer",
        "screenName": "Developer",
        "dbTableName": "Developers",
        "dbFieldName": "Developer",
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "programmer",
        "screenName": "Programmer",
        "dbTableName": "Programmers",
        "dbFieldName": "Programmer",
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "parent_genre",
        "screenName": "Parent genre",
        "dbTableName": "PGenres",
        "dbFieldName": "ParentGenre",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "genre",
        "screenName": "Genre",
        "dbTableName": "Genres",
        "dbFieldName": "Genre",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "language",
        "screenName": "Language",
        "dbTableName": "Languages",
        "dbFieldName": "Language",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "cracker",
        "screenName": "Cracker",
        "dbTableName": "Crackers",
        "dbFieldName": "Cracker",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "artist",
        "screenName": "Artist",
        "dbTableName": "Artists",
        "dbFieldName": "Artist",
        "dbType": "Text (510)",
        "defaultWidth": 250,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "license",
        "screenName": "License",
        "dbTableName": "Licenses",
        "dbFieldName": "License",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "rarity",
        "screenName": "Rarity",
        "dbTableName": "Rarities",
        "dbFieldName": "Rarity",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_name",
        "screenName": "Musician",
        "dbTableName": "Musicians",
        "dbFieldName": "Musician",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_photo",
        "screenName": "Musician photo",
        "dbTableName": "Musicians",
        "dbFieldName": "Photo",
        "dbType": "Text (510)",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Musician Photo within Photo Path"
    },
    {
        "id": "musician_group",
        "screenName": "Musician group",
        "dbTableName": "Musicians",
        "dbFieldName": "Grp",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "musician_nick",
        "screenName": "Musician nick",
        "dbTableName": "Musicians",
        "dbFieldName": "Nick",
        "dbType": "Text (510)",
        "defaultWidth": 150,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "music",
        "screenName": "Music",
        "dbTableName": "Games",
        "dbFieldName": "SidFilename",
        "dbType": "Memo/Hyperlink (255)",
        "defaultWidth": 35,
        "sortable": False,
        "filterable": False,
        "textAlignment": "center",
        "comment": "Music Filename within Music Path"
    },
    {
        "id": "pal_ntsc",
        "screenName": "PAL/NTSC",
        "dbTableName": "Games",
        "dbFieldName": "V_PalNTSC",
        "dbType": "Long Integer",
        "type": "enum",
        "enumMap": {
            0: "PAL",
            1: "both",
            2: "NTSC",
            3: "PAL[+NTSC?]"
        },
        "defaultWidth": 75,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game version is PAL, NTSC or BOTH (0=PAL, 1=BOTH, 2=NTSC, 3=PAL[+NTSC?])"
    },
    {
        "id": "control",
        "screenName": "Control",
        "dbTableName": "Games",
        "dbFieldName": "Control",
        "dbType": "Long Integer",
        "type": "enum",
        "enumMap": {
            0: "JoyPort2",
            1: "JoyPort1",
            2: "Keyboard",
            3: "PaddlePort2",
            4: "PaddlePort1",
            5: "Mouse",
            6: "LightPen",
            7: "KoalaPad",
            8: "LightGun"
        },
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Game's control method (0=JoyPort2, 1=JoyPort1, 2=Keyboard, 3=PaddlePort2, 4=PaddlePort1, 5=Mouse, 6=LightPen, 7=KoalaPad, 8=LightGun"
    },
    {
        "id": "clone_of",
        "screenName": "Clone of",
        "dbTableName": "Games",
        "dbFieldName": "CloneOf",
        "dbType": "Long Integer",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
    {
        "id": "prequel",
        "screenName": "Prequel",
        "dbTableName": "Games",
        "dbFieldName": "Prequel",
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of prequel game (0 if no prequel)"
    },
    {
        "id": "sequel",
        "screenName": "Sequel",
        "dbTableName": "Games",
        "dbFieldName": "Sequel",
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of sequel game (0 if no sequel)"
    },
    {
        "id": "related",
        "screenName": "Related",
        "dbTableName": "Games",
        "dbFieldName": "Related",
        "dbType": "Long Integer NOT NULL",
        "type": "gameId",
        "defaultWidth": 100,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
        "comment": "Link to GA_ID of related game (0 if no related game)"
    },
]

def usableColumn_getById(i_id):
    """
    Params:
     i_id:
      (str)

    Returns:
     Either (Column)
     or (None)
    """
    columns = [column  for column in g_usableColumns  if column["id"] == i_id]
    if len(columns) == 0:
        return None
    return columns[0]


# + + }}}

# + + In GUI table view {{{

g_tableColumns = [
    { "id": "detail",
      "screenName": "Show detail (+)",
      "width": 35,
      "sortable": False,
      "filterable": False,
      "textAlignment": "center"
    },
    { "id": "play",
      "screenName": "Start game (▶)",
      "width": 35,
      "sortable": False,
      "filterable": False,
      "textAlignment": "center"
    },
    { "id": "pic",
      "screenName": "Picture",
      "width": 320,
      "sortable": False,
      "filterable": False
    },
    #{ "id": "pic2",
    #  "screenName": "Picture 2",
    #  "width": 320,
    #  "sortable": False,
    #  "filterable": False
    #},
    { "id": "id",
      "screenName": "ID",
      "width": 50,
      "sortable": False,
      "filterable": False,
      "textAlignment": "left"
    },
    { "id": "name",
      "screenName": "Name",
      "width": 250,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    { "id": "year",
      "screenName": "Year",
      "width": 75,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    #{ "id": "playerssim",
    #  "screenName": "Players",
    #  "width": 75,
    #  "sortable": True,
    #  "filterable": True,
    #  "textAlignment": "left"
      #},
    { "id": "publisher",
      "screenName": "Publisher",
      "width": 250,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    { "id": "developer",
      "screenName": "Developer",
      "width": 250,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    { "id": "programmer",
      "screenName": "Programmer",
      "width": 250,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    { "id": "parent_genre",
      "screenName": "Parent genre",
      "width": 150,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    },
    { "id": "genre",
      "screenName": "Genre",
      "width": 150,
      "sortable": True,
      "filterable": True,
      "textAlignment": "left"
    }
]
# (list of Column)

# Type: Column
#  (dict)
#  Has keys:
#   screenName:
#    (str)
#    Used in
#     heading button, if it's visible
#     list of fields on right-click menu
#   width:
#    (int)
#    In pixels

# + + + New column accessors {{{

def tableColumn_add(i_id):
    usableColumn = usableColumn_getById(i_id)
    tableColumn = {
        "id": usableColumn["id"],
        "screenName": usableColumn["screenName"],
        "width": usableColumn["defaultWidth"],
        "sortable": usableColumn["sortable"],
        "filterable": usableColumn["filterable"],
        "textAlignment": usableColumn["textAlignment"]
    }

    g_tableColumns.append(tableColumn)

def tableColumn_remove(i_id):
    foundColumnNo = None
    for columnNo, column in enumerate(g_tableColumns):
        if column["id"] == i_id:
            foundColumnNo = columnNo
            break
    if foundColumnNo != None:
        del(g_tableColumns[foundColumnNo])

    #
    foundSortOperationNo = None
    for sortOperationNo, sortOperation in enumerate(headerBar.sort_operations):
        if sortOperation[0] == i_id:
            foundSortOperationNo = sortOperationNo
            break
    if foundSortOperationNo != None:
        del(headerBar.sort_operations[foundSortOperationNo])
        headerBar.sort_updateGui()

def tableColumn_toggle(i_id):
    present = tableColumn_getById(i_id)
    if not present:
        tableColumn_add(i_id)
    else:
        tableColumn_remove(i_id)

def tableColumn_move(i_moveColumn, i_beforeColumn):
    """
    Move a column.

    Params:
     i_moveColumn:
      (Column)
      Column to move.
     i_beforeColumn:
      Either (Column)
       Move to before of this column.
      or (None)
       Move to the end.
    """
    # Delete column from original position
    del(g_tableColumns[g_tableColumns.index(i_moveColumn)])

    # Reinsert/append in new position
    if i_beforeColumn == None:
        g_tableColumns.append(i_moveColumn)
    else:
        g_tableColumns.insert(g_tableColumns.index(i_beforeColumn), i_moveColumn)

def tableColumn_count():
    """
    Count the visible columns.

    Returns:
     (int)
    """
    return len(g_tableColumns)

def tableColumn_getBySlice(i_startPos=None, i_endPos=None):
    """
    Get the objects of a range of visible columns.

    Params:
     i_startPos, i_endPos:
      Either (int)
      or (None)

    Returns:
     (list of Column)
    """
    return g_tableColumns[i_startPos:i_endPos]

def tableColumn_getByPos(i_pos):
    """
    Get the object of the n'th column.

    Params:
     i_pos:
      (int)

    Returns:
     Either (Column)
     or (None)
    """
    if i_pos < 0 or i_pos >= len(g_tableColumns):
        return None
    return g_tableColumns[i_pos]

def tableColumn_getById(i_id):
    """
    Get the object of the column with some ID.

    Params:
     i_id:
      (str)

    Returns:
     Either (Column)
     or (None)
    """
    # [could shorten with next()]
    for column in g_tableColumns:
        if column["id"] == i_id:
            return column
    return None

def tableColumn_idToPos(i_id):
    """
    Get the visible position of the column with some ID.

    Params:
     i_id:
      (str)

    Returns:
     (int)
     Visible position of the column with the given ID.
     -1: There was no visible column with this ID.
    """
    visiblePos = -1
    for column in g_tableColumns:
        visiblePos += 1
        if i_id == column["id"]:
            return visiblePos
    return -1

# + + + }}}

# + + }}}

# + }}}

# + Screenshot file/URL resolving {{{

def normalizeDirPathFromConfig(i_dirPath):
    """
    Strip trailing slash from a directory path, if present.

    Params:
     i_dirPath:
      (str)
      eg.
       "/mnt/gamebase/games/"

    Returns:
     (str)
     eg.
      "/mnt/gamebase/games"
    """
    if i_dirPath.endswith("/") or i_dirPath.endswith("\\"):
        i_dirPath = i_dirPath[:-1]
    return i_dirPath

def getScreenshotAbsolutePath(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    if not hasattr(gamebase, "config_screenshotsBaseDirPath"):
        return None
    return normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + i_relativePath

def getScreenshotUrl(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    i_relativePath = i_relativePath.replace(" ", "%20")
    i_relativePath = i_relativePath.replace("#", "%23")
    screenshotAbsolutePath = getScreenshotAbsolutePath(i_relativePath)
    if screenshotAbsolutePath == None:
        return None
    return "file://" + getScreenshotAbsolutePath(i_relativePath)

# + }}}

# + DB {{{

g_db = None
g_db_gamesColumnNames = None
#  (list of str)
g_dbSchema = {}

def openDb():
    if not hasattr(gamebase, "config_databaseFilePath"):
        messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
        messageBox.setText("<big><b>Missing config setting:</b></big>")
        messageBox.setInformativeText("config_databaseFilePath")
        messageBox.exec()
        return

    global g_db
    #g_db = sqlite3.connect(gamebase.config_databaseFilePath)
    #print("file:" + gamebase.config_databaseFilePath + "?mode=ro")
    try:
        g_db = sqlite3.connect("file:" + normalizeDirPathFromConfig(gamebase.config_databaseFilePath) + "?mode=ro", uri=True)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
        messageBox.setText("<big><b>When opening database file:</b></big>")
        messageBox.setInformativeText("With path:\n" + gamebase.config_databaseFilePath + "\n\nAn error occurred:\n" + "\n".join(traceback.format_exception_only(e)))
        #messageBox.setFixedWidth(800)
        messageBox.exec()
        sys.exit(1)

    # Add REGEXP function
    def functionRegex(i_pattern, i_value):
        #print("functionRegex(" + i_value + ", " + i_pattern + ")")
        #c_pattern = re.compile(r"\b" + i_pattern.lower() + r"\b")
        compiledPattern = re.compile(i_pattern)
        return compiledPattern.search(str(i_value)) is not None
    g_db.create_function("REGEXP", 2, functionRegex)

    # Get names of tables
    cursor = g_db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    rows = cursor.fetchall()
    dbTableNames = [row[0]  for row in rows]

    # Remove columns from g_usableColumns whose tables don't exist in the database
    global g_usableColumns
    def validateUsableColumn(i_usableColumn):
        if not ("dbTableName" in i_usableColumn):
            return True
        return i_usableColumn["dbTableName"] in dbTableNames
    g_usableColumns = [column  for column in g_usableColumns  if validateUsableColumn(column)]

    # Remove columns from g_tableColumns that don't exist in g_usableColumns
    global g_tableColumns
    g_tableColumns = [column  for column in g_tableColumns  if usableColumn_getById(column["id"])]

    # Get info about tables
    g_db.row_factory = sqlite3.Row
    global g_dbSchema
    for tableName in ["Games", "Years", "Genres", "PGenres", "Publishers", "Developers", "Programmers", "Languages", "Crackers", "Artists", "Licenses", "Rarities", "Musicians"]:
        if tableName in dbTableNames:
            cursor = g_db.execute("PRAGMA table_info(" + tableName + ")")
            rows = cursor.fetchall()
            rows = [{keyName: row[keyName] for keyName in row.keys()}  for row in rows]  # Convert sqlite3.Row objects to plain dicts for easier viewing
            g_dbSchema[tableName] = rows

    # Get columns in Games table
    global g_db_gamesColumnNames
    g_db_gamesColumnNames = [row["name"]  for row in g_dbSchema["Games"]]

def closeDb():
    global g_db
    g_db.close()
    g_db = None

g_dbColumnNames = None
#  (list of str)
g_dbRows = None
#  (list of tuple)

def stringLooksLikeNumber(i_str):
    try:
        float(i_str)
        return True
    except ValueError:
        return False

def getJoinTermsToTable(i_tableName, io_tableConnections):
    """
    Params:
     i_tableName:
      (str)
     io_tableConnections:
      (dict)
      Mapping of table names to join clauses and dependencies
      eg.
       {
           "PGenres": {
               "dependencies": ["Genres"],
               "fromTerm": "LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id"
           },
           "Genres": {
               "dependencies": [],
               "fromTerm": "LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id"
           },
       }

    Returns:
     Function return value:
      (list of str)
     io_tableConnections:
      The used connections will be removed from the list.
    """
    rv = []

    if i_tableName in io_tableConnections:
        tableConnection = io_tableConnections[i_tableName]
        for dependency in tableConnection["dependencies"]:
            rv += getJoinTermsToTable(dependency, io_tableConnections)
        rv.append(tableConnection["fromTerm"])
        del(io_tableConnections[i_tableName])

    return rv

connectionsFromGamesTable = {
    "Years": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Years ON Games.YE_Id = Years.YE_Id"
    },
    "Genres": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id"
    },
    "PGenres": {
        "dependencies": ["Genres"],
        "fromTerm": "LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id"
    },
    "Publishers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Publishers ON Games.PU_Id = Publishers.PU_Id"
    },
    "Developers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Developers ON Games.DE_Id = Developers.DE_Id"
    },
    "Programmers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Programmers ON Games.PR_Id = Programmers.PR_Id"
    },
    "Languages": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Languages ON Games.LA_Id = Languages.LA_Id"
    },
    "Crackers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Crackers ON Games.CR_Id = Crackers.CR_Id"
    },
    "Artists": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Artists ON Games.AR_Id = Artists.AR_Id"
    },
    "Licenses": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Licenses ON Games.LI_Id = Licenses.LI_Id"
    },
    "Rarities": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Rarities ON Games.RA_Id = Rarities.RA_Id"
    },
    "Musicians": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Musicians ON Games.MU_Id = Musicians.MU_Id"
    },
}

def queryDb():
    selectTerms = [
        "Games.GA_Id",
        "Games.ScrnshotFilename",
        "Games.Comment",
        "Games.Gemus",
        "Games.Filename",
        "Games.FileToRun",
        "Games.MemoText"
    ]

    fromTerms = [
        "Games"
    ]

    tableConnections = copy.deepcopy(connectionsFromGamesTable)
    visibleDbNames = [(usableColumn["dbTableName"], usableColumn["dbFieldName"])
                      for usableColumn in [usableColumn_getById(column["id"])  for column in tableColumn_getBySlice()]
                      if "dbTableName" in usableColumn and "dbFieldName" in usableColumn]
    for tableName, fieldName in visibleDbNames:
        fromTerms += getJoinTermsToTable(tableName, tableConnections)

        if tableName == "Games" and fieldName == "GA_Id":
            pass
        else:
            selectTerms.append(tableName + "." + fieldName)

    if "CloneOf" in g_db_gamesColumnNames:
        selectTerms.append("CloneOfGame.Name AS CloneOfName")
        fromTerms.append("LEFT JOIN Games AS CloneOfGame ON Games.CloneOf = CloneOfGame.GA_Id")
    if "WebLink_Name" in g_db_gamesColumnNames:
        selectTerms.append("Games.WebLink_Name")
    if "WebLink_URL" in g_db_gamesColumnNames:
        selectTerms.append("Games.WebLink_URL")

    # SELECT
    sql = "SELECT " + ", ".join(selectTerms)
    sql += "\nFROM " + " ".join(fromTerms)

    # WHERE
    andGroups = []

    for filterRowNo in range(0, len(headerBar.filterRows)):
        andTerms = []

        for column in tableColumn_getBySlice():
            usableColumn = usableColumn_getById(column["id"])
            if column["filterable"]:
                value = headerBar.columnWidgets[column["id"]]["filterEdits"][filterRowNo].text()
                value = value.strip()
                if value != "":
                    # If range operator
                    betweenValues = value.split("~")
                    if len(betweenValues) == 2 and stringLooksLikeNumber(betweenValues[0]) and stringLooksLikeNumber(betweenValues[1]):
                        andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " BETWEEN " + betweenValues[0] + " AND " + betweenValues[1])

                    # Else if regular expression
                    elif len(value) > 2 and value.startswith("/") and value.endswith("/"):
                        # Get regexp
                        value = value[1:-1]

                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " REGEXP " + value)
                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                    # Else if a comparison operator (=, <>, >, <, >=, <=)
                    elif value.startswith("=") or value.startswith(">") or value.startswith("<"):
                        # Get operator and value
                        if value.startswith(">=") or value.startswith("<=") or value.startswith("<>"):
                            operator = value[:2]
                            value = value[2:]
                        else:
                            operator = value[:1]
                            value = value[1:]

                        # If testing for exact equality, handle the special value "NULL"
                        if operator == "=" and value == "NULL":
                            operator = "IS"
                        elif operator == "<>" and value == "NULL":
                            operator = "IS NOT"
                        # Else if value doesn't look like a number, format it as a string
                        elif not stringLooksLikeNumber(value):
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                        #
                        andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " " + operator + " " + value)

                    # Else if LIKE expression (contains an unescaped %)
                    elif value.replace("\\%", "").find("%") != -1:
                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " LIKE " + value + " ESCAPE '\\'")

                    # Else if a plain string
                    else:
                        value = "%" + value + "%"

                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " LIKE " + value + " ESCAPE '\\'")

        if len(andTerms) > 0:
            andGroups.append(andTerms)

    if len(andGroups) > 0:
        sql += "\nWHERE "
        sql += " OR ".join(["(" + andGroupStr + ")"  for andGroupStr in [" AND ".join(andGroup)  for andGroup in andGroups]])

    # ORDER BY
    if len(headerBar.sort_operations) > 0:
        sql += "\nORDER BY "

        orderByTerms = []
        for columnId, direction in headerBar.sort_operations:
            usableColumn = usableColumn_getById(columnId)
            term = usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"]
            if direction == -1:
                term += " DESC"
            orderByTerms.append(term)
        sql += ", ".join(orderByTerms)

    # Execute
    #print(sql)
    cursor = g_db.execute(sql)

    global g_dbColumnNames
    g_dbColumnNames = [column[0]  for column in cursor.description]
    global g_dbRows
    g_dbRows = cursor.fetchall()

    label_statusbar.setText("Showing " + str(len(g_dbRows)) + " games.")

def getGameRecord(i_gameId):
    # Select all fields from Games table
    fromTerms = [
        "Games"
    ]
    fullyQualifiedFieldNames = False
    if fullyQualifiedFieldNames:
        selectTerms = [
        ]
        for field in g_dbSchema["Games"]:
            selectTerms.append("Games." + field["name"] + " AS [Games." + field["name"] + "]")

    # For all other tables connected to Games
    # that are present in this database
    tableConnections = copy.deepcopy(connectionsFromGamesTable)
    tableNames = [tableName  for tableName in tableConnections.keys()  if tableName in g_dbSchema.keys()]
    for tableName in tableNames:
        # Join to it
        fromTerms += getJoinTermsToTable(tableName, tableConnections)
        # Select all fields from it
        if fullyQualifiedFieldNames:
            for field in g_dbSchema[tableName]:
                selectTerms.append(tableName + "." + field["name"] + " AS [" + tableName + "." + field["name"] + "]")

    # Build SQL string
    #  SELECT
    if fullyQualifiedFieldNames:
        sql = "SELECT " + ", ".join(selectTerms)
    else:
        sql = "SELECT *"
    #  FROM
    sql += "\nFROM " + " ".join(fromTerms)
    #  WHERE
    sql += "\nWHERE Games.GA_Id = " + str(i_gameId)

    # Execute
    g_db.row_factory = sqlite3.Row
    cursor = g_db.execute(sql)

    row = cursor.fetchone()
    row = {keyName: row[keyName] for keyName in row.keys()}  # Convert sqlite3.Row objects to plain dicts for easier viewing
    return row

def getExtrasRecords(i_gameId):
    # Build SQL string
    sql = "SELECT * FROM Extras"
    sql += "\nWHERE GA_Id = " + str(i_gameId)
    sql += "\nORDER BY DisplayOrder"

    # Execute
    g_db.row_factory = sqlite3.Row
    cursor = g_db.execute(sql)

    rows = cursor.fetchall()
    rows = [{keyName: row[keyName] for keyName in row.keys()}  for row in rows]  # Convert sqlite3.Row objects to plain dicts for easier viewing
    return rows

def dbRow_getScreenshotRelativePath(i_row):
    """
    Get the path of a game's first screenshot picture.
    This comes from the 'ScrnshotFilename' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      The database didn't specify a screenshot file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.screenshotRelativePath)
        #i_row.
        screenshotRelativePath = i_row["ScrnshotFilename"]
        if screenshotRelativePath != None:
            screenshotRelativePath = screenshotRelativePath.replace("\\", "/")

    # Return it from cache
    #return i_row.
    return screenshotRelativePath

def dbRow_getTitleshotRelativePath(i_row):
    """
    Get the path of a game's titleshot picture.
    This is alternative, equivalent terminology to the first screenshot.
    This comes from the 'ScrnshotFilename' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      The database didn't specify a titleshot file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.titleshotRelativePath)
        #i_row.
        titleshotRelativePath = dbRow_getScreenshotRelativePath(i_row);

    # Return it from cache
    #return i_row.
    return titleshotRelativePath;

def dbRow_getSupplementaryScreenshotPaths(i_row, i_simulateCount=None):
    """
    Params:
     i_row:
      (sqlite3.Row)
     i_simulateCount:
      Either (int)
      or (None)

    Returns:
     (list of str)
     Paths of images, relative to the 'Screenshots' folder.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#!i_row.supplementaryScreenshotPaths:
        supplementaryScreenshotPaths = []

        # Get titleshot relative path
        titleshotRelativePath = dbRow_getTitleshotRelativePath(i_row)
        if titleshotRelativePath != None:
            # Search disk for further image files similarly-named but with a numeric suffix
            screenshotStem, imageExtension = os.path.splitext(titleshotRelativePath)

            if i_simulateCount == None:
                screenshotNo = 1
                while True:
                    screenshotRelativePath = screenshotStem + "_" + str(screenshotNo) + imageExtension
                    screenshotAbsolutePath = getScreenshotAbsolutePath(screenshotRelativePath)
                    if screenshotAbsolutePath == None or not os.path.exists(screenshotAbsolutePath):
                        break

                    supplementaryScreenshotPaths.append(screenshotRelativePath)

                    screenshotNo += 1

                #i_row.supplementaryScreenshotPaths = supplementaryScreenshotPaths
            else:
                for screenshotNo in range(1, i_simulateCount + 1):
                    screenshotRelativePath = screenshotStem + "_" + str(screenshotNo) + imageExtension

                    supplementaryScreenshotPaths.append(screenshotRelativePath)

                return supplementaryScreenshotPaths;

    # Return it from cache
    #return i_row.
    return supplementaryScreenshotPaths

def dbRow_getPhotoRelativePath(i_row):
    """
    Get the path of a game's (musician) photo.
    This comes from the 'Photo' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Photos' folder.
     or (None)
      The database didn't specify a photo file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.photoRelativePath)
        #i_row.
        photoRelativePath = i_row["Photo"]
        if photoRelativePath != None:
            photoRelativePath = photoRelativePath.replace("\\", "/")

    # Return it from cache
    #return i_row.
    return photoRelativePath

# + }}}


class HeaderBar(QWidget):
    """
    A top row of buttons to act as table headings and controls for column resizing and sorting,
    and a second row of text box controls for entering filter criteria.
    """
    # Within this many pixels either side of a vertical boundary between header buttons, allow dragging to resize a column.
    resizeMargin = 10
    # Minimum number of pixels that a column can be resized to by dragging.
    minimumColumnWidth = 30

    headingButtonHeight = 30
    filterRowHeight = 30

    # Emitted after the text in one of the filter text boxes is changed, or a row is deleted
    filterChange = Signal()

    #print(tableView.geometry())
    #print(tableView.frameGeometry())
    #print(tableView.contentsMargins())
    #print(tableView.contentsRect())
    #tableView.horizontalHeader().resizeSection(self.parent().resize_columnNo, newWidth)

    class HeadingButton(QPushButton):
        def __init__(self, i_text, i_hasBorder, i_parent=None):
            QPushButton.__init__(self, i_text, i_parent)

            if not i_hasBorder:
                self.setStyleSheet("QPushButton { border: none; }");
                self.setFlat(True)
                self.setFocusPolicy(Qt.NoFocus)
                #self.setStyleSheet("QPushButton { background-color: red; color: black;}");

            # Receive mouse move events even if button isn't held down
            # and install event filter to let parent HeaderBar see all events first
            self.setMouseTracking(True)
            self.installEventFilter(self.parent())

            # + Context menu {{{

            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

            # + }}}

        # + Context menu {{{

        def onCustomContextMenuRequested(self, i_pos):
            contextMenu = QMenu(self)

            def action_onTriggered(i_columnId):
                tableColumn_toggle(i_columnId)

                # Update GUI
                # If the following recreateWidgets() call deletes the button which we right-clicked to open this context menu,
                # QT will subsequently segfault. To workaround this, use a one-shot zero-delay QTimer to continue at idle-time,
                # when apparently the context menu has been cleaned up and a crash does not happen.
                continueTimer = QTimer(self)
                continueTimer.setSingleShot(True)
                def on_continueTimer():
                    headerBar.recreateWidgets()
                    headerBar.repositionHeadingButtons()
                    headerBar.repositionFilterEdits()
                    headerBar.repositionTabOrder()

                    # Requery DB in case filter criteria have changed
                    queryDb()
                    tableView.requery()
                    #
                    tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])
                continueTimer.timeout.connect(on_continueTimer)
                continueTimer.start(0)

            action = contextMenu.addAction("Columns")
            action.setEnabled(False)
            contextMenu.addSeparator()
            for usableColumnNo, usableColumn in enumerate(g_usableColumns):
                action = contextMenu.addAction(usableColumn["screenName"])
                action.setCheckable(True)
                columnId = usableColumn["id"]
                action.setChecked(tableColumn_getById(columnId) != None)
                action.triggered.connect(functools.partial(action_onTriggered, columnId))

            contextMenu.popup(self.mapToGlobal(i_pos))
        #def mousePressEvent(self, i_event):
        #    if i_event.button() == Qt.MouseButton.RightButton:

        # + }}}

    class FilterEdit(QFrame):
        # Emitted after the text is changed
        textChange = Signal()

        def __init__(self, i_parent=None):
            QFrame.__init__(self, i_parent)

            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setProperty("class", "FilterEdit")
            self.setAutoFillBackground(True)

            self.layout = QHBoxLayout(self)
            self.setLayout(self.layout)
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)

            self.lineEdit = QLineEdit(self)
            self.lineEdit.setFixedHeight(HeaderBar.filterRowHeight)
            self.layout.addWidget(self.lineEdit)
            self.layout.setStretch(0, 1)
            self.lineEdit.editingFinished.connect(self.lineEdit_onEditingFinished)

            self.clearButton = QPushButton("", self)
            self.clearButton.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            self.clearButton.setStyleSheet("QPushButton { margin: 4px; border-width: 1px; border-radius: 10px; }");
            #self.clearButton.setFlat(True)
            self.clearButton.setFixedHeight(HeaderBar.filterRowHeight)
            self.clearButton.setFixedWidth(HeaderBar.filterRowHeight)
            self.clearButton.setFocusPolicy(Qt.NoFocus)
            self.clearButton.setVisible(False)
            self.layout.addWidget(self.clearButton)
            self.layout.setStretch(1, 0)
            self.clearButton.clicked.connect(self.clearButton_onClicked)

            self.lineEdit.textEdited.connect(self.lineEdit_onTextEdited)

        def lineEdit_onEditingFinished(self):
            # If text was modified, requery,
            # else focus the tableview
            textWasModified = self.lineEdit.isModified()
            self.lineEdit.setModified(False)
            if textWasModified:
                self.textChange.emit()
            else:
                tableView.setFocus()

        def lineEdit_onTextEdited(self, i_text):
            # Hide or show clear button depending on whether there's text
            self.clearButton.setVisible(i_text != "")

        def clearButton_onClicked(self):
            self.lineEdit.setText("")
            self.clearButton.setVisible(False)
            self.textChange.emit()

        def text(self):
            """
            Returns:
             (str)
            """
            return self.lineEdit.text()

        def setFocus(self, i_reason):
            self.lineEdit.setFocus(i_reason)

        def setText(self, i_text):
            """
            Params:
             i_text:
              (str)
            """
            self.lineEdit.setText(i_text)
            self.lineEdit_onTextEdited(i_text)

    def __init__(self, i_parent=None):
        QWidget.__init__(self, i_parent)

        # Allow this custom widget derived from a QWidget to be fully styled by stylesheets
        # https://stackoverflow.com/a/49179582
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.scrollX = 0
        self.scrollY = 0

        #pal = QPalette()
        #pal.setColor(QPalette.Window, Qt.red)
        #self.setPalette(pal)
        #self.setAutoFillBackground(True)

        #self.container = QWidget(self)
        #self.container.setGeometry(0, 0, 800, 90)

        #self.setStyleSheet("* { border: 1px solid red; }");

        self.columnWidgets = {}
        # (dict)
        # Per-column GUI widgets.
        # Dictionary has arbitrary key-value properties:
        #  Keys:
        #   (str)
        #   Column id
        #  Values:
        #   (dict)
        #   Dictionary has specific key-value properties:
        #    headingButton:
        #     (HeadingButton)
        #    filterEdits:
        #     (list of FilterEdit)

        self.filterRows = []
        # (list)
        # Per-filter row GUI widgets.
        # The length of this list is currently used as the primary indication of how many filter rows there are.
        # Each element is:
        #  (dict)
        #  Dictionary has specific key-value properties:
        #   deleteRow_pushButton:
        #    (QPushButton)

        # + Mouse drag to resize/reorder columns {{{

        self.installEventFilter(self)

        # Receive mouse move events even if button isn't held down
        self.setMouseTracking(True)

        # State used while resizing
        self.resize_column = None  # [rename to mouse_resize_...]
        self.resize_columnLeftX = None
        self.resize_mouseToEdgeOffset = None

        # State used while reordering
        self.reorder_column = None
        #  Either (Column)
        #  or (None)

        self.reorderIndicator_widget = QFrame(self)
        #self.reorderIndicator_widget.setAutoFillBackground(True)
        self.reorderIndicator_widget.setGeometry(10, 10, 100, 20)
        pal = QPalette()
        #pal.setColor(QPalette.Window, Qt.red)
        pal.setColor(QPalette.WindowText, Qt.red)
        self.reorderIndicator_widget.setPalette(pal)
        self.reorderIndicator_widget.hide()

        self.reorderIndicator_widget.setFrameStyle(QFrame.Box)
        self.reorderIndicator_widget.setLineWidth(2)

        # + }}}

        # State of column sorting
        self.sort_operations = []
        # (list)
        # Successive levels of sorting.
        # Each element is:
        #  (list)
        #  List has elements:
        #   0:
        #    (str)
        #    ID of the column to sort by
        #   1:
        #    (int)
        #    1: sort in ascending order
        #    -1: sort in descending order

        # Create header buttons
        self.recreateWidgets()

        #
        self.insertRow_pushButton = QPushButton("+", self)
        self.insertRow_pushButton.clicked.connect(self.insertRow_pushButton_onClicked)

        self.insertFilterRow(0)

        self.initFromColumns()

    def initFromColumns(self):
        # Create header buttons
        self.recreateWidgets()
        # Initially set all widget positions
        self.repositionHeadingButtons()
        self.repositionFilterEdits()
        self.repositionTabOrder()

    def recreateWidgets(self):
        """
        Call this when a filterable column is added or removed in the master description in g_tableColumns
        to create/delete GUI widgets as necessary, bringing self.columnWidgets into sync with it.
        """
        # For each new filterable, visible column
        # that does not already have header widgets
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"] and \
               (column["id"] not in self.columnWidgets):

                # Create an object for its header widgets
                widgetDict = {}

                # Create header button
                headingButton = HeaderBar.HeadingButton(column["screenName"], column["filterable"], self)
                widgetDict["headingButton"] = headingButton
                # Set its fixed properties (apart from position)
                headingButton.setVisible(True)
                headingButton.clicked.connect(functools.partial(self.headingButton_onClicked, column["id"]))

                # Create filter edits
                widgetDict["filterEdits"] = []
                for filterRowNo in range(0, len(self.filterRows)):
                    headerFilter = HeaderBar.FilterEdit(self)
                    widgetDict["filterEdits"].append(headerFilter)
                    # Set its fixed properties (apart from position)
                    headerFilter.setVisible(True)
                    headerFilter.textChange.connect(self.lineEdit_onTextChange)

                # Save the object of header widgets
                self.columnWidgets[column["id"]] = widgetDict

        # For each object of header widgets
        # which no longer corresponds to an existing, filterable, visible column
        columnIds = list(self.columnWidgets.keys())
        for columnId in columnIds:
            column = tableColumn_getById(columnId)
            if column != None:
                if not column["filterable"]:
                    column = None
            if column == None:

                # Remove all its widgets from the GUI
                widgetDict = self.columnWidgets[columnId]
                widgetDict["headingButton"].setParent(None)
                #del(widgetDict["headingButton"])
                for filterEdit in widgetDict["filterEdits"]:
                    filterEdit.setParent(None)

                # Remove object of header widgets
                del(self.columnWidgets[columnId])

    # + Filter rows {{{

    def insertFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """

        # Add per-filter row GUI widgets
        newRow = {}
        self.filterRows.insert(i_position, newRow)

        # 'Delete row' button
        deleteRow_pushButton = QPushButton("x", self)
        # Set its fixed properties (apart from position)
        deleteRow_pushButton.clicked.connect(functools.partial(self.deleteRow_pushButton_onClicked, newRow))
        deleteRow_pushButton.setVisible(True)
        # Save in member object
        newRow["deleteRow_pushButton"] = deleteRow_pushButton

        # Add per-column GUI widgets
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"]:
                # Create FilterEdit
                headerFilter = HeaderBar.FilterEdit(self)
                # Set its fixed properties (apart from position)
                headerFilter.setVisible(True)
                headerFilter.textChange.connect(self.lineEdit_onTextChange)
                # Save in member object
                self.columnWidgets[column["id"]]["filterEdits"].insert(i_position, headerFilter)

        # Resize header to accommodate the current number of filter rows
        self.setFixedHeight(HeaderBar.headingButtonHeight + HeaderBar.filterRowHeight*len(self.filterRows))

    def appendFilterRow(self):
        self.insertFilterRow(len(self.filterRows))

    def deleteFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """
        # Remove per-column widgets
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"]:
                # From the GUI
                self.columnWidgets[column["id"]]["filterEdits"][i_position].setParent(None)
                # From member object
                del(self.columnWidgets[column["id"]]["filterEdits"][i_position])

        # Remove per-filter row widgets
        filterRow = self.filterRows[i_position]

        # 'Delete row' button
        #  From the GUI
        filterRow["deleteRow_pushButton"].setParent(None)
        #  From member object
        del(self.filterRows[i_position])

        # Resize header to accommodate the current number of filter rows
        self.setFixedHeight(HeaderBar.headingButtonHeight + HeaderBar.filterRowHeight*len(self.filterRows))

    def clearFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"]:
                self.columnWidgets[column["id"]]["filterEdits"][i_position].setText("")

    def clearAllFilterRows(self):
        while len(self.filterRows) > 1:
            self.deleteFilterRow(len(self.filterRows) - 1)
        self.clearFilterRow(0)

        self.repositionFilterEdits()
        #self.repositionTabOrder()
        self.filterChange.emit()

    def deleteRow_pushButton_onClicked(self, i_filterRow):
        if len(self.filterRows) == 1:
            self.clearFilterRow(0)
        else:
            for filterRowNo, filterRow in enumerate(self.filterRows):
                if filterRow == i_filterRow:
                    self.deleteFilterRow(filterRowNo)
                    self.repositionFilterEdits()
                    #self.repositionTabOrder()
        self.filterChange.emit()

    def insertRow_pushButton_onClicked(self):
        self.appendFilterRow()
        #self.repositionHeadingButtons()
        self.repositionFilterEdits()
        self.repositionTabOrder()

    # + }}}

    #def sizeHint(self):
    #    return QSize(10000, 59)

    # + Scrolling {{{

    def scroll(self, i_dx, i_dy):
        self.scrollX += i_dx
        self.scrollY += i_dy
        QWidget.scroll(self, i_dx, i_dy)

    # + }}}

    # + Sorting {{{

    def headingButton_onClicked(self, i_columnId):
        self.sort(i_columnId, application.queryKeyboardModifiers() == Qt.ControlModifier)

    def sort(self, i_columnId, i_appendOrModify):
        """
        Params:
         i_columnId:
          (str)
         i_appendOrModify:
          (bool)
        """
        # Get column object
        clickedColumn = tableColumn_getById(i_columnId)

        # If column isn't sortable,
        # bail
        if not clickedColumn["sortable"]:
            return

        # Update list of sort operations
        if not i_appendOrModify:
            if len(self.sort_operations) == 1 and self.sort_operations[0][0] == clickedColumn["id"]:
                self.sort_operations[0][1] = -self.sort_operations[0][1]
            else:
                self.sort_operations = [[clickedColumn["id"], 1]]
        else:
            found = False
            for operation in self.sort_operations:
                if operation[0] == clickedColumn["id"]:
                    operation[1] = -operation[1]
                    found = True
            if not found:
                self.sort_operations.append([clickedColumn["id"], 1])

        #
        self.sort_updateGui()

        # Requery DB in new order
        queryDb()
        tableView.requery()

    def sort_updateGui(self):
        # Update header button texts with arrows
        def subscriptDigit(i_digit):
            """
            Params:
             i_digit:
              (int)

            Returns:
             (str)
            """
            return "₀₁₂₃₄₅₆₇₈₉"[i_digit % 10]

        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"]:
                headingButton = self.columnWidgets[column["id"]]["headingButton"]

                newCaption = column["screenName"]

                sortIndex = 1
                sortDirection = 0
                for operation in self.sort_operations:
                    if operation[0] == column["id"]:
                        sortDirection = operation[1]
                        break
                    sortIndex += 1
                if sortDirection != 0:
                    if sortDirection == 1:
                        newCaption += "  ▲" + subscriptDigit(sortIndex)
                    else: # if sortDirection == -1:
                        newCaption += "  ▼" + subscriptDigit(sortIndex)

                headingButton.setText(newCaption)

    # + }}}

    def lineEdit_onTextChange(self):
        self.filterChange.emit()

    # + Mouse drag to resize/reorder columns {{{

    def _columnBoundaryNearPixelX(self, i_x, i_withinMargin=None):
        """
        Params:
         i_x:
          (int)
          Relative to the left of the window.
         i_withinMargin:
          Either (int)
           Require the resulting edge to be within this many pixels of i_x
          or (None)
           Get the nearest edge regardless of how far from i_x it is.

        Returns:
         Either (tuple)
          Tuple has elements:
           0:
            Either (Column)
             The object of the visible column before the edge that i_x is nearest to
            or (None)
             There is no before the edge that i_x is nearest to (ie. it is the first edge).
           1:
            Either (Column)
             The object of the visible column after the edge that i_x is nearest to
            or (None)
             There is no after the edge that i_x is nearest to (ie. it is the last edge).
           2:
            (int)
            Column edge X pixel position
          (None, None, None): There are no visible columns, or there is not an edge within the distance of i_withinMargin.
        """
        # If no visible columns,
        # return none
        tableColumns = tableColumn_getBySlice()
        if len(tableColumns) == 0:
            return None, None, None

        # Indicate left edge of first column
        columnEdgeX = 0
        nearest = (None, tableColumns[0], columnEdgeX)

        # For each column, replace result with its right edge if it's nearer
        for tableColumnNo, column in enumerate(tableColumns):
            columnEdgeX += column["width"]
            if abs(i_x - columnEdgeX) <= abs(i_x - nearest[2]):
                nextColumn = None
                if tableColumnNo + 1 < len(tableColumns):
                    nextColumn = tableColumns[tableColumnNo + 1]
                nearest = (column, nextColumn, columnEdgeX)

        # If requested a maximum margin and closest edge is not within that,
        # return none
        if i_withinMargin != None and abs(i_x - nearest[2]) > i_withinMargin:
            return None, None, None

        # Return details of closest edge
        return nearest

    def _columnAtPixelX(self, i_x):
        """
        Params:
         i_x:
          (int)
          Relative to the left of the window.

        Returns:
         Either (Column)
          The object of the visible column that i_x is under
         or (None)
          There is not a visible column at i_x.
        """
        if i_x < 0:
            return None

        x = 0
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            x += column["width"]
            if i_x < x:
                return column

        return None

    def _columnScreenX(self, i_column):
        """
        Params:
         i_column:
          (Column)

        Returns:
         Either (int)
         or (None)
        """
        x = 0
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column == i_column:
                return x
            x += column["width"]

        return None

    def eventFilter(self, i_watched, i_event):
        #print(i_event.type())

        if i_event.type() == QEvent.MouseButtonPress:
            # If pressed the left button
            if i_event.button() == Qt.MouseButton.LeftButton:
                # Get mouse pos relative to the HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # If holding Shift
                if i_event.modifiers() & Qt.ShiftModifier:
                    self.reorder_column = self._columnAtPixelX(mousePos.x())
                    self.reorder_dropBeforeColumn = self.reorder_column

                    # Show drop indicator
                    self.reorderIndicator_widget.setGeometry(self._columnScreenX(self.reorder_column), 0, self.reorder_column["width"], HeaderBar.headingButtonHeight)
                    self.reorderIndicator_widget.show()
                    self.reorderIndicator_widget.raise_()

                    return True
                # Else if cursor is near a draggable vertical edge
                else:
                    leftColumn, rightColumn, edgeX = self._columnBoundaryNearPixelX(mousePos.x(), HeaderBar.resizeMargin)
                    if leftColumn != None:
                        #
                        self.resize_column = leftColumn
                        self.resize_columnLeftX = edgeX - self.resize_column["width"]

                        # Get horizontal distance from mouse to the draggable vertical edge (ie. the right edge of the button being resized)
                        #button = column["headingButton"]
                        #buttonBottomRight = button.mapTo(self, QPoint(button.size().width(), button.size().height()))
                        self.resize_mouseToEdgeOffset = edgeX - mousePos.x()

                        #
                        return True

        elif i_event.type() == QEvent.MouseMove:
            # If currently resizing,
            # do the resize
            if self.resize_column != None:
                # Get mouse pos relative to the HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # Get new width
                newRightEdge = mousePos.x() + self.resize_mouseToEdgeOffset
                newWidth = newRightEdge - self.resize_columnLeftX
                if newWidth < HeaderBar.minimumColumnWidth:
                    newWidth = HeaderBar.minimumColumnWidth
                # Resize column
                self.resize_column["width"] = newWidth

                # Move/resize buttons and lineedits
                self.repositionHeadingButtons()
                self.repositionFilterEdits()
                #
                tableView.horizontalHeader().resizeSection(tableColumn_idToPos(self.resize_column["id"]), newWidth)

                return True

            # Else if currently reordering,
            # draw line at nearest vertical edge
            elif self.reorder_column != None:
                # Get mouse pos relative to the HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                #
                leftColumn, rightColumn, edgeX = self._columnBoundaryNearPixelX(mousePos.x())
                self.reorder_dropBeforeColumn = rightColumn
                if self.reorder_dropBeforeColumn == self.reorder_column:
                    self.reorderIndicator_widget.setGeometry(self._columnScreenX(self.reorder_column), 0, self.reorder_column["width"], HeaderBar.headingButtonHeight)
                else:
                    self.reorderIndicator_widget.setGeometry(edgeX - 3 + self.scrollX, 0, 6, self.height())

            # Else if not currently resizing or reordering,
            # then depending on whether cursor is near a draggable vertical edge,
            # set cursor shape
            else:
                # Get mouse pos relative to the HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                #
                leftColumn, _, _ = self._columnBoundaryNearPixelX(mousePos.x(), HeaderBar.resizeMargin)
                if leftColumn != None:
                    self.setCursor(Qt.SizeHorCursor)
                else:
                    self.unsetCursor()

        elif i_event.type() == QEvent.MouseButtonRelease:
            # If currently resizing and released the left button
            if self.resize_column != None and i_event.button() == Qt.MouseButton.LeftButton:
                # Stop resizing
                self.resize_column = None

                #
                return True

            # Else if currently reordering and released the left button
            if self.reorder_column != None and i_event.button() == Qt.MouseButton.LeftButton:
                if self.reorder_column != self.reorder_dropBeforeColumn:
                    tableColumn_move(self.reorder_column, self.reorder_dropBeforeColumn)

                # Stop reordering
                self.reorder_column = None

                #
                self.reorderIndicator_widget.hide()
                # Move/resize buttons and lineedits
                self.repositionHeadingButtons()
                self.repositionFilterEdits()
                self.repositionTabOrder()
                #
                tableView.requery()
                #
                tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])
                #self.reorderIndicator_widget.setFrameRect(QRect(edgeX - 2, 0, 4, 20))
                #self.reorderIndicator_widget.setFrameRect(QRect(2, 2, 50, 10))
                #print(leftColumn["id"], rightColumn["id"], edgeX)

                #
                return True

        # Let event continue
        return False

    # + }}}

    def repositionHeadingButtons(self):
        x = 0
        x += self.scrollX  # Adjust for horizontal scroll amount
        y = 0
        for column in tableColumn_getBySlice():
            if column["filterable"]:
                self.columnWidgets[column["id"]]["headingButton"].setGeometry(x, y, column["width"], HeaderBar.headingButtonHeight)
            x += column["width"]

    def repositionFilterEdits(self):
        y = HeaderBar.headingButtonHeight

        for filterRowNo, filterRow in enumerate(self.filterRows):
            x = 0
            x += self.scrollX  # Adjust for horizontal scroll amount
            for columnNo, column in enumerate(tableColumn_getBySlice()):
                if column["filterable"]:
                    self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].setGeometry(x, y, column["width"], HeaderBar.filterRowHeight)
                x += column["width"]

            filterRow["deleteRow_pushButton"].setGeometry(x, y, HeaderBar.filterRowHeight, HeaderBar.filterRowHeight)
            x += HeaderBar.filterRowHeight

            y += HeaderBar.filterRowHeight

        y -= HeaderBar.filterRowHeight
        self.insertRow_pushButton.setGeometry(x, y, HeaderBar.filterRowHeight, HeaderBar.filterRowHeight)

    def repositionTabOrder(self):
        previousWidget = None

        # For each heading button
        for column in tableColumn_getBySlice():
            if column["filterable"]:
                nextWidget = self.columnWidgets[column["id"]]["headingButton"]
                if previousWidget != None:
                    self.setTabOrder(previousWidget, nextWidget)
                previousWidget = nextWidget

        # For each filter edit
        for filterRowNo, filterRow in enumerate(self.filterRows):
            for column in tableColumn_getBySlice():
                if column["filterable"]:
                    nextWidget = self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].lineEdit
                    if previousWidget != None:
                        self.setTabOrder(previousWidget, nextWidget)
                    previousWidget = nextWidget

            nextWidget = filterRow["deleteRow_pushButton"]
            if previousWidget != None:
                self.setTabOrder(previousWidget, nextWidget)
            previousWidget = nextWidget

        #
        nextWidget = self.insertRow_pushButton
        if previousWidget != None:
            self.setTabOrder(previousWidget, nextWidget)
        previousWidget = nextWidget


class MyStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, i_parent=None):
        QStyledItemDelegate.__init__(self, i_parent)

    def initStyleOption(self, i_option, i_index):
        QStyledItemDelegate.initStyleOption(self, i_option, i_index)

        # Default selection colours
        i_option.palette.setColor(QPalette.Active, QPalette.Highlight, QColor.fromRgbF(0, 0, 0.75, 1))
        i_option.palette.setColor(QPalette.Inactive, QPalette.Highlight, QColor.fromRgbF(0.8125, 0.8125, 0.8125, 1))
        i_option.palette.setColor(QPalette.Active, QPalette.HighlightedText, QColor.fromRgbF(1, 1, 1, 1))
        i_option.palette.setColor(QPalette.Inactive, QPalette.HighlightedText, QColor.fromRgbF(0, 0, 0, 1))

    def paint(self, i_painter, i_option, i_index):
        #print(i_painter, i_option, i_index)

        #if i_option.state & QStyle.State_Selected:
        #    i_painter.fillRect(i_option.rect, i_option.palette.highlight())

        column = tableColumn_getByPos(i_index.column())

        # Screenshot
        if column["id"] == "pic":
            screenshotPath = dbRow_getScreenshotRelativePath(g_dbRows[i_index.row()])
            if screenshotPath != None:
                if hasattr(gamebase, "config_screenshotsBaseDirPath"):
                    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath)
                    i_painter.drawPixmap(i_option.rect, pixmap)
        elif column["id"] == "musician_photo":
            photoPath = dbRow_getPhotoRelativePath(g_dbRows[i_index.row()])
            if photoPath != None:
                if hasattr(gamebase, "config_photosBaseDirPath"):
                    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_photosBaseDirPath) + "/" + photoPath)
                    i_painter.drawPixmap(i_option.rect, pixmap)
        else:
            QStyledItemDelegate.paint(self, i_painter, i_option, i_index)

class MyTableModel(QAbstractTableModel):
    FilterRole = Qt.UserRole + 1

    def __init__(self, i_parent, *args):
        QAbstractTableModel.__init__(self, i_parent, *args)

    def rowCount(self, i_parent):
        if g_dbRows == None:
            return 0
        return len(g_dbRows)

    def columnCount(self, i_parent):
        return tableColumn_count()

    #https://stackoverflow.com/questions/7988182/displaying-an-image-from-a-qabstracttablemodel
    #https://forum.qt.io/topic/5195/qtableview-extra-column-space-solved/8
    def data(self, i_index, i_role):
        if not i_index.isValid():
            return None

        column = tableColumn_getByPos(i_index.column())

        # Detail
        if column["id"] == "detail":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                return "+"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Play
        elif column["id"] == "play":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                if g_dbRows[i_index.row()][g_dbColumnNames.index("Filename")] == None:
                    return ""
                return "▶"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Music
        elif column["id"] == "music":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                if g_dbRows[i_index.row()][g_dbColumnNames.index("SidFilename")] == None:
                    return ""
                return "M"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Screenshot
        elif column["id"] == "pic":
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    screenshotPath = g_dbRows[i_index.row()][g_dbColumnNames.index("ScrnshotFilename")]
            #    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath)
            #    return pixmap;
            pass
        #
        else:
            usableColumn = usableColumn_getById(column["id"])
            # Enum field
            if "type" in usableColumn and usableColumn["type"] == "enum":
                if i_role == MyTableModel.FilterRole:
                    return g_dbRows[i_index.row()][usableColumn["dbFieldName"]]
                elif i_role == Qt.DisplayRole:
                    value = g_dbRows[i_index.row()][usableColumn["dbFieldName"]]
                    if value in usableColumn["enumMap"]:
                        value = str(value) + ": " + usableColumn["enumMap"][value]
                    return value
                elif i_role == Qt.TextAlignmentRole:
                    if column["textAlignment"] == "center":
                        return Qt.AlignCenter
                    elif column["textAlignment"] == "left":
                        return Qt.AlignLeft
            # Game ID field
            if "type" in usableColumn and usableColumn["type"] == "gameId":
                if i_role == MyTableModel.FilterRole:
                    return g_dbRows[i_index.row()][usableColumn["dbFieldName"]]
                elif i_role == Qt.DisplayRole:
                    value = g_dbRows[i_index.row()][usableColumn["dbFieldName"]]
                    if value == 0:
                        return ""
                    return ">" + str(value)
                elif i_role == Qt.TextAlignmentRole:
                    if column["textAlignment"] == "center":
                        return Qt.AlignCenter
                    elif column["textAlignment"] == "left":
                        return Qt.AlignLeft
            # Other ordinary text field
            else:
                if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                    return g_dbRows[i_index.row()][usableColumn["dbFieldName"]]
                elif i_role == Qt.TextAlignmentRole:
                    if column["textAlignment"] == "center":
                        return Qt.AlignCenter
                    elif column["textAlignment"] == "left":
                        return Qt.AlignLeft

        return None

    # [Not used anymore since the native QTableView headers are hidden]
    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            column = tableColumn_getByPos(i_columnNo)
            return column["screenName"]

        return None

# [No longer used]
def dbRowToDict(i_row, i_columnNames):
    """
    Params:
     i_row:
      (list)
     i_columnNames:
      (list of str)

    Returns:
     (dict)
    """
    rv = {}

    for columnNo, columnName in enumerate(i_columnNames):
        rv[columnName] = i_row[columnNo]

    return rv

# [No longer used]
def getGameInfoDict(i_dbRow):
    """
    Params:
     i_dbRow:
      (list)
    """
    return dbRowToDict(i_dbRow, g_dbColumnNames)

def findGameWithId(i_id):
    idColumnNo = g_dbColumnNames.index("GA_Id")
    for rowNo, row in enumerate(g_dbRows):
        if row[idColumnNo] == i_id:
            return rowNo
    return None

class MyTableView(QTableView):
    def __init__(self, i_parent=None):
        QTableView.__init__(self, i_parent)

        # set font
        #font = QFont("Courier New", 14)
        #self.setFont(font)

        ## set column width to fit contents (set font first!)
        #self.resizeColumnsToContents()

        # Create model and set it in the table view
        self.tableModel = MyTableModel(None)
        self.setModel(self.tableModel)

        # Set row height
        #self.rowHeight(200)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(200)
        self.verticalHeader().setMinimumSectionSize(2)
        self.verticalHeader().hide()

        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        #self.horizontalHeader().setDefaultSectionSize(200)
        #self.horizontalHeader().resizeSection(0, 20)
        #self.horizontalHeader().resizeSection(1, 20)
        #self.horizontalHeader().resizeSection(2, 300)
        #self.horizontalHeader().resizeSection(3, 50)
        self.horizontalHeader().hide()

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # + Context menu {{{

        self.contextMenu_filter = QMenu("Use in filter")

        self.contextMenu_filter_or = QMenu("OR", self.contextMenu_filter)
        action = self.contextMenu_filter_or.addAction("Containing")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", ""))
        action = self.contextMenu_filter_or.addAction("Not containing")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "nc"))
        action = self.contextMenu_filter_or.addAction("Equal to (=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "="))
        action = self.contextMenu_filter_or.addAction("Not equal to (<>)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "<>"))
        action = self.contextMenu_filter_or.addAction("Greater than (>)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", ">"))
        action = self.contextMenu_filter_or.addAction("Greater than or equal to (>=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", ">="))
        action = self.contextMenu_filter_or.addAction("Less than (<)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "<"))
        action = self.contextMenu_filter_or.addAction("Less than or equal to (<=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "<="))
        action = self.contextMenu_filter_or.addAction("Regular expression (/.../)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "OR", "/.../"))
        self.contextMenu_filter.addMenu(self.contextMenu_filter_or)

        self.contextMenu_filter.addSeparator()
        action = self.contextMenu_filter.addAction("AND")
        action.setEnabled(False)
        action = self.contextMenu_filter.addAction("Containing")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", ""))
        action = self.contextMenu_filter.addAction("Not containing")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "nc"))
        action = self.contextMenu_filter.addAction("Equal to (=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "="))
        action = self.contextMenu_filter.addAction("Not equal to (<>)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "<>"))
        action = self.contextMenu_filter.addAction("Greater than (>)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", ">"))
        action = self.contextMenu_filter.addAction("Greater than or equal to (>=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", ">="))
        action = self.contextMenu_filter.addAction("Less than (<)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "<"))
        action = self.contextMenu_filter.addAction("Less than or equal to (<=)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "<="))
        action = self.contextMenu_filter.addAction("Regular expression (/.../)")
        action.triggered.connect(functools.partial(self.contextMenu_filter_item_onTriggered, "AND", "/.../"))

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # + }}}

        #
        self.clicked.connect(functools.partial(self.onActivatedOrClicked, False))
        self.activated.connect(functools.partial(self.onActivatedOrClicked, True))

        #https://stackoverflow.com/questions/69076597/how-can-i-remove-the-outside-gridlines-of-qtablewidget-and-qheaderview
        # Have no border on the table view so the scrollbar is right at the edge
        self.setStyleSheet("""
             QTableView { padding-left: 0px; border: 0px; margin: 0px; /*border-top: 1px solid grey;*/ }
        """)
        #self.setStyleSheet("""
        #     QTableView::item {padding-left: 0px; border-top: 1px solid red; border-left: 1px solid red; border-bottom: none; border-right: none; margin: 0px}
        #""")
        #self.horizontalHeader().setStyleSheet("""
        #    QHeaderView::section {padding-left: 0px; border: 0px}
        #""")

        # Resizing of rows by mouse dragging
        self.viewport().installEventFilter(self)
        #  Receive mouse move events even if button isn't held down
        self.viewport().setMouseTracking(True)
        #  State used while resizing
        self.resize_rowNo = None
        self.resize_lastMouseY = None
        self.resize_selectedRowTopY = None

        #self.verticalScrollBar().setSingleStep(30)

    def onActivatedOrClicked(self, i_keyboardOriented, i_modelIndex):
        """
        Params:
         i_keyboardOriented:
          (bool)
         i_modelIndex:
          (QModelIndex)
        """
        columnId = tableColumn_getByPos(i_modelIndex.column())["id"]

        if columnId == "detail":
            self.scrollTo(i_modelIndex, QAbstractItemView.PositionAtTop)
            detailPaneWasAlreadyVisible = detailPane_height() > 0
            detailPane_show()
            if g_dbRows[i_modelIndex.row()][g_dbColumnNames.index("GA_Id")] != detailPane_currentGameId:
                detailPane_populate(i_modelIndex.row())
            if i_keyboardOriented and detailPaneWasAlreadyVisible:
                detailPane_webEngineView.setFocus(Qt.OtherFocusReason)

        elif columnId == "play":
            rowNo = i_modelIndex.row()
            gameId = g_dbRows[rowNo][g_dbColumnNames.index("GA_Id")]

            try:
                gamebase.runGame(g_dbRows[rowNo][g_dbColumnNames.index("Filename")],
                                 g_dbRows[rowNo][g_dbColumnNames.index("FileToRun")],
                                 getGameRecord(gameId))
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
                messageBox.setText("<big><b>In runGame():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                #messageBox.setFixedWidth(800)
                messageBox.exec()

        elif columnId == "music":
            rowNo = i_modelIndex.row()
            gameId = g_dbRows[rowNo][g_dbColumnNames.index("GA_Id")]

            try:
                gamebase.runMusic(g_dbRows[rowNo][g_dbColumnNames.index("SidFilename")],
                                  getGameRecord(gameId))
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
                messageBox.setText("<big><b>In runMusic():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                #messageBox.setFixedWidth(800)
                messageBox.exec()

        else:
            usableColumn = usableColumn_getById(columnId)
            if usableColumn["type"] == "gameId":
                # Get the target game ID
                rowNo = i_modelIndex.row()
                gameId = g_dbRows[rowNo][g_dbColumnNames.index(usableColumn["dbFieldName"])]

                # Look for row in table,
                # and if not found then clear filter and look again
                rowNo = findGameWithId(gameId)
                if rowNo == None:
                    headerBar.clearAllFilterRows()
                    rowNo = findGameWithId(gameId)

                # If found, select it
                if rowNo != None:
                    selectedIndex = self.selectionModel().currentIndex()
                    tableView.selectionModel().setCurrentIndex(tableView.selectionModel().model().index(rowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

    def selectionChanged(self, i_selected, i_deselected):
        QTableView.selectionChanged(self, i_selected, i_deselected)

        # If detail pane is open,
        # repopulate it from the new row
        if detailPane_height() > 0:
            selectedIndex = self.selectionModel().currentIndex()
            if g_dbRows[selectedIndex.row()][g_dbColumnNames.index("GA_Id")] != detailPane_currentGameId:
                detailPane_populate(selectedIndex.row())

    # + Context menu {{{

    def onCustomContextMenuRequested(self, i_pos):
        # Create a menu for this popup
        contextMenu = QMenu(self)

        # If selected column is filterable then add the submenu for filtering
        selectedIndex = self.selectionModel().currentIndex()
        column = tableColumn_getByPos(selectedIndex.column())
        if column["filterable"]:
            contextMenu.addMenu(self.contextMenu_filter)
            contextMenu.addSeparator()

        # Add remainder of top-level context menu actions
        action = contextMenu.addAction("Copy")
        action.triggered.connect(self.clipboardCopy)
        action.setShortcut(QKeySequence("Ctrl+C"))

        # Popup the menu
        contextMenu.popup(self.viewport().mapToGlobal(i_pos))

    def contextMenu_filter_item_onTriggered(self, i_combiner, i_comparisonOperation): #, i_checked):
        selectedIndex = self.selectionModel().currentIndex()
        selectedValue = self.tableModel.data(selectedIndex, MyTableModel.FilterRole)

        formattedCriteria = None
        if i_comparisonOperation == "nc":
            formattedCriteria = "/^((?!" + str(selectedValue) + ").)*$/"
        elif i_comparisonOperation == "/.../":
            formattedCriteria = "/" + str(selectedValue) + "/"
        else:
            formattedCriteria = i_comparisonOperation + str(selectedValue)

        if i_combiner == "OR":
            headerBar.appendFilterRow()
            headerBar.repositionFilterEdits()
            headerBar.repositionTabOrder()

        columnId = tableColumn_getByPos(selectedIndex.column())["id"]
        headerBar.columnWidgets[columnId]["filterEdits"][-1].setText(formattedCriteria)
        headerBar.filterChange.emit()

    # + }}}

    def scrollContentsBy(self, i_dx, i_dy):
        # If the table view is scrolled horizontally,
        # scroll external header by the same amount
        QTableView.scrollContentsBy(self, i_dx, i_dy)
        headerBar.scroll(i_dx, 0)

    def requery(self):
        self.tableModel.modelReset.emit()

    def updateGeometries(self):
        # Increase the horizontal scrollbar's maximum to enable scrolling to the insert/delete filter row buttons 

        # Save initial scrollbar position to prevent jitter
        initialValue = self.horizontalScrollBar().value()

        #
        QTableView.updateGeometries(self)

        # Calculate and set new scrollbar maximum
        allColumnsWidth = sum([column["width"]  for column in tableColumn_getBySlice()])
        newMaximum = allColumnsWidth - self.horizontalScrollBar().pageStep() + HeaderBar.filterRowHeight*2 + self.verticalScrollBar().width()
        if newMaximum < 0:
            newMaximum = 0
        self.horizontalScrollBar().setMaximum(newMaximum)

        # Restore initial scrollbar position
        self.horizontalScrollBar().setValue(initialValue)

    def clipboardCopy(self):
        selectedIndexes = self.selectedIndexes()
        if len(selectedIndexes) == 1:
            QApplication.clipboard().setText(self.tableModel.data(selectedIndexes[0], Qt.DisplayRole))
        elif len(selectedIndexes) > 1:
            # Group selected cells by row
            import itertools
            indexGroups = itertools.groupby(sorted(selectedIndexes), lambda index: index.row())
            # Extract text of each cell
            textRows = []
            for indexGroup in indexGroups:
                textRows.append([self.tableModel.data(index, Qt.DisplayRole)  for index in indexGroup[1]])
            # Convert texts to CSV format
            rowCsvs = []
            for textRow in textRows:
                rowCsv = []
                for text in textRow:
                    if isinstance(text, str):
                        text = '"' + text.replace('"', '""') + '"'
                    else:
                        text = str(text)
                    rowCsv.append(text)
                rowCsvs.append(rowCsv)
            csv = "\n".join([",".join(rowCsv)  for rowCsv in rowCsvs])
            # Copy CSV text to clipboard
            QApplication.clipboard().setText(csv)

    def keyPressEvent(self, i_event):
        # If pressed Ctrl+C
        if i_event.key() == Qt.Key_C and (i_event.modifiers() & Qt.ControlModifier):
            self.clipboardCopy()
        else:
            super().keyPressEvent(i_event)

    def resizeAllColumns(self, i_widths):
        """
        Params:
         i_widths:
          (list of int)
        """
        for widthNo, width in enumerate(i_widths):
            self.horizontalHeader().resizeSection(widthNo, width)

    # + Resizing rows by mouse dragging {{{

    def rowHeight(self):
        """
        Returns:
         (int)
        """
        return self.verticalHeader().defaultSectionSize()

    # Within this many pixels either side of a horizontal boundary between rows, allow dragging to resize a row.
    resizeMargin = 10

    def _rowBoundaryNearPixelY(self, i_y):
        """
        Params:
         i_y:
          (int)
          Relative to the top of the widget.

        Returns:
         Either (tuple)
          Tuple has elements:
           0:
            (int)
            Row number
           1:
            (int)
            Row edge Y pixel position
          (None, None): There is not a row boundary near i_y.
        """
        rowHeight = self.rowHeight()

        # Get current scroll position in pixels
        #  If scrolling is per item,
        #  temporarily turn that off
        #  so that the scrollbar returns positions in pixels instead of items
        if tableView.verticalScrollMode() == QAbstractItemView.ScrollPerPixel:
            scrollY = self.verticalScrollBar().value()
        else: # if tableView.verticalScrollMode() == QAbstractItemView.ScrollPerItem:
            tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            scrollY = self.verticalScrollBar().value()
            tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

        # Add current scroll position to i_y to make it relative to the top of the content
        i_y += scrollY

        #
        offsetFromEdge = i_y % rowHeight

        effectiveResizeMargin = min(MyTableView.resizeMargin, self.rowHeight() / 8)

        if offsetFromEdge >= rowHeight - effectiveResizeMargin:
            rowNo = int(i_y / rowHeight)
            return (rowNo, rowNo * rowHeight - scrollY)
        elif offsetFromEdge <= effectiveResizeMargin:
            rowNo = int(i_y / rowHeight) - 1
            return (rowNo, rowNo * rowHeight - scrollY)
        else:
            return None, None

    def eventFilter(self, i_watched, i_event):
        if i_watched != self.viewport():
            return False
        #print(i_event.type())

        if i_event.type() == QEvent.MouseButtonPress:
            # If pressed the left button
            if i_event.button() == Qt.MouseButton.LeftButton:
                # Get mouse pos relative to the MyTableView
                mousePos = i_watched.mapTo(self, i_event.pos())
                # If cursor is near a draggable horizontal edge
                # change the pointer shape
                rowNo, _ = self._rowBoundaryNearPixelY(mousePos.y())
                if rowNo != None:
                    self.resize_rowNo = rowNo
                    self.resize_lastMouseY = mousePos.y()
                    self.resize_scrollModeIsPerItem = tableView.verticalScrollMode() == QAbstractItemView.ScrollPerItem

                    # Remember where on the screen the row being resized is
                    #selectedIndex = tableView.selectionModel().currentIndex()
                    #self.resize_selectedRowId = g_dbRows[selectedIndex.row()][g_dbColumnNames.index("GA_Id")]
                    self.resize_selectedRowTopY = tableView.rowViewportPosition(rowNo)

                    # If scrolling is per item,
                    # temporarily turn that off for the duration of the resize
                    # so that the scrollbar returns positions in pixels and we can resize smoothly
                    if self.resize_scrollModeIsPerItem:
                        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

                    #
                    return True

        elif i_event.type() == QEvent.MouseMove:
            # If not currently resizing,
            # then depending on whether cursor is near a draggable horizontal edge,
            # set cursor shape
            if self.resize_rowNo == None:
                # Get mouse pos relative to the MyTableView
                mousePos = i_watched.mapTo(self, i_event.pos())
                # If cursor is near a draggable horizontal edge
                # change the pointer shape
                rowNo, _ = self._rowBoundaryNearPixelY(mousePos.y())
                if rowNo != None:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.unsetCursor()
            # Else if currently resizing,
            # do the resize
            else:
                # Get mouse pos relative to the MyTableView
                mousePos = i_watched.mapTo(self, i_event.pos())
                # Get distance moved
                deltaY = mousePos.y() - self.resize_lastMouseY
                # Change row height
                self.verticalHeader().setDefaultSectionSize(self.rowHeight() + deltaY)
                # Keep start of initially resized row in same position on screen
                self.verticalScrollBar().setValue(self.rowHeight() * self.resize_rowNo - self.resize_selectedRowTopY)

                self.resize_lastMouseY = mousePos.y()

                return True

        elif i_event.type() == QEvent.MouseButtonRelease:
            # If currently resizing and released the left button
            if self.resize_rowNo != None and i_event.button() == Qt.MouseButton.LeftButton:
                # Stop resizing
                self.resize_rowNo = None

                if self.resize_scrollModeIsPerItem:
                    self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

                #
                return True

        elif i_event.type() == QEvent.Leave:
            self.unsetCursor()

        # Let event continue
        return False

    # + }}}

# Create a Qt application
# (or reuse old one if it already exists; ie. when re-running in REPL during development)
if not QApplication.instance():
    application = QApplication(sys.argv)
else:
    application = QApplication.instance()

# Create a top-level window by creating a widget with no parent
mainWindow = QWidget()
mainWindow.resize(800, 600)
mainWindow.move(QApplication.desktop().rect().center() - mainWindow.rect().center())
mainWindow.move(QApplication.desktop().rect().center() - mainWindow.rect().center())
if hasattr(gamebase, "config_title"):
    mainWindow.setWindowTitle(gamebase.config_title + " - GameBase")
else:
    mainWindow.setWindowTitle(param_configModuleFilePath + " - GameBase")

mainWindow.setProperty("class", "mainWindow")

frontend.mainWindow = mainWindow

#mainWindow.setStyleSheet("* {background-color: white; }")

# Application-wide keyboard shortcuts
shortcut = QShortcut(QKeySequence("Ctrl+F"), mainWindow)
shortcut.setContext(Qt.ApplicationShortcut)
def ctrlFShortcut_onActivated():
    # If table view has the focus and the selected column is filterable,
    # target that
    selectedIndex = tableView.selectionModel().currentIndex()
    selectedColumn = tableColumn_getByPos(selectedIndex.column())
    if tableView.hasFocus() and selectedColumn["filterable"]:
        targetColumn = selectedColumn
    # Else target the first visible and filterable column
    else:
        for column in tableColumn_getBySlice():
            if column["filterable"]:
                targetColumn = column
                break

    # Set focus to filter edit control
    if targetColumn != None:
        headerBar.columnWidgets[targetColumn["id"]]["filterEdits"][0].setFocus(Qt.ShortcutFocusReason)
shortcut.activated.connect(ctrlFShortcut_onActivated)

shortcut = QShortcut(QKeySequence("Escape"), mainWindow)
shortcut.setContext(Qt.ApplicationShortcut)
def escShortcut_onActivated():
    # If table view is not already focused,
    # focus it
    if not tableView.hasFocus():
        tableView.setFocus(Qt.ShortcutFocusReason)
    # Else if table view is not already focused,
    # close the detail pane
    else:
        detailPane_hide()
shortcut.activated.connect(escShortcut_onActivated)

shortcut = QShortcut(QKeySequence("F12"), mainWindow)
shortcut.setContext(Qt.ApplicationShortcut)
def f12Shortcut_onActivated():
    # If detail pane is closed
    if detailPane_height() == 0:
        # Scroll selected row to top
        selectedIndex = tableView.selectionModel().currentIndex()
        tableView.scrollTo(selectedIndex, QAbstractItemView.PositionAtTop)

        # Open, populate and focus the detail pane
        detailPane_show()

        if g_dbRows[selectedIndex.row()][g_dbColumnNames.index("GA_Id")] != detailPane_currentGameId:
            detailPane_populate(selectedIndex.row())

        detailPane_webEngineView.setFocus(Qt.OtherFocusReason)
    # Else if detail pane is open,
    # close it (and return focus to the table view)
    else:
        detailPane_hide()
shortcut.activated.connect(f12Shortcut_onActivated)

# Window layout
mainWindow_layout = QVBoxLayout()
mainWindow_layout.setSpacing(0)
mainWindow_layout.setContentsMargins(0, 0, 0, 0)
mainWindow.setLayout(mainWindow_layout)

# Layout overview:
#  mainWindow
#   menuBar
#   splitter
#    gameTable
#     headerBar
#     tableView
#    detailPane
#   statusbar

#
menuBar = QMenuBar()
mainWindow_layout.addWidget(menuBar)

def menu_file_openDatabaseInExternalProgram_onTriggered(i_checked):
    openInDefaultApplication([gamebase.config_databaseFilePath])

# [currently just for menu_file_openDatabaseInExternalProgram_onTriggered()]
def openInDefaultApplication(i_filePaths):
    """
    Params:
     i_filePaths:
      Either (str)
      or (list of str)
    """
    # Choose launcher command
    import platform
    #  If on macOS
    if platform.system() == "Darwin":
        executableAndArgs = ["open"]
    #  Else if on Windows
    elif platform.system() == "Windows":
        executableAndArgs = ["start"]
    #  Else assume a Linux variant
    else:
        executableAndArgs = ["xdg-open"]

    # Append file paths
    if type(i_filePaths) == str:
        executableAndArgs.append(i_filePaths)
    else:  # if an array
        executableAndArgs.extend(i_filePaths)

    # [shellExecList()]

    # Quote arguments if necessary
    import shlex
    executableAndArgs = [shlex.quote(arg)  for arg in executableAndArgs]

    # Convert to string
    executableAndArgs = " ".join(executableAndArgs)

    # [Use "...String()" function]
    # Start program
    import subprocess
    popen = subprocess.Popen(executableAndArgs,
                             shell=True,
                             stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())

menu = QMenu(mainWindow)
#menu.addAction("File")
#menuBar.addMenu(menu)
fileMenu_action = menuBar.addMenu("&File")
action = fileMenu_action.addAction("Open &database in external program")
action.triggered.connect(menu_file_openDatabaseInExternalProgram_onTriggered)
fileMenu_action.addAction("New")
fileMenu_action.addAction("Open")
fileMenu_action.addAction("Save")
fileMenu_action.addSeparator()
fileMenu_action.addAction("Quit")
editMenu_action = menuBar.addMenu("&Edit")
editMenu_action.addAction("Copy")
#menuBar.addMenu("View")
#menuBar.addMenu("Help")

# Create splitter
splitter = QSplitter(Qt.Vertical)
mainWindow_layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

#
gameTable = QWidget()
gameTable.setProperty("class", "gameTable")
splitter.addWidget(gameTable)
splitter.setStretchFactor(0, 0)  # Don't stretch game table when window is resized
#gameTable.setMinimumHeight(1)  # Allow splitter to slide all the way over this widget without snapping closed
#gameTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
# Set background colour
#gameTable.setStyleSheet("* { background-color: white; }")
#gameTable.backgroundRole().setColor(QPalette.Window, QColor.red())
pal = QPalette()
pal.setColor(QPalette.Window, Qt.white)
gameTable.setAutoFillBackground(True)
gameTable.setPalette(pal)
gameTable.show()

gameTable_layout = QVBoxLayout()
gameTable_layout.setSpacing(0)
gameTable_layout.setContentsMargins(0, 0, 0, 0)
gameTable.setLayout(gameTable_layout)

def splitter_onSplitterMoved(i_pos, i_index):
    # If detail pane has been dragged closed,
    # call detailPane_hide() to keep track
    if splitter.sizes()[1] == 0:
        detailPane_hide()
splitter.splitterMoved.connect(splitter_onSplitterMoved)

# Create header
headerBar = HeaderBar()
headerBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
gameTable_layout.addWidget(headerBar)

def headerBar_onFilterChange():
    # Remember what game is currently selected and where on the screen the row is
    selectedIndex = tableView.selectionModel().currentIndex()
    if selectedIndex.row() < 0 or selectedIndex.row() >= len(g_dbRows):
        selectedGameId = None
    else:
        selectedGameId = g_dbRows[selectedIndex.row()][g_dbColumnNames.index("GA_Id")]
        selectedRowTopY = tableView.rowViewportPosition(selectedIndex.row())

    # Query database and update table widget data
    queryDb()
    tableView.requery()

    # If a game was previously selected,
    # search for new row number of that game
    # and if found, scroll to put that game in the same screen position it previously was
    if selectedGameId != None:
        idColumnNo = g_dbColumnNames.index("GA_Id")
        newDbRowNo = None
        for dbRowNo, dbRow in enumerate(g_dbRows):
            if dbRow[idColumnNo] == selectedGameId:
                newDbRowNo = dbRowNo
                break

        if newDbRowNo == None:
            tableView.scrollToTop()
        else:
            tableView.verticalScrollBar().setValue(tableView.rowHeight() * newDbRowNo - selectedRowTopY)
            tableView.selectionModel().setCurrentIndex(tableView.selectionModel().model().index(newDbRowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)
headerBar.filterChange.connect(headerBar_onFilterChange)

# Create table
tableView = MyTableView()
gameTable_layout.addWidget(tableView)
tableView.setItemDelegate(MyStyledItemDelegate())
# Set vertical size policy to 'Ignored' which lets widget shrink to zero
#  https://stackoverflow.com/questions/18342590/setting-qlistwidget-minimum-height
tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

#  Set initial column widths
tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])

# Create detail pane
#class DetailPane(QWidget):
#    def __init__(self):
#        QWidget.__init__(self)
#        #QShortcut(QKeySequence("Escape"), self, activated=self.escapeShortcut_onActivated)
#        #QShortcut(QKeySequence("Page Up"), self, activated=self.pageUpShortcut_onActivated)
#    #def escapeShortcut_onActivated(self):
#    #    detailPane_hide()
#    #def pageUpShortcut_onActivated(self):
#    #    detailPane_hide()

detailPane_widget = QWidget()
detailPane_widget.setProperty("class", "detailPane")
splitter.addWidget(detailPane_widget)
splitter.setStretchFactor(1, 1)  # Do stretch detail pane when window is resized
detailPane_layout = QHBoxLayout()
detailPane_layout.setSpacing(0)
detailPane_layout.setContentsMargins(0, 0, 0, 0)
detailPane_widget.setLayout(detailPane_layout)

def detailPane_show():
    # Position splitter so that the table view shows exactly one row
    topPaneHeight = headerBar.geometry().height() + tableView.rowHeight()
    if tableView.horizontalScrollBar().isVisible():
        topPaneHeight += application.style().pixelMetric(QStyle.PM_ScrollBarExtent)  # Scrollbar height
    splitter.setSizes([topPaneHeight, splitter.geometry().height() - topPaneHeight])
    # Switch table view scroll mode so that an item will stay aligned at the top,
    # to fit neatly into the area we resized above
    tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

def detailPane_hide():
    # Hide detail pane
    splitter.setSizes([splitter.geometry().height(), 0])
    # Stop forcibly aligning an item to the top of the table view
    tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    # Give focus to the component next in line, ie. the table view
    tableView.setFocus(Qt.OtherFocusReason)

def detailPane_height():
    """
    Returns:
     (int)
    """
    return splitter.sizes()[1]

detailPane_margin = QPushButton("x")
detailPane_margin.clicked.connect(detailPane_hide)
#detailPane_margin = QWidget()
detailPane_layout.addWidget(detailPane_margin)
#detailPane_margin_layout = QVBoxLayout()
#detailPane_margin.setLayout(detailPane_margin_layout)

detailPane_margin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
#detailPane_margin.setGeometry(0, 0, tableColumn_getByPos(0)["width"], 100)
detailPane_margin.setFixedWidth(tableColumn_getByPos(0)["width"])
#print(tableColumn_getByPos(0)["width"])

#detailPane_margin_layout.addWidget(QPushButton())
#detailPane_margin_layout.addWidget(QPushButton())
#detailPane_margin_layout.addWidget(QPushButton())

detailPane_webEngineView = QWebEngineView()
detailPane_webEngineView.setProperty("class", "webEngineView")
detailPane_layout.addWidget(detailPane_webEngineView)

detailPane_currentGameId = None
def detailPane_populate(i_rowNo):
    """
    Params:
     i_rowNo:
      (int)
    """
    gameRow = getGameRecord(g_dbRows[i_rowNo][g_dbColumnNames.index("GA_Id")])

    global detailPane_currentGameId
    detailPane_currentGameId = gameRow["GA_Id"]

    html = ""

    html += '<link rel="stylesheet" type="text/css" href="file://' + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + '/detail_pane.css">'

    # Insert screenshots after the first one
    supplementaryScreenshotRelativePaths = dbRow_getSupplementaryScreenshotPaths(gameRow)
    for relativePath in supplementaryScreenshotRelativePaths:
        screenshotUrl = getScreenshotUrl(relativePath)
        if screenshotUrl != None:
            html += '<img src="' + screenshotUrl + '">'

    # If this game is a clone,
    # insert a link to the original
    if "CloneOfName" in gameRow and gameRow["CloneOfName"] != None:  # [broken]
        html += '<p style="white-space: pre-wrap;">'
        html += 'Clone of: '

        html += '<a href="#">' + gameRow["CloneOfName"] + '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #
        #    for (var columnNo = 0, columnCount = g_tableColumns.length; columnNo < columnCount; ++columnNo)
        #    {
        #        var column = tableColumn_getByPos(columnNo);
        #
        #        if (column.filterable)
        #        {
        #            if (column.id == "name")
        #                column.headerFilter.setValue(i_gameRow.CloneOfName);
        #            else
        #                column.headerFilter.setValue("");
        #        }
        #    }
        #
        #    queryDb();
        #    tableView.requery()
        #    //showDetailPane(0);
        #    g_dynamicTable.scrollTop = 0;
        #});
        html += '</p>'

    # Insert memo text
    if gameRow["MemoText"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += gameRow["MemoText"]
        html += '</p>'

    # Insert comment
    if gameRow["Comment"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += gameRow["Comment"]
        html += '</p>'

    # Insert weblink(s)
    if "WebLink_Name" in g_dbColumnNames and gameRow["WebLink_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'

        html += gameRow["WebLink_Name"] + ": "
        url = gameRow["WebLink_URL"]
        html += '<a target="_blank" href="' + url + '">'
        html += url
        html += '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #    electron.shell.openExternal(this.href);
        #});

        # If it's a World Of Spectrum link then insert a corresponding Spectrum Computing link
        if "WebLink_Name" in g_dbColumnNames and gameRow["WebLink_Name"] == "WOS":
            # Separator
            html += '<span style="margin-left: 8px; margin-right: 8px; border-left: 1px dotted #666;"></span>'
            # Label
            html += 'Spectrum Computing: '
            # Link
            url = url.replace("http://www.worldofspectrum.org/infoseekid.cgi?id=", "https://spectrumcomputing.co.uk/entry/")
            html += '<a target="_blank" href="' + url + '">'
            html += url
            html += '</a>'
            html += '</span>'
            #link.addEventListener("click", function (i_event) {
            #    i_event.preventDefault();
            #    electron.shell.openExternal(this.href);
            #});

        html += '</p>'

    # Get extras
    extrasRows = getExtrasRecords(str(gameRow["GA_Id"]))

    # Seperate extras which are and aren't images
    imageRows = []
    nonImageRows = []
    for extrasRow in extrasRows:
        path = extrasRow["Path"]
        if path != None and (path.lower().endswith(".jpg") or path.lower().endswith(".jpeg") or path.lower().endswith(".gif") or path.lower().endswith(".png")):
            imageRows.append(extrasRow)
        else:
            nonImageRows.append(extrasRow)

    # For each non-image, insert a link
    if len(nonImageRows) > 0:
        html += '<div id="nonImageExtras">'

        for nonImageRowNo, nonImageRow in enumerate(nonImageRows):
            #var label = nonImageRow.Name + " (" + nonImageRow.Path + ")";
            #container.appendChild(document.createTextNode(label));

            if nonImageRowNo > 0:
                #container.appendChild(document.createTextNode(" | "));
                html += '<span style="margin-left: 8px; margin-right: 8px; border-left: 1px dotted #666;"></span>'

            html += '<a'
            path = nonImageRow["Path"]
            if path != None:
                html += ' href="extra:///' + path + '"'
            html += '>'
            html += nonImageRow["Name"]
            html += '</a>'

        html += "</div>"


    # For each image, insert an image
    if len(imageRows) > 0:
        html += '<div id="imageExtras">'

        for imageRowNo, imageRow in enumerate(imageRows):
            #print("imageRow: " + str(imageRow))
            #var cell = document.createElement("div");

            html += '<a href="extra:///' + imageRow["Path"] + '" style="display: inline-block; text-align: center;">'
            if hasattr(gamebase, "config_extrasBaseDirPath"):
                html += '<img src="file://' + normalizeDirPathFromConfig(gamebase.config_extrasBaseDirPath) + "/" + imageRow["Path"] + '" style="height: 300px;">'
            #html += '<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" style="height: 300px;">'
            html += '<div>' + imageRow["Name"] + '</div>'
            html += '</a>'

            #cell.appendChild(link);

        html += "</div>"

    print(html)

    #detailPane_webEngineView.setHtml(html, QUrl("file:///"))
    # Load HTML into a QWebEnginePage with a handler for link clicks
    class WebEnginePage(QWebEnginePage):
        def __init__(self, i_gameRow, i_extrasRows, i_parent=None):
            QWebEnginePage.__init__(self, i_parent)

            self.gameRow = i_gameRow
            self.extrasRows = i_extrasRows

        def acceptNavigationRequest(self, i_qUrl, i_requestType, i_isMainFrame):
            if i_requestType == QWebEnginePage.NavigationTypeLinkClicked:
                #print(i_isMainFrame)

                # If it's a link to an extra,
                # pass it to the config file's runExtra()
                url = i_qUrl.toString()
                if url.startswith("extra:///"):
                    extraPath = url[9:]
                    extraInfo = [row  for row in self.extrasRows  if row["Path"] == extraPath][0]
                    gameInfo = self.gameRow
                    try:
                        gamebase.runExtra(extraPath, extraInfo, gameInfo)
                    except Exception as e:
                        import traceback
                        print(traceback.format_exc())
                        messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
                        messageBox.setText("<big><b>In runExtra():</b></big>")
                        messageBox.setInformativeText(traceback.format_exc())
                        #messageBox.setFixedWidth(800)
                        messageBox.exec()
                # Else if it's a normal link,
                # open it with the default browser
                else:
                    QDesktopServices.openUrl(i_qUrl)

                # Refuse navigation
                return False

            else:
                return True
    webEnginePage = WebEnginePage(gameRow, extrasRows, detailPane_webEngineView)
    webEnginePage.setHtml(html, QUrl("file:///"))
    # Let background of application show through to stop white flash on page loads
    webEnginePage.setBackgroundColor(Qt.transparent)

    def webEnginePage_onLinkHovered(i_url):
        if i_url == "":
            label_statusbar.setText("Showing " + str(len(g_dbRows)) + " games.")
        else:
            label_statusbar.setText(i_url)
    webEnginePage.linkHovered.connect(webEnginePage_onLinkHovered)

    # Load web engine page into the web engine view
    #webEnginePage.setView(detailPane_webEngineView)
    detailPane_webEngineView.setPage(webEnginePage)

# Create statusbar
label_statusbar = QLabel()
label_statusbar.setProperty("class", "statusbar")
#mainWindow_layout.addSpacing(8)
mainWindow_layout.addWidget(label_statusbar)
label_statusbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
label_statusbar.setContentsMargins(8, 8, 8, 8)

## Create test for styling
#class StyleTest(QWidget):
#    def __init__(self, i_parent=None):
#        QWidget.__init__(self, i_parent)
#        self.setAttribute(Qt.WA_StyledBackground, True)
#        #self.setProperty("class", "zzz2")
#        #print(self.property("class"))
#
#        #pal = QPalette()
#        #pal.setColor(QPalette.Window, Qt.red)
#        #self.setPalette(pal)
#        #self.setAutoFillBackground(True)
#
#        #self.container = QWidget(self)
#        #self.container.setGeometry(0, 0, 800, 90)
#
#        #self.setStyleSheet("* { border: 1px solid red; }");
#
#    #def sizeHint(self):
#    #    return QSize(10000, 59)
#
#
#zzz = StyleTest()
#zzz.setProperty("class", "zzz2")
#mainWindow_layout.addWidget(zzz)
#zzz.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#zzz.setAutoFillBackground(True)
#zzz.setFixedSize(300, 120)

detailPane_hide()

#
mainWindow.show()

openDb()

headerBar.initFromColumns()
queryDb()
tableView.requery()
tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])

headerBar.sort("name", False)  # TODO what if name column is initially not visible

# + Subprocess output {{{

class Log(QPlainTextEdit):
    def __init__(self, i_parent=None):
        QPlainTextEdit.__init__(self, i_parent)

        self.setWindowTitle("Subprocess Output")
        self.setGeometry(50, 75, 600, 400)
        #self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        #self.setUndoRedoEnabled(False)
        font = QFont("monospace")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        #self.document().setDefaultFont(QFont("monospace", 10, QFont.Normal))

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(500)
        self.refresh_timer.timeout.connect(self.updateText)

        self.updateText()

    def setVisible(self, i_visible):
        QPlainTextEdit.setVisible(self, i_visible)
        if i_visible:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()

    def updateText(self):
        if len(utils.tasks) > 0:
            # For AsyncSubprocess
            #print(utils.tasks[-1].getState())
            #mergedOutput = utils.tasks[-1].getMergedOutput()
            #subprocessOutput_log.setPlainText(mergedOutput.decode("utf-8"))

            task = utils.tasks[-1]

            text = "Run: " + str(task.executableAndArgs)
            if task.popen != None:
                text += "\nPID: " + str(task.popen.pid)
            text += "\n---\n"
            text += task.output
            if task.returncode != None:
                text += "\n---\nProcess exited with code " + str(task.returncode)

            self.setPlainText(text)
        else:
            self.setPlainText("")

subprocessOutput_log = None
def menu_file_showSubprocessOutput_onTriggered(i_checked):
    global subprocessOutput_log
    if subprocessOutput_log == None:
        subprocessOutput_log = Log()

    subprocessOutput_log.show()

action = fileMenu_action.addAction("Show subprocess &output")
action.triggered.connect(menu_file_showSubprocessOutput_onTriggered)

# + }}}

# Enter Qt application main loop
exitCode = application.exec_()
sys.exit(exitCode)
