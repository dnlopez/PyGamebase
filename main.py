#!/usr/bin/python
# -*- coding: utf-8 -*-


# Python std
import sys
import sqlite3
import functools
import os.path
import re
import copy
import urllib.parse
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
    {
        "id": "gemus",
        "screenName": "Gemus",
        "dbTableName": "Games",
        "dbFieldName": "Gemus",
        "dbType": "Memo/Hyperlink (255)",
        "defaultWidth": 200,
        "sortable": True,
        "filterable": True,
        "textAlignment": "left",
    },
]

def usableColumn_getById(i_id):
    """
    Params:
     i_id:
      (str)

    Returns:
     Either (UsableColumn)
     or (None)
    """
    columns = [column  for column in g_usableColumns  if column["id"] == i_id]
    if len(columns) == 0:
        return None
    return columns[0]

def usableColumn_getByDbIdentifier(i_identifier):
    """
    Params:
     i_identifier:
      (str)
      A column name, with optional table name prefix.
      eg.
       "Name"
       "Games.Name"

    Returns:
     Either (UsableColumn)
     or (None)
    """
    parts = i_identifier.split(".", 1)
    if len(parts) == 1:
        for column in g_usableColumns:
            if column["filterable"] and column["dbFieldName"] == parts[0]:
                return column
    else:
        for column in g_usableColumns:
            if column["filterable"] and column["dbTableName"] == parts[0] and column["dbFieldName"] == parts[1]:
                return column
    return None


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
# (list of TableColumn)

# Type: TableColumn
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

def tableColumn_add(i_id, i_beforeColumnId=None):
    """
    Add a column to the live table view.

    Params:
     i_id:
      (str)
      ID of column to add to the table view.
      Details of it should exist in g_usableColumns.
     i_beforeColumnId:
      Either (str)
       ID of column already present in the table view to insert this column before.
      or (None)
       Add the new column as the last one.

    Returns:
     (TableColumn)
    """
    usableColumn = usableColumn_getById(i_id)
    newTableColumn = {
        "id": usableColumn["id"],
        "screenName": usableColumn["screenName"],
        "width": usableColumn["defaultWidth"],
        "sortable": usableColumn["sortable"],
        "filterable": usableColumn["filterable"]
    }
    if "textAlignment" in usableColumn:
        newTableColumn["textAlignment"] = usableColumn["textAlignment"]

    # Either append column at end or insert it before i_beforeColumnId
    if i_beforeColumnId == None:
        g_tableColumns.append(newTableColumn)
    else:
        g_tableColumns.insert(tableColumn_idToPos(i_beforeColumnId), newTableColumn)

    # Return the new table column
    return newTableColumn

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
    for sortOperationNo, sortOperation in enumerate(columnNameBar.sort_operations):
        if sortOperation[0] == i_id:
            foundSortOperationNo = sortOperationNo
            break
    if foundSortOperationNo != None:
        del(columnNameBar.sort_operations[foundSortOperationNo])
        columnNameBar.sort_updateGui()

def tableColumn_toggle(i_id, i_addBeforeColumnId=None):
    present = tableColumn_getById(i_id)
    if not present:
        tableColumn_add(i_id, i_addBeforeColumnId)
    else:
        tableColumn_remove(i_id)

def tableColumn_move(i_moveColumn, i_beforeColumn):
    """
    Move a column.

    Params:
     i_moveColumn:
      (TableColumn)
      Column to move.
     i_beforeColumn:
      Either (TableColumn)
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
     (list of TableColumn)
    """
    return g_tableColumns[i_startPos:i_endPos]

def tableColumn_getByPos(i_pos):
    """
    Get the object of the n'th column.

    Params:
     i_pos:
      (int)

    Returns:
     Either (TableColumn)
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
     Either (TableColumn)
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

def sqliteRowToDict(i_row):
    """
    Convert a sqlite3.Row object to a plain dict for easier viewing.

    Params:
     i_row:
      (sqlite3.Row)

    Returns:
     (dict)
    """
    return { keyName: i_row[keyName]  for keyName in i_row.keys() }

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
            rows = [sqliteRowToDict(row)  for row in rows]
            g_dbSchema[tableName] = rows

    # Get columns in Games table
    global g_db_gamesColumnNames
    g_db_gamesColumnNames = [row["name"]  for row in g_dbSchema["Games"]]

def closeDb():
    global g_db
    g_db.close()
    g_db = None

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


def getGameRecord(i_gameId, i_includeRelatedGameNames=False):
    """
    Params:
     i_gameId:
      (int)
     i_includeRelatedGameNames:
      (bool)
    """
    # From Games table, select all fields
    fromTerms = [
        "Games"
    ]

    selectTerms = [
    ]
    fullyQualifiedFieldNames = False
    if fullyQualifiedFieldNames:
        for field in g_dbSchema["Games"]:
            selectTerms.append("Games." + field["name"] + " AS [Games." + field["name"] + "]")
    else:
        selectTerms.append("Games.*")

    #
    if i_includeRelatedGameNames:
        gamesColumnNames = [row["name"]  for row in g_dbSchema["Games"]]
        if "CloneOf" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS CloneOf_Games ON Games.CloneOf = CloneOf_Games.GA_Id")
            selectTerms.append("CloneOf_Games.Name AS CloneOf_Name")
        if "Prequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Prequel_Games ON Games.Prequel = Prequel_Games.GA_Id")
            selectTerms.append("Prequel_Games.Name AS Prequel_Name")
        if "Sequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Sequel_Games ON Games.Sequel = Sequel_Games.GA_Id")
            selectTerms.append("Sequel_Games.Name AS Sequel_Name")
        if "Related" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Related_Games ON Games.Related = Related_Games.GA_Id")
            selectTerms.append("Related_Games.Name AS Related_Name")

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
        else:
            selectTerms.append(tableName + ".*")

    # Build SQL string
    #  SELECT
    sql = "SELECT " + ", ".join(selectTerms)
    #  FROM
    sql += "\nFROM " + " ".join(fromTerms)
    #  WHERE
    sql += "\nWHERE Games.GA_Id = " + str(i_gameId)

    # Execute
    g_db.row_factory = sqlite3.Row
    cursor = g_db.execute(sql)

    row = cursor.fetchone()
    row = sqliteRowToDict(row)
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
    rows = [sqliteRowToDict(row)  for row in rows]
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

# + Column name bar {{{

class ColumnNameBar(QWidget):
    """
    A row of buttons to act as table headings and controls for column resizing and sorting.
    """
    # Within this many pixels either side of a vertical boundary between header buttons, allow dragging to resize a column.
    resizeMargin = 10
    # Minimum number of pixels that a column can be resized to by dragging.
    minimumColumnWidth = 30

    headingButtonHeight = 30

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

            # + Context menu {{{

            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

            # + }}}

        # + Context menu {{{

        def onCustomContextMenuRequested(self, i_pos):
            # Get context menu invocation position (normally mouse position, but could also be centre of header button if pressed keyboard menu button) relative to the ColumnNameBar
            # and adjust for horizontal scroll amount
            invocationPos = self.mapTo(self.parent(), i_pos)
            invocationPos.setX(invocationPos.x() - self.parent().scrollX)
            # Get the specific column on which the context menu was invoked,
            # so if we end up showing any new columns, they can be inserted at that position
            contextColumn = self.parent()._columnAtPixelX(invocationPos.x())

            # Build popup menu
            class StayOpenMenu(QMenu):
                """
                A menu which stays open after something is selected
                so you can make multiple selections in one go.
                """
                def __init__(self, i_parent=None):
                    QMenu.__init__(self, i_parent)
                    self.installEventFilter(self)

                def eventFilter(self, i_watched, i_event):
                    if i_event.type() == QEvent.MouseButtonRelease:
                        if i_watched.activeAction():
                            # If the selected action does not have a submenu,
                            # trigger the function and eat the event
                            if not i_watched.activeAction().menu():
                                i_watched.activeAction().trigger()
                                return True
                    return QMenu.eventFilter(self, i_watched, i_event)
            contextMenu = StayOpenMenu(self)

            def action_onTriggered(i_selectedColumnId, i_contextMenuColumnId):
                tableColumn_toggle(i_selectedColumnId, i_contextMenuColumnId)

                # Update GUI
                # If the following recreateWidgets() call deletes the button which we right-clicked to open this context menu,
                # QT will subsequently segfault. To workaround this, use a one-shot zero-delay QTimer to continue at idle-time,
                # when apparently the context menu has been cleaned up and a crash does not happen.
                continueTimer = QTimer(self)
                continueTimer.setSingleShot(True)
                def on_continueTimer():
                    columnNameBar.recreateWidgets()
                    columnNameBar.repositionHeadingButtons()
                    columnNameBar.repositionTabOrder()
                    columnFilterBar.recreateWidgets()
                    columnFilterBar.repositionFilterEdits()
                    columnFilterBar.repositionTabOrder()

                    # Requery DB in case filter criteria have changed
                    refilterFromCurrentlyVisibleBar()
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
                action.triggered.connect(functools.partial(action_onTriggered, columnId, contextColumn["id"]))

            # Show popup menu
            contextMenu.popup(self.mapToGlobal(i_pos))
        #def mousePressEvent(self, i_event):
        #    if i_event.button() == Qt.MouseButton.RightButton:

        # + }}}


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
        #  Either (TableColumn)
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

        self.initFromColumns()

    def initFromColumns(self):
        # Create header buttons
        self.recreateWidgets()
        # Initially set all widget positions
        self.repositionHeadingButtons()
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
                headingButton = ColumnNameBar.HeadingButton(column["screenName"], column["filterable"], self)
                widgetDict["headingButton"] = headingButton
                # Set its fixed properties (apart from position)
                headingButton.setVisible(True)
                headingButton.clicked.connect(functools.partial(self.headingButton_onClicked, column["id"]))
                #  Filter events to facilitate drag resizing and scroll to upon focus,
                #  and for the former, receive mouse move events even if button isn't held down
                headingButton.installEventFilter(self)
                headingButton.setMouseTracking(True)

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

                # Remove object of header widgets
                del(self.columnWidgets[columnId])

    #def sizeHint(self):
    #    return QSize(10000, 59)

    # + Scrolling {{{

    def scroll(self, i_dx, i_dy):  # override from QWidget
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
        refilterFromCurrentlyVisibleBar()
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

    # + Mouse drag to resize/reorder columns {{{

    def _columnBoundaryNearPixelX(self, i_x, i_withinMargin=None):
        """
        Params:
         i_x:
          (int)
          Relative to the left of the header bar.
         i_withinMargin:
          Either (int)
           Require the resulting edge to be within this many pixels of i_x
          or (None)
           Get the nearest edge regardless of how far from i_x it is.

        Returns:
         Either (tuple)
          Tuple has elements:
           0:
            Either (TableColumn)
             The object of the visible column before the edge that i_x is nearest to
            or (None)
             There is no before the edge that i_x is nearest to (ie. it is the first edge).
           1:
            Either (TableColumn)
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
          Relative to the left of the header bar.

        Returns:
         Either (TableColumn)
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
          (TableColumn)

        Returns:
         Either (int)
          Relative to the left of the header bar.
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
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # If holding Shift
                if i_event.modifiers() & Qt.ShiftModifier:
                    self.reorder_column = self._columnAtPixelX(mousePos.x())
                    self.reorder_dropBeforeColumn = self.reorder_column

                    # Show drop indicator
                    self.reorderIndicator_widget.setGeometry(self._columnScreenX(self.reorder_column) + self.scrollX, 0, self.reorder_column["width"], ColumnNameBar.headingButtonHeight)
                    self.reorderIndicator_widget.show()
                    self.reorderIndicator_widget.raise_()

                    return True
                # Else if cursor is near a draggable vertical edge
                else:
                    leftColumn, rightColumn, edgeX = self._columnBoundaryNearPixelX(mousePos.x(), ColumnNameBar.resizeMargin)
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
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # Get new width
                newRightEdge = mousePos.x() + self.resize_mouseToEdgeOffset
                newWidth = newRightEdge - self.resize_columnLeftX
                if newWidth < ColumnNameBar.minimumColumnWidth:
                    newWidth = ColumnNameBar.minimumColumnWidth
                # Resize column
                self.resize_column["width"] = newWidth

                # Move/resize buttons and lineedits
                self.repositionHeadingButtons()
                columnFilterBar.repositionFilterEdits()
                #
                tableView.horizontalHeader().resizeSection(tableColumn_idToPos(self.resize_column["id"]), newWidth)

                return True

            # Else if currently reordering,
            # draw line at nearest vertical edge
            elif self.reorder_column != None:
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                #
                leftColumn, rightColumn, edgeX = self._columnBoundaryNearPixelX(mousePos.x())
                self.reorder_dropBeforeColumn = rightColumn
                if self.reorder_dropBeforeColumn == self.reorder_column:
                    self.reorderIndicator_widget.setGeometry(self._columnScreenX(self.reorder_column) + self.scrollX, 0, self.reorder_column["width"], ColumnNameBar.headingButtonHeight)
                else:
                    self.reorderIndicator_widget.setGeometry(edgeX - 3 + self.scrollX, 0, 6, self.height())

            # Else if not currently resizing or reordering,
            # then depending on whether cursor is near a draggable vertical edge,
            # set cursor shape
            else:
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                #
                leftColumn, _, _ = self._columnBoundaryNearPixelX(mousePos.x(), ColumnNameBar.resizeMargin)
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
                self.repositionTabOrder()
                columnFilterBar.repositionFilterEdits()
                columnFilterBar.repositionTabOrder()
                #
                tableView.requery()
                #
                tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])
                #self.reorderIndicator_widget.setFrameRect(QRect(edgeX - 2, 0, 4, 20))
                #self.reorderIndicator_widget.setFrameRect(QRect(2, 2, 50, 10))
                #print(leftColumn["id"], rightColumn["id"], edgeX)

                #
                return True

        elif i_event.type() == QEvent.FocusIn:
            # If this widget is off the side of the header bar / window,
            # scroll horizontally
            positionOnBar = i_watched.mapTo(self, QPoint(0, 0))
            if positionOnBar.x() < 0:
                tableView.scrollBy(positionOnBar.x(), 0)
            elif positionOnBar.x() + i_watched.geometry().width() > self.geometry().width():
                tableView.scrollBy(positionOnBar.x() + i_watched.geometry().width() - self.geometry().width(), 0)

        # Let event continue
        return False

    # + }}}

    # + Layout {{{

    def repositionHeadingButtons(self):
        x = 0
        x += self.scrollX  # Adjust for horizontal scroll amount
        y = 0
        for column in tableColumn_getBySlice():
            if column["filterable"]:
                self.columnWidgets[column["id"]]["headingButton"].setGeometry(x, y, column["width"], ColumnNameBar.headingButtonHeight)
            x += column["width"]

    def repositionTabOrder(self):
        previousWidget = None

        # For each heading button
        for column in tableColumn_getBySlice():
            if column["filterable"]:
                nextWidget = self.columnWidgets[column["id"]]["headingButton"]
                if previousWidget != None:
                    self.setTabOrder(previousWidget, nextWidget)
                previousWidget = nextWidget

    # + }}}

# + }}}

# + Column filter bar {{{

class ColumnFilterBar(QWidget):
    """
    One or more rows of text box controls for entering filter criteria per column.
    """
    filterRowHeight = 30

    # Emitted after the text in one of the filter text boxes is changed, or a row is deleted
    filterChange = Signal()

    class FilterEdit(QFrame):
        # Emitted after the text is changed
        textChange = Signal()

        def __init__(self, i_columnId, i_parent=None):
            QFrame.__init__(self, i_parent)

            self.columnId = i_columnId

            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setProperty("class", "FilterEdit")
            self.setAutoFillBackground(True)

            self.layout = QHBoxLayout(self)
            self.setLayout(self.layout)
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)

            self.lineEdit = QLineEdit(self)
            self.lineEdit.setFixedHeight(ColumnFilterBar.filterRowHeight)
            self.layout.addWidget(self.lineEdit)
            self.layout.setStretch(0, 1)
            self.lineEdit.editingFinished.connect(self.lineEdit_onEditingFinished)

            self.clearButton = QPushButton("", self)
            self.clearButton.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
            self.clearButton.setStyleSheet("QPushButton { margin: 4px; border-width: 1px; border-radius: 10px; }");
            #self.clearButton.setFlat(True)
            self.clearButton.setFixedHeight(ColumnFilterBar.filterRowHeight)
            self.clearButton.setFixedWidth(ColumnFilterBar.filterRowHeight)
            self.clearButton.setFocusPolicy(Qt.NoFocus)
            self.clearButton.setVisible(False)
            self.layout.addWidget(self.clearButton)
            self.layout.setStretch(1, 0)
            self.clearButton.clicked.connect(self.clearButton_onClicked)

            self.lineEdit.textEdited.connect(self.lineEdit_onTextEdited)

        # + Internal event handling {{{

        def lineEdit_onTextEdited(self, i_text):
            # Hide or show clear button depending on whether there's text
            self.clearButton.setVisible(i_text != "")

        def lineEdit_onEditingFinished(self):
            # If text was modified, requery,
            # else focus the tableview
            textWasModified = self.lineEdit.isModified()
            self.lineEdit.setModified(False)
            if textWasModified:
                self.textChange.emit()
            else:
                tableView.setFocus()
                tableView.selectCellInColumnWithId(self.columnId)

        def clearButton_onClicked(self):
            self.lineEdit.setText("")
            self.clearButton.setVisible(False)
            self.textChange.emit()

        # + }}}

        # + Text {{{

        def text(self):
            """
            Returns:
             (str)
            """
            return self.lineEdit.text()

        def setText(self, i_text):
            """
            Params:
             i_text:
              (str)
            """
            self.lineEdit.setText(i_text)
            self.lineEdit_onTextEdited(i_text)

        # + }}}

        # + Focus {{{

        def setFocus(self, i_reason):
            self.lineEdit.setFocus(i_reason)

        # + }}}


    def __init__(self, i_parent=None):
        QWidget.__init__(self, i_parent)

        # Allow this custom widget derived from a QWidget to be fully styled by stylesheets
        # https://stackoverflow.com/a/49179582
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.scrollX = 0
        self.scrollY = 0

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

        # Create header buttons
        self.recreateWidgets()

        #
        self.insertRow_pushButton = QPushButton("+", self)
        self.insertRow_pushButton.clicked.connect(self.insertRow_pushButton_onClicked)
        #  Filter events to facilitate scroll to upon focus
        self.insertRow_pushButton.installEventFilter(self)

        self.insertFilterRow(0)

    def initFromColumns(self):
        # Create filter edits
        self.recreateWidgets()
        # Initially set all widget positions
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

                # Create filter edits
                widgetDict["filterEdits"] = []
                for filterRowNo in range(0, len(self.filterRows)):
                    filterEdit = ColumnFilterBar.FilterEdit(column["id"], self)
                    widgetDict["filterEdits"].append(filterEdit)
                    # Set its fixed properties (apart from position)
                    filterEdit.setVisible(True)
                    filterEdit.textChange.connect(self.lineEdit_onTextChange)
                    #  Filter events to facilitate scroll to upon focus
                    filterEdit.lineEdit.installEventFilter(self)

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
        #  Filter events to facilitate scroll to upon focus
        deleteRow_pushButton.installEventFilter(self)
        # Save in member object
        newRow["deleteRow_pushButton"] = deleteRow_pushButton

        # Add per-column GUI widgets
        for columnNo, column in enumerate(tableColumn_getBySlice()):
            if column["filterable"]:
                # Create FilterEdit
                filterEdit = ColumnFilterBar.FilterEdit(column["id"], self)
                # Set its fixed properties (apart from position)
                filterEdit.setVisible(True)
                filterEdit.textChange.connect(self.lineEdit_onTextChange)
                #  Filter events to facilitate scroll to upon focus
                filterEdit.lineEdit.installEventFilter(self)
                # Save in member object
                self.columnWidgets[column["id"]]["filterEdits"].insert(i_position, filterEdit)

        # Resize bar to accommodate the current number of filter rows
        self.setFixedHeight(ColumnFilterBar.filterRowHeight * len(self.filterRows))

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

        # Resize bar to accommodate the current number of filter rows
        self.setFixedHeight(ColumnFilterBar.filterRowHeight * len(self.filterRows))

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
        for filterRowNo in range(0, len(self.filterRows)):
            self.clearFilterRow(filterRowNo)

        self.filterChange.emit()

    def resetFilterRowCount(self, i_rowCount, i_updateGui=True, i_requery=True):
        """
        Set count of filter rows and clear all their contents.
        """
        # If need to add filter rows
        if i_rowCount > len(self.filterRows):
            # Clear existing filter rows
            for filterRowNo in range(0, len(self.filterRows)):
                self.clearFilterRow(filterRowNo)

            # Add new rows
            while len(self.filterRows) < i_rowCount:
                self.appendFilterRow()

            #
            if i_updateGui:
                self.repositionFilterEdits()
                self.repositionTabOrder()

        # Else if need to remove filter rows
        elif i_rowCount < len(self.filterRows):
            # Remove them
            while len(self.filterRows) > i_rowCount:
                self.deleteFilterRow(len(self.filterRows) - 1)

            #
            if i_updateGui:
                self.repositionFilterEdits()  # for the insert row button

            # Clear remaining filter rows
            for filterRowNo in range(0, len(self.filterRows)):
                self.clearFilterRow(filterRowNo)

        # Else if already have the right number of filter rows
        else:
            # Clear them
            for filterRowNo in range(0, len(self.filterRows)):
                self.clearFilterRow(filterRowNo)

        #
        if i_requery:
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

    def lineEdit_onTextChange(self):
        self.filterChange.emit()

    def setFilterValues(self, i_oredRows):
        """
        Params:
         i_oredRows:
          (list)
          As returned from sqlWhereExpressionToColumnFilters().
        """
        self.resetFilterRowCount(max(len(i_oredRows), 1), False, False)

        for oredRowNo, oredRow in enumerate(i_oredRows):
            for andedFieldId, andedFieldValue in oredRow.items():
                # If table column doesn't exist (ie. is not visible)
                # then add it (ie. unhide it)
                if tableColumn_getById(andedFieldId) == None:
                    tableColumn_add(andedFieldId)

                # Set text in widget
                self.columnWidgets[andedFieldId]["filterEdits"][oredRowNo].setText(andedFieldValue)

    # + }}}

    def getSqlWhereExpression(self):
        """
        Returns:
         (str)
        """
        andGroups = []

        for filterRowNo in range(0, len(self.filterRows)):
            andTerms = []

            for column in tableColumn_getBySlice():
                usableColumn = usableColumn_getById(column["id"])
                if column["filterable"]:
                    value = self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].text()
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

                        # Else if a LIKE expression (contains an unescaped %)
                        elif value.replace("\\%", "").find("%") != -1:
                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerm = usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " LIKE " + value
                            if value.find("\\%") != -1:
                                andTerm += " ESCAPE '\\'"
                            andTerms.append(andTerm)

                        # Else if a plain string
                        else:
                            value = "%" + value + "%"

                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerms.append(usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"] + " LIKE " + value)

            if len(andTerms) > 0:
                andGroups.append(andTerms)

        if len(andGroups) > 0:
            return " OR ".join(["(" + andGroupStr + ")"  for andGroupStr in [" AND ".join(andGroup)  for andGroup in andGroups]])
        else:
            return ""

    # + Scrolling {{{

    def scroll(self, i_dx, i_dy):  # override from QWidget
        self.scrollX += i_dx
        self.scrollY += i_dy
        QWidget.scroll(self, i_dx, i_dy)

    def eventFilter(self, i_watched, i_event):
        #print(i_event.type())

        if i_event.type() == QEvent.FocusIn:
            # If this widget is off the side of the header bar / window,
            # scroll horizontally
            positionOnBar = i_watched.mapTo(self, QPoint(0, 0))
            if positionOnBar.x() < 0:
                tableView.scrollBy(positionOnBar.x(), 0)
            elif positionOnBar.x() + i_watched.geometry().width() > self.geometry().width():
                tableView.scrollBy(positionOnBar.x() + i_watched.geometry().width() - self.geometry().width(), 0)

        # Let event continue
        return False

    # + }}}

    # + Layout {{{

    def repositionFilterEdits(self):
        y = 0

        for filterRowNo, filterRow in enumerate(self.filterRows):
            x = 0
            x += self.scrollX  # Adjust for horizontal scroll amount
            for columnNo, column in enumerate(tableColumn_getBySlice()):
                if column["filterable"]:
                    self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].setGeometry(x, y, column["width"], ColumnFilterBar.filterRowHeight)
                x += column["width"]

            filterRow["deleteRow_pushButton"].setGeometry(x, y, ColumnFilterBar.filterRowHeight, ColumnFilterBar.filterRowHeight)
            x += ColumnFilterBar.filterRowHeight

            y += ColumnFilterBar.filterRowHeight

        y -= ColumnFilterBar.filterRowHeight
        self.insertRow_pushButton.setGeometry(x, y, ColumnFilterBar.filterRowHeight, ColumnFilterBar.filterRowHeight)

    def repositionTabOrder(self):
        previousWidget = None

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

    # + }}}

# + }}}

# + SQL filter bar {{{

class SqlFilterBar(QWidget):
    # Emitted after the text in the filter text box is changed
    filterChange = Signal()

    def __init__(self, i_parent=None):
        QWidget.__init__(self, i_parent)

        # Allow this custom widget derived from a QWidget to be fully styled by stylesheets
        # https://stackoverflow.com/a/49179582
        self.setAttribute(Qt.WA_StyledBackground, True)

        #
        self.lineEdit = QLineEdit(self)

        self.lineEdit.textChange.connect(self.lineEdit_onTextChange)

    def lineEdit_onTextChange(self):
        self.filterChange.emit()

    # + Focus {{{

    def setFocus(self, i_reason):
        self.lineEdit.setFocus(i_reason)

    # + }}}

# + }}}

# + Filter history {{{

g_filterHistory = [""]
g_filterHistory_pos = 1

def filterHistory_goBack():
    global g_filterHistory_pos

    # If already at start of history,
    # nothing to do
    if g_filterHistory_pos == 1:
        return

    #
    g_filterHistory_pos -= 1

    #
    sqlWhereExpression = g_filterHistory[g_filterHistory_pos - 1]

    # TODO if sql bar is visible update that instead
    oredRows = sqlWhereExpressionToColumnFilters(sqlWhereExpression)
    columnFilterBar.setFilterValues(oredRows)

    tableView.refilter(sqlWhereExpression)

def filterHistory_goForward():
    global g_filterHistory_pos

    # If already at end of history,
    # nothing to do
    if g_filterHistory_pos == len(g_filterHistory):
        return

    #
    g_filterHistory_pos += 1

    #
    sqlWhereExpression = g_filterHistory[g_filterHistory_pos - 1]

    # TODO if sql bar is visible update that instead
    oredRows = sqlWhereExpressionToColumnFilters(sqlWhereExpression)
    columnFilterBar.setFilterValues(oredRows)

    tableView.refilter(sqlWhereExpression)

# + }}}

# + Game table view {{{

class MyStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, i_parent=None):
        QStyledItemDelegate.__init__(self, i_parent)

    def initStyleOption(self, i_option, i_index):  # override from QStyledItemDelegate
        QStyledItemDelegate.initStyleOption(self, i_option, i_index)

        # Default selection colours
        i_option.palette.setColor(QPalette.Active, QPalette.Highlight, QColor.fromRgbF(0, 0, 0.75, 1))
        i_option.palette.setColor(QPalette.Inactive, QPalette.Highlight, QColor.fromRgbF(0.8125, 0.8125, 0.8125, 1))
        i_option.palette.setColor(QPalette.Active, QPalette.HighlightedText, QColor.fromRgbF(1, 1, 1, 1))
        i_option.palette.setColor(QPalette.Inactive, QPalette.HighlightedText, QColor.fromRgbF(0, 0, 0, 1))

    def paint(self, i_painter, i_option, i_index):  # override from QAbstractItemDelegate
        #print(i_painter, i_option, i_index)

        #if i_option.state & QStyle.State_Selected:
        #    i_painter.fillRect(i_option.rect, i_option.palette.highlight())

        column = tableColumn_getByPos(i_index.column())

        # Screenshot
        if column["id"] == "pic":
            screenshotPath = dbRow_getScreenshotRelativePath(self.parent().dbRows[i_index.row()])
            if screenshotPath != None:
                if hasattr(gamebase, "config_screenshotsBaseDirPath"):
                    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath)
                    i_painter.drawPixmap(i_option.rect, pixmap)
        elif column["id"] == "musician_photo":
            photoPath = dbRow_getPhotoRelativePath(self.parent().dbRows[i_index.row()])
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

    def rowCount(self, i_parent):  # override from QAbstractTableModel
        if self.parent().dbRows == None:
            return 0
        return len(self.parent().dbRows)

    def columnCount(self, i_parent):  # override from QAbstractTableModel
        return tableColumn_count()

    #https://stackoverflow.com/questions/7988182/displaying-an-image-from-a-qabstracttablemodel
    #https://forum.qt.io/topic/5195/qtableview-extra-column-space-solved/8
    def data(self, i_index, i_role):  # override from QAbstractTableModel
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
                if self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("Filename")] == None:
                    return ""
                return "▶"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Music
        elif column["id"] == "music":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                if self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("SidFilename")] == None:
                    return ""
                return "M"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Screenshot
        elif column["id"] == "pic":
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    screenshotPath = self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("ScrnshotFilename")]
            #    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath)
            #    return pixmap;
            pass
        #
        else:
            usableColumn = usableColumn_getById(column["id"])
            # Enum field
            if "type" in usableColumn and usableColumn["type"] == "enum":
                if i_role == MyTableModel.FilterRole:
                    return self.parent().dbRows[i_index.row()][usableColumn["dbFieldName"]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][usableColumn["dbFieldName"]]
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
                    return self.parent().dbRows[i_index.row()][usableColumn["dbFieldName"]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][usableColumn["dbFieldName"]]
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
                    return self.parent().dbRows[i_index.row()][usableColumn["dbFieldName"]]
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


class MyTableView(QTableView):
    def __init__(self, i_parent=None):
        QTableView.__init__(self, i_parent)

        # set font
        #font = QFont("Courier New", 14)
        #self.setFont(font)

        ## set column width to fit contents (set font first!)
        #self.resizeColumnsToContents()

        self.dbColumnNames = None
        #  (list of str)
        self.dbRows = None
        #  (list of tuple)

        # Create model and set it in the table view
        self.tableModel = MyTableModel(self)
        self.setModel(self.tableModel)

        self.setItemDelegate(MyStyledItemDelegate(self))

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

    def queryDb(self, i_whereExpression):
        """
        Params:
         i_whereExpression:
          (str)
        """
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
        #visibleDbNames = []
        #for tableColumn in tableColumn_getBySlice():
        #    usableColumn = usableColumn_getById(tableColumn["id"])
        #    if "dbTableName" in usableColumn and "dbFieldName" in usableColumn:
        #        visibleDbNames.append((usableColumn["dbTableName"], usableColumn["dbFieldName"]))

        for tableName, fieldName in visibleDbNames:
            fromTerms += getJoinTermsToTable(tableName, tableConnections)

            if tableName == "Games" and fieldName == "GA_Id":
                pass
            else:
                selectTerms.append(tableName + "." + fieldName)

        # SELECT
        sql = "SELECT " + ", ".join(selectTerms)
        sql += "\nFROM " + " ".join(fromTerms)

        # WHERE
        i_whereExpression = i_whereExpression.strip()
        if i_whereExpression != "":
            sql += "\nWHERE " + i_whereExpression

        # ORDER BY
        if len(columnNameBar.sort_operations) > 0:
            sql += "\nORDER BY "

            orderByTerms = []
            for columnId, direction in columnNameBar.sort_operations:
                usableColumn = usableColumn_getById(columnId)
                term = usableColumn["dbTableName"] + "." + usableColumn["dbFieldName"]
                if direction == -1:
                    term += " DESC"
                orderByTerms.append(term)
            sql += ", ".join(orderByTerms)

        # Execute
        #print(sql)
        cursor = g_db.execute(sql)

        self.dbColumnNames = [column[0]  for column in cursor.description]
        self.dbRows = cursor.fetchall()

        label_statusbar.setText("Showing " + str(len(self.dbRows)) + " games.")

    def selectedGameId(self):
        """
        Returns:
         (int)
        """
        selectedIndex = self.selectionModel().currentIndex()
        return self.dbRows[selectedIndex.row()][self.dbColumnNames.index("GA_Id")]

    def refilter(self, i_sqlWhereExpression):
        """
        Params:
         i_sqlWhereExpression:
          (str)

        Returns:
         (bool)
        """
        # Remember what game is currently selected and where on the screen the row is
        selectedIndex = self.selectionModel().currentIndex()
        if selectedIndex.row() < 0 or selectedIndex.row() >= len(self.dbRows):
            selectedGameId = None
        else:
            selectedGameId = self.selectedGameId()
            selectedRowTopY = self.rowViewportPosition(selectedIndex.row())

        # Query database
        sqlValid = True
        try:
            self.queryDb(i_sqlWhereExpression)
        except sqlite3.OperationalError as e:
            sqlValid = False

            import traceback
            print(traceback.format_exc())

            #messageBox = QMessageBox(QMessageBox.Critical, "Error", "")
            messageBox = MyMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
            messageBox.setText("<big><b>In SQL WHERE expression:</b></big>")
            messageBox.setInformativeText("\n".join(traceback.format_exception_only(e)))
            messageBox.resizeToContent()
            messageBox.exec()

        # Update table widget data
        self.requery()

        # If a game was previously selected,
        # search for new row number of that game
        # and if found, scroll to put that game in the same screen position it previously was
        if selectedGameId != None:
            idColumnNo = self.dbColumnNames.index("GA_Id")
            newDbRowNo = None
            for dbRowNo, dbRow in enumerate(self.dbRows):
                if dbRow[idColumnNo] == selectedGameId:
                    newDbRowNo = dbRowNo
                    break

            if newDbRowNo == None:
                self.scrollToTop()
            else:
                self.verticalScrollBar().setValue(self.rowHeight() * newDbRowNo - selectedRowTopY)
                self.selectionModel().setCurrentIndex(self.selectionModel().model().index(newDbRowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

        return sqlValid

    def requery(self):
        self.tableModel.modelReset.emit()

    def focusInEvent(self, i_event):  # override from QWidget
        # If don't have a selection, its row and column both showing up as -1
        # (which can happen eg. after a column is added or deleted),
        # select the top-left cell
        selectedIndex = self.selectionModel().currentIndex()
        if selectedIndex.row() == -1 and selectedIndex.column() == -1:
            selectedIndex = self.selectionModel().model().index(0, 0)
            self.selectionModel().setCurrentIndex(selectedIndex, QItemSelectionModel.ClearAndSelect)
        # Scroll to the selected cell
        self.scrollTo(selectedIndex)

    def selectCellInColumnWithId(self, i_id):
        """
        Params:
         i_id:
          (str)
        """
        columnNo = tableColumn_idToPos(i_id)
        selectedIndex = self.selectionModel().currentIndex()
        self.selectionModel().setCurrentIndex(self.selectionModel().model().index(selectedIndex.row(), columnNo), QItemSelectionModel.ClearAndSelect)

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
            detailPaneWasAlreadyVisible = detailPane_height() > 0
            detailPane_show()
            self.scrollTo(i_modelIndex, QAbstractItemView.PositionAtTop)
            gameId = self.dbRows[i_modelIndex.row()][self.dbColumnNames.index("GA_Id")]
            if gameId != detailPane_currentGameId:
                detailPane_populate(gameId)
            if i_keyboardOriented and detailPaneWasAlreadyVisible:
                detailPane_webEngineView.setFocus(Qt.OtherFocusReason)

        elif columnId == "play":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("GA_Id")]

            try:
                gamebase.runGame(self.dbRows[rowNo][self.dbColumnNames.index("Filename")],
                                 self.dbRows[rowNo][self.dbColumnNames.index("FileToRun")],
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
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("GA_Id")]

            try:
                gamebase.runMusic(self.dbRows[rowNo][self.dbColumnNames.index("SidFilename")],
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
            if "type" in usableColumn and usableColumn["type"] == "gameId":
                # Get the target game ID
                rowNo = i_modelIndex.row()
                gameId = self.dbRows[rowNo][self.dbColumnNames.index(usableColumn["dbFieldName"])]
                if gameId != 0:
                    self.selectGameWithId(gameId)

    def findGameWithId(self, i_id):
        idColumnNo = self.dbColumnNames.index("GA_Id")
        for rowNo, row in enumerate(self.dbRows):
            if row[idColumnNo] == i_id:
                return rowNo
        return None

    def selectGameWithId(self, i_gameId):
        # Look for row in table,
        # and if not found then clear filter and look again
        rowNo = self.findGameWithId(i_gameId)
        if rowNo == None:
            columnFilterBar.resetFilterRowCount(1)
            rowNo = self.findGameWithId(i_gameId)

        # If found, select it
        if rowNo != None:
            selectedIndex = self.selectionModel().currentIndex()
            self.selectionModel().setCurrentIndex(self.selectionModel().model().index(rowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

    def selectionChanged(self, i_selected, i_deselected):  # override from QAbstractItemView
        QTableView.selectionChanged(self, i_selected, i_deselected)

        # If detail pane is open,
        # repopulate it from the new row
        if detailPane_height() > 0:
            selectedIndex = self.selectionModel().currentIndex()
            if self.selectedGameId() != detailPane_currentGameId:
                detailPane_populate(self.selectedGameId())

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
            columnNameBar.appendFilterRow()
            columnNameBar.repositionTabOrder()
            columnFilterBar.repositionFilterEdits()
            columnFilterBar.repositionTabOrder()

        columnId = tableColumn_getByPos(selectedIndex.column())["id"]
        columnFilterBar.columnWidgets[columnId]["filterEdits"][-1].setText(formattedCriteria)
        columnFilterBar.filterChange.emit()

    # + }}}

    # + Scrolling {{{

    def scrollContentsBy(self, i_dx, i_dy):  # override from QAbstractScrollArea
        """
        Called whenever the table view is scrolled.
        """
        # Call base class to scroll the actual table view
        QTableView.scrollContentsBy(self, i_dx, i_dy)
        # Scroll external bars horizontally by the same amount
        columnNameBar.scroll(i_dx, 0)
        columnFilterBar.scroll(i_dx, 0)

    def scrollBy(self, i_dx, i_dy):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + i_dx)

    # + }}}

    def updateGeometries(self):  # override from QAbstractItemView
        # Increase the horizontal scrollbar's maximum to enable scrolling to the insert/delete filter row buttons 

        # Save initial scrollbar position to prevent jitter
        initialValue = self.horizontalScrollBar().value()

        #
        QTableView.updateGeometries(self)

        # Calculate and set new scrollbar maximum
        allColumnsWidth = sum([column["width"]  for column in tableColumn_getBySlice()])
        newMaximum = allColumnsWidth - self.horizontalScrollBar().pageStep() + ColumnFilterBar.filterRowHeight*2 + self.verticalScrollBar().width()
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

    def keyPressEvent(self, i_event):  # override from QWidget
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
        if self.verticalScrollMode() == QAbstractItemView.ScrollPerPixel:
            scrollY = self.verticalScrollBar().value()
        else: # if self.verticalScrollMode() == QAbstractItemView.ScrollPerItem:
            self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            scrollY = self.verticalScrollBar().value()
            self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

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
                    self.resize_scrollModeIsPerItem = self.verticalScrollMode() == QAbstractItemView.ScrollPerItem

                    # Remember where on the screen the row being resized is
                    #selectedIndex = self.selectionModel().currentIndex()
                    #self.resize_selectedRowId = self.dbRows[selectedIndex.row()][self.dbColumnNames.index("GA_Id")]
                    self.resize_selectedRowTopY = self.rowViewportPosition(rowNo)

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
    if sqlFilterBar.isVisible():
        sqlFilterBar.setFocus(Qt.ShortcutFocusReason)
    else:
        # If table view has the focus and the selected column is filterable,
        # target that
        selectedIndex = tableView.selectionModel().currentIndex()
        selectedColumn = tableColumn_getByPos(selectedIndex.column())
        if tableView.hasFocus() and selectedColumn != None and selectedColumn["filterable"]:
            targetColumn = selectedColumn
        # Else target the first visible and filterable column
        else:
            for column in tableColumn_getBySlice():
                if column["filterable"]:
                    targetColumn = column
                    break

        # Set focus to filter edit control
        if targetColumn != None:
            columnFilterBar.columnWidgets[targetColumn["id"]]["filterEdits"][0].setFocus(Qt.ShortcutFocusReason)
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

        if tableView.selectedGameId() != detailPane_currentGameId:
            detailPane_populate(self.selectedGameId())

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
#     columnNameBar
#     columnFilterBar
#     sqlFilterBar
#     tableView
#    detailPane
#   statusbar

# + Menu bar {{{

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

fileMenu = menuBar.addMenu("&File")
action = fileMenu.addAction("Open &database in external program")
action.triggered.connect(menu_file_openDatabaseInExternalProgram_onTriggered)
fileMenu.addAction("New")
fileMenu.addAction("Open")
fileMenu.addAction("Save")
fileMenu.addSeparator()
fileMenu.addAction("Quit")

editMenu = menuBar.addMenu("&Edit")
editMenu.addAction("Copy")

import sql

def interpretColumnOperation(i_node):
    """
    Params:
     i_node:
      (dict)

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (str)
       Operator name
       eg.
        "="
        "LIKE"
      1:
       (str)
       DB column identifier
       eg.
        "Games.Name"
        "Name"
      2:
       (str)
       Value
       eg.
        "Uridium"
        "Uri%"
    """
    if type(i_node) != dict or "op" not in i_node:
        return None, None, None
    operator = i_node["op"][1]

    columnName = None
    value = None
    for child in i_node["children"]:
        if type(child) == dict:
            if "op" in child and child["op"] == ("operator", "ESCAPE"):
                value = child["children"][0][1]  # TODO unescape?
            elif operator == "BETWEEN" and child["op"] == ("operator", "AND"):
                value = child["children"][0][1] + "~" + child["children"][1][1]
            else:
                return None, None, None
        elif type(child) == tuple:
            if child[0] == "identifier":
                if columnName != None:
                    return None, None, None
                columnName = child[1]
            else:
                if value != None:
                    return None, None, None
                value = child[1]

    if operator == None or columnName == None or value == None:
        return None, None, None
    return operator, columnName, value

def sqlWhereExpressionToColumnFilters(i_whereExpression):
    """
    Convert SQL text to per-column filter values

    Params:
     i_sqlWhereExpression:
      (str)

    Returns:
     (list)
     An element for each 'row' of filter edits in the UI.
     Each element is:
      (dict with arbitrary key-value properties)
      The filter UI text for a particular column.
      Dict has:
       Keys:
        (str)
        ID of column
       Value:
        (str)
        Text for the filter box.
    """
    # Tokenize, parse and postprocess it
    tokenized = sql.tokenizeWhereExpr(i_whereExpression)
    if len(tokenized) == 0:
        return []
    sql.initializeOperatorTable()
    parsed = sql.parseExpression(tokenized)
    #print(parsed)
    if parsed == None:
        statusbar.setText("failed to parse")
        return []
    parsed = sql.flattenOperator(parsed, "AND")
    parsed = sql.flattenOperator(parsed, "OR")
    #pprint.pprint(parsed)

    # Get or construct a top-level OR array from the input parse tree
    if parsed["op"] == ("operator", "OR"):
        orExpressions = parsed["children"]
    else:
        orExpressions = [parsed]

    # Initialize a top-level OR array for output,
    # and then for every input OR expression
    oredRows = []
    for orExpressionNo, orExpression in enumerate(orExpressions):

        # Get or construct a second-level AND array from the input parse tree
        if orExpression["op"] == ("operator", "AND"):
            andExpressions = orExpression["children"]
        else:
            andExpressions = [orExpression]

        # Initialize a second-level AND dict for output,
        # and then for every input AND expression
        andedFields = {}
        for andExpression in andExpressions:
            operator, columnName, value = interpretColumnOperation(andExpression)
            #print("operator, columnName, value: " + str((operator, columnName, value)))
            #if columnName != None:
            usableColumn = usableColumn_getByDbIdentifier(columnName)
            if usableColumn != None:
                widgetText = None
                if operator == "LIKE":
                    # If have percent sign at beginning and end and nowhere else
                    if len(value) >= 2 and value[0] == "%" and value[-1] == "%" and value[1:-1].find("%") == -1:
                        widgetText = value[1:-1]
                    else:
                        widgetText = value
                elif operator == "REGEXP":
                    widgetText = "/" + value + "/"
                elif operator == "BETWEEN":
                    widgetText = value
                elif operator == "IS":
                    widgetText = "=" + value
                elif operator == "IS NOT":
                    widgetText = "<>" + value
                elif operator == "=" or operator == "==":
                    widgetText = "=" + value
                elif operator == "<":
                    widgetText = "<" + value
                elif operator == "<=":
                    widgetText = "<=" + value
                elif operator == ">":
                    widgetText = ">" + value
                elif operator == ">=":
                    widgetText = ">=" + value
                elif operator == "<>" or operator == "!=":
                    widgetText = "<>" + value

                # Save widget text in output dict
                if widgetText != None:
                    andedFields[usableColumn["id"]] = widgetText

        #
        oredRows.append(andedFields)

    return oredRows

def filterFormat_perColumn():
    # Show column filter bar instead of SQL filter bar
    columnFilterBar.show()
    sqlFilterBar.hide()

    # Convert SQL text to per-column filters
    # and set it in the per-column widgets

    # Get the expression text
    whereExpression = sqlFilterBar.text().strip()

    #
    oredRows = sqlWhereExpressionToColumnFilters(whereExpression)
    columnFilterBar.setFilterValues(oredRows)

    columnFilterBar.repositionFilterEdits()
    columnFilterBar.repositionTabOrder()
    columnFilterBar.filterChange.emit()

def filterFormat_sql():
    # Show SQL filter bar instead of column filter bar
    columnFilterBar.hide()
    sqlFilterBar.show()

    # Convert per-column filters to SQL text
    # and set it in the SQL widget
    sqlWhereExpression = columnFilterBar.getSqlWhereExpression()
    sqlFilterBar.setText(sqlWhereExpression)

filterMenu = menuBar.addMenu("F&ilter")

#filterMenu.addSection("Go")
filterMenu_back_action = filterMenu.addAction("Go &back")
filterMenu_back_action.triggered.connect(filterHistory_goBack)
filterMenu_forward_action = filterMenu.addAction("Go &forward")
filterMenu_forward_action.triggered.connect(filterHistory_goForward)

filterMenu.addSeparator()

actionGroup = QActionGroup(filterMenu)
actionGroup.setExclusive(True)
filterMenu_filterFormat_perColumn_action = filterMenu.addAction("Edit per-&column")
filterMenu_filterFormat_perColumn_action.setCheckable(True)
filterMenu_filterFormat_perColumn_action.setChecked(True)
filterMenu_filterFormat_perColumn_action.triggered.connect(filterFormat_perColumn)
actionGroup.addAction(filterMenu_filterFormat_perColumn_action)
#filterMenu_separator = filterMenu.addAction("sep")
#filterMenu_separator.setSeparator(True)
filterMenu_filterFormat_sql_action = filterMenu.addAction("Edit as &SQL")
filterMenu_filterFormat_sql_action.setCheckable(True)
filterMenu_filterFormat_sql_action.triggered.connect(filterFormat_sql)
actionGroup.addAction(filterMenu_filterFormat_sql_action)
#filterMenu.addAction(actionGroup)
#menuBar.addMenu("View")
#menuBar.addMenu("Help")

filterMenu.addSeparator()

filterMenu_filterFormat_copySql_action = filterMenu.addAction("C&opy SQL")

viewMenu = menuBar.addMenu("&View")
viewMenu_toolbar_action = viewMenu.addAction("&Toolbar")
viewMenu_toolbar_action.setCheckable(True)
viewMenu_toolbar_action.setChecked(True)

viewMenu.addSeparator()

#viewMenu_splitMenu = QMenu("&Split")
#viewMenu_toolbar_action = viewMenu.addMenu(viewMenu_splitMenu)
viewMenu_horizontalAction = viewMenu.addAction("Split &horizontally")
viewMenu_horizontalAction.setCheckable(True)
viewMenu_horizontalAction.setChecked(True)
viewMenu_verticalAction = viewMenu.addAction("Split &vertically")
viewMenu_verticalAction.setCheckable(True)
actionGroup = QActionGroup(filterMenu)
actionGroup.setExclusive(True)
actionGroup.addAction(viewMenu_horizontalAction)
actionGroup.addAction(viewMenu_verticalAction)

# + }}}

# + Toolbar {{{

toolbar = QToolBar()
toolbar_back_action = toolbar.addAction(QIcon(application.style().standardIcon(QStyle.SP_ArrowLeft)), "Back")
toolbar_back_action.triggered.connect(filterHistory_goBack)
toolbar_forward_action = toolbar.addAction(QIcon(application.style().standardIcon(QStyle.SP_ArrowRight)), "Forward")
toolbar_forward_action.triggered.connect(filterHistory_goForward)
mainWindow_layout.addWidget(toolbar)

# + }}}

# Create splitter
splitter = QSplitter(Qt.Vertical)
mainWindow_layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# + Game table {{{

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

# + }}}

def splitter_onSplitterMoved(i_pos, i_index):
    # If detail pane has been dragged closed,
    # call detailPane_hide() to keep track
    if splitter.sizes()[1] == 0:
        detailPane_hide()
splitter.splitterMoved.connect(splitter_onSplitterMoved)

# + Column name bar {{{

columnNameBar = ColumnNameBar()
columnNameBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
columnNameBar.setFixedHeight(30)
gameTable_layout.addWidget(columnNameBar)

# + }}}

class MyMessageBox(QDialog):
    def __init__(self, i_icon, i_title, i_text, i_buttons=QDialogButtonBox.Ok, i_parent=None, i_windowFlags=Qt.Dialog):
        """
        Params:
         i_icon:
          Either (QMessageBox.Icon)
           eg.
            self.style().standardIcon(QStyle.SP_MessageBoxCritical)
          or (None)
         i_title:
          (str)
         i_text:
          (str)
         i_buttons:
          (QMessageBox.StandardButtons)
         i_parent:
          (QWidget)
         i_windowFlags:
          (Qt.WindowFlags)
        """
        QDialog.__init__(self, i_parent, i_windowFlags)

        self.layout = QGridLayout(self)

        self.iconLabel = QLabel(self)
        self.layout.addWidget(self.iconLabel, 0, 0, 2, 1, Qt.AlignTop)
        if i_icon != None:
           self.iconLabel.setPixmap(i_icon.pixmap(128, 128))

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label, 0, 2, Qt.AlignTop)
        #2, 0: <PySide2.QtWidgets.QLabel(0x55f631f52a30, name="qt_msgbox_label") at 0x7fc7814ecf40>
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard|Qt.TextSelectableByKeyboard)

        self.informativeLabel = QLabel(self)
        self.informativeLabel.setWordWrap(True)
        self.layout.addWidget(self.informativeLabel, 1, 2, Qt.AlignTop)
        #2, 1: <PySide2.QtWidgets.QLabel(0x55f632830ea0, name="qt_msgbox_informativelabel") at 0x7fc7814ecfc0>
        self.informativeLabel.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard|Qt.TextSelectableByKeyboard)

        self.buttons = QDialogButtonBox(i_buttons, self)
        self.layout.addWidget(self.buttons, 2, 0, 1, 3)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 0)

        self.setWindowTitle(i_title)
        self.setText(i_text)

    def resizeToContent(self):
        # Get dimensions of screen
        # and choose the margin we want to keep from the edge
        screen = QGuiApplication.primaryScreen()
        screenGeometry = screen.geometry()
        screenEdgeMargin = 100

        # Get dimensions of text when unwrapped
        labelFontMetrics = QFontMetrics(self.label.property("font"))
        labelWidth = labelFontMetrics.horizontalAdvance(self.label.text())
        informativeLabelFontMetrics = QFontMetrics(self.informativeLabel.property("font"))
        informativeLabelWidth = informativeLabelFontMetrics.horizontalAdvance(self.informativeLabel.text())

        #
        layoutContentsMargins = self.layout.contentsMargins()
        layoutSpacing = self.layout.spacing()

        #
        contentWidth = layoutContentsMargins.left() + self.layout.itemAtPosition(0, 0).geometry().width() + layoutSpacing + max(labelWidth, informativeLabelWidth) + layoutContentsMargins.right()
        if contentWidth > screenGeometry.width() - screenEdgeMargin:
            contentWidth = screenGeometry.width() - screenEdgeMargin

        #
        labelBoundingRect = labelFontMetrics.boundingRect(0, 0, contentWidth, screenGeometry.height() - screenEdgeMargin, Qt.TextWordWrap | Qt.TextExpandTabs, self.label.text(), 4);
        informativeLabelBoundingRect = informativeLabelFontMetrics.boundingRect(0, 0, contentWidth, screenGeometry.height() - screenEdgeMargin, Qt.TextWordWrap | Qt.TextExpandTabs, self.informativeLabel.text(), 4);
        contentHeight = layoutContentsMargins.top() + labelBoundingRect.height() + layoutSpacing + informativeLabelBoundingRect.height() + layoutSpacing + self.buttons.height() + layoutContentsMargins.bottom()
        if contentHeight > screenGeometry.height() - screenEdgeMargin:
            contentHeight = screenGeometry.height() - screenEdgeMargin

        #
        self.resize(contentWidth, contentHeight)

    """
    def resizeEvent(self, event):
        _result = super().resizeEvent(event)
        print("---")
        print(str(self.label.width()) + ", " + str(self.label.height()))
        print(str(self.iconLabel.width()) + ", " + str(self.label.height()))
        print(str(self.buttons.width()) + ", " + str(self.label.height()))

        self.setFixedWidth(self._width)

        _text_box = self.findChild(QTextEdit)
        if _text_box is not None:
            # get width
            _width = int(self._width - 50)  # - 50 for border area
            # get box height depending on content
            _font = _text_box.document().defaultFont()
            _fontMetrics = QFontMetrics(_font)
            _textSize = _fontMetrics.size(0, details_box.toPlainText(), 0)
            _height = int(_textSize.height()) + 30  # Need to tweak
            # set size
            _text_box.setFixedSize(_width, _height)
    """

    def setText(self, i_text):
        self.label.setText(i_text)

    def setInformativeText(self, i_text):
        self.informativeLabel.setText(i_text)

def refilterFromCurrentlyVisibleBar():
    if columnFilterBar.isVisible():
        sqlWhereExpression = columnFilterBar.getSqlWhereExpression()
    else: #if columnFilterBar.isVisible():
        sqlWhereExpression = sqlFilterBar.text()

    tableView.refilter(sqlWhereExpression)

# + Column filter bar {{{

columnFilterBar = ColumnFilterBar()
columnFilterBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
gameTable_layout.addWidget(columnFilterBar)

def columnFilterBar_onFilterChange():
    sqlWhereExpression = columnFilterBar.getSqlWhereExpression()
    if not tableView.refilter(sqlWhereExpression):
        return

    # If expression is different from the last history item at the current position,
    # truncate history at current position and append new item
    global g_filterHistory
    global g_filterHistory_pos
    if g_filterHistory[g_filterHistory_pos - 1] != sqlWhereExpression:
        del(g_filterHistory[g_filterHistory_pos:])
        g_filterHistory.append(sqlWhereExpression)
        g_filterHistory_pos += 1

columnFilterBar.filterChange.connect(columnFilterBar_onFilterChange)

# + }}}

# + SQL filter bar {{{

#sqlFilterBar = SqlFilterBar()
sqlFilterBar = ColumnFilterBar.FilterEdit("")
sqlFilterBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
sqlFilterBar.setFixedHeight(30)
sqlFilterBar.hide()
gameTable_layout.addWidget(sqlFilterBar)

def sqlFilterBar_onTextChange():
    sqlWhereExpression = sqlFilterBar.text()
    if not tableView.refilter(sqlWhereExpression):
        return

    # If expression is different from the last history item at the current position,
    # truncate history at current position and append new item
    global g_filterHistory
    global g_filterHistory_pos
    if g_filterHistory[g_filterHistory_pos - 1] != sqlWhereExpression:
        del(g_filterHistory[g_filterHistory_pos:])
        g_filterHistory.append(sqlWhereExpression)
        g_filterHistory_pos += 1
sqlFilterBar.textChange.connect(sqlFilterBar_onTextChange)

# + }}}

# + Table view {{{

# Create table
tableView = MyTableView()
gameTable_layout.addWidget(tableView)
# Set vertical size policy to 'Ignored' which lets widget shrink to zero
#  https://stackoverflow.com/questions/18342590/setting-qlistwidget-minimum-height
tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

#  Set initial column widths
tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])

# + }}}

# + Detail pane {{{

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
    topPaneHeight = columnNameBar.geometry().height() + columnFilterBar.geometry().height() + tableView.rowHeight()
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
def detailPane_populate(i_gameId):
    """
    Params:
     i_gameId:
      (int)
    """
    gameRow = getGameRecord(i_gameId, True)

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

    # If there are related games,
    # insert links to the originals
    if "CloneOf_Name" in gameRow and gameRow["CloneOf_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Clone of: '
        html += '<a href="game:///' + str(gameRow["CloneOf"]) + '">' + gameRow["CloneOf_Name"] + '</a>'
        html += '</p>'

    if "Prequel_Name" in gameRow and gameRow["Prequel_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Prequel: '
        html += '<a href="game:///' + str(gameRow["Prequel"]) + '">' + gameRow["Prequel_Name"] + '</a>'
        html += '</p>'

    if "Sequel_Name" in gameRow and gameRow["Sequel_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Sequel: '
        html += '<a href="game:///' + str(gameRow["Sequel"]) + '">' + gameRow["Sequel_Name"] + '</a>'
        html += '</p>'

    if "Related_Name" in gameRow and gameRow["Related_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Related: '
        html += '<a href="game:///' + str(gameRow["Related"]) + '">' + gameRow["Related_Name"] + '</a>'
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
    if "WebLink_Name" in gameRow and gameRow["WebLink_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'

        html += gameRow["WebLink_Name"] + ": "
        url = gameRow["WebLink_URL"]
        html += '<a href="' + url + '">'
        html += url
        html += '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #    electron.shell.openExternal(this.href);
        #});

        # If it's a World Of Spectrum link then insert a corresponding Spectrum Computing link
        if gameRow["WebLink_Name"] == "WOS":
            # Separator
            html += '<span style="margin-left: 8px; margin-right: 8px; border-left: 1px dotted #666;"></span>'
            # Label
            html += 'Spectrum Computing: '
            # Link
            url = url.replace("http://www.worldofspectrum.org/infoseekid.cgi?id=", "https://spectrumcomputing.co.uk/entry/")
            html += '<a href="' + url + '">'
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

    #print(html)

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
                    extraPath = urllib.parse.unquote(extraPath)
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
                # If it's a link to a game,
                # select it in the table view
                elif url.startswith("game:///"):
                    gameId = url[8:]
                    gameId = urllib.parse.unquote(gameId)
                    gameId = int(gameId)
                    tableView.selectGameWithId(gameId)
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
            label_statusbar.setText("Showing " + str(len(tableView.dbRows)) + " games.")
        else:
            label_statusbar.setText(i_url)
    webEnginePage.linkHovered.connect(webEnginePage_onLinkHovered)

    # Load web engine page into the web engine view
    #webEnginePage.setView(detailPane_webEngineView)
    detailPane_webEngineView.setPage(webEnginePage)

# + }}}

# + Statusbar {{{

# Create statusbar
label_statusbar = QLabel()
label_statusbar.setProperty("class", "statusbar")
#mainWindow_layout.addSpacing(8)
mainWindow_layout.addWidget(label_statusbar)
label_statusbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
label_statusbar.setContentsMargins(8, 8, 8, 8)

# + }}}

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

columnNameBar.initFromColumns()
columnFilterBar.initFromColumns()
refilterFromCurrentlyVisibleBar()
tableView.requery()
tableView.resizeAllColumns([column["width"]  for column in tableColumn_getBySlice()])

columnNameBar.sort("name", False)  # TODO what if name column is initially not visible

tableView.selectionModel().setCurrentIndex(tableView.selectionModel().model().index(0, 0), QItemSelectionModel.ClearAndSelect)

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

    def setVisible(self, i_visible):  # override from QWidget
        QPlainTextEdit.setVisible(self, i_visible)
        if i_visible:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()

    def updateText(self):
        if len(utils.tasks) > 0:
            selectionStartPos = self.textCursor().selectionStart()
            selectionEndPos = self.textCursor().selectionEnd()

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

            textCursor = self.textCursor()
            textCursor.setPosition(selectionStartPos)
            textCursor.setPosition(selectionEndPos, QTextCursor.KeepAnchor)
            self.setTextCursor(textCursor)
        else:
            self.setPlainText("")

subprocessOutput_log = None
def menu_file_showSubprocessOutput_onTriggered(i_checked):
    global subprocessOutput_log
    if subprocessOutput_log == None:
        subprocessOutput_log = Log()

    subprocessOutput_log.show()

action = fileMenu.addAction("Show subprocess &output")
action.triggered.connect(menu_file_showSubprocessOutput_onTriggered)

# + }}}

# Enter Qt application main loop
exitCode = application.exec_()
sys.exit(exitCode)
