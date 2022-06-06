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
import json
import pprint

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras
import columns
import frontend_utils
import frontend
import utils
import sql_filter_bar


# + Parse command line {{{

COMMAND_NAME = "PyGamebase"

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


# Load frontend config settings
g_frontendSettings = {}
settingsFilePath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation) + os.sep + "pyGamebase.json"
if os.path.exists(settingsFilePath):
    try:
        with open(settingsFilePath, "rb") as f:
            g_frontendSettings = json.loads(f.read().decode("utf-8"))
    except Exception as e:
        import traceback
        print("Failed to read frontend settings file: " + "\n".join(traceback.format_exception_only(e)))

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
        messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
        messageBox.setText("<big><b>Missing config setting:</b></big>")
        messageBox.setInformativeText("config_databaseFilePath")
        messageBox.resizeToContent()
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
        messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
        messageBox.setText("<big><b>When opening database file:</b></big>")
        messageBox.setInformativeText("With path:\n" + gamebase.config_databaseFilePath + "\n\nAn error occurred:\n" + "\n".join(traceback.format_exception_only(e)))
        messageBox.resizeToContent()
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

    # Get info about tables
    g_db.row_factory = sqlite3.Row
    global g_dbSchema
    for tableName in ["Games", "Years", "Genres", "PGenres", "Publishers", "Developers", "Programmers", "Languages", "Crackers", "Artists", "Licenses", "Rarities", "Musicians"]:
        if tableName in dbTableNames:
            cursor = g_db.execute("PRAGMA table_info(" + tableName + ")")
            rows = cursor.fetchall()
            rows = [sqliteRowToDict(row)  for row in rows]
            g_dbSchema[tableName] = rows

    # Only use the columns that the database actually has
    columns.filterColumnsByDb(dbTableNames, g_dbSchema)

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

    Returns:
     (dict)
    """
    # From Games table, select all fields
    fromTerms = [
        "Games"
    ]

    selectTerms = [
    ]
    fullyQualifiedFieldNames = True
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
        screenshotRelativePath = i_row["Games.ScrnshotFilename"]
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
        photoRelativePath = i_row["Musicians.Photo"]
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

            # Inform the table columns menu of the column
            # and pop it up
            viewMenu_tableColumnsMenu.context = contextColumn["id"]
            viewMenu_tableColumnsMenu.popup(self.mapToGlobal(i_pos))

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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
            column = columns.tableColumn_getById(columnId)
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
        clickedColumn = columns.tableColumn_getById(i_columnId)

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

        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
        tableColumns = columns.tableColumn_getBySlice()
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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
                tableView.horizontalHeader().resizeSection(columns.tableColumn_idToPos(self.resize_column["id"]), newWidth)

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

                # Move drop indicator
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
                    columns.tableColumn_move(self.reorder_column, self.reorder_dropBeforeColumn)

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
                tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])
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
        for column in columns.tableColumn_getBySlice():
            if column["filterable"]:
                self.columnWidgets[column["id"]]["headingButton"].setGeometry(x, y, column["width"], ColumnNameBar.headingButtonHeight)
            x += column["width"]

    def repositionTabOrder(self):
        previousWidget = None

        # For each heading button
        for column in columns.tableColumn_getBySlice():
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

    class FilterEdit(qt_extras.LineEditWithClearButton):
        def __init__(self, i_columnId, i_parent=None):
            qt_extras.LineEditWithClearButton.__init__(self, ColumnFilterBar.filterRowHeight, i_parent)

            self.columnId = i_columnId

            self.lineEdit.editingFinished.connect(self.lineEdit_onEditingFinished)

        # + Internal event handling {{{

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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
            column = columns.tableColumn_getById(columnId)
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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
        for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
            if column["filterable"]:
                self.columnWidgets[column["id"]]["filterEdits"][i_position].setText("")

    # [not currently used]
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
                if columns.tableColumn_getById(andedFieldId) == None:
                    columns.tableColumn_add(andedFieldId)

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

            for column in columns.tableColumn_getBySlice():
                usableColumn = columns.usableColumn_getById(column["id"])
                if column["filterable"]:
                    value = self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].text()
                    value = value.strip()
                    if value != "":
                        # If range operator
                        betweenValues = value.split("~")
                        if len(betweenValues) == 2 and stringLooksLikeNumber(betweenValues[0]) and stringLooksLikeNumber(betweenValues[1]):
                            andTerms.append(usableColumn["dbIdentifiers"][0] + " BETWEEN " + betweenValues[0] + " AND " + betweenValues[1])

                        # Else if regular expression
                        elif len(value) > 2 and value.startswith("/") and value.endswith("/"):
                            # Get regexp
                            value = value[1:-1]

                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerms.append(usableColumn["dbIdentifiers"][0] + " REGEXP " + value)
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
                            andTerms.append(usableColumn["dbIdentifiers"][0] + " " + operator + " " + value)

                        # Else if a LIKE expression (contains an unescaped %)
                        elif value.replace("\\%", "").find("%") != -1:
                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerm = usableColumn["dbIdentifiers"][0] + " LIKE " + value
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
                            andTerms.append(usableColumn["dbIdentifiers"][0] + " LIKE " + value)

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
            for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
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
            for column in columns.tableColumn_getBySlice():
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

    # Set text in UI
    if sqlFilterBar.isVisible():
        sqlFilterBar.setText(sqlWhereExpression)
    else:
        oredRows = sqlWhereExpressionToColumnFilters(sqlWhereExpression)
        columnFilterBar.setFilterValues(oredRows)

    # Refilter
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

    # Set text in UI
    if sqlFilterBar.isVisible():
        sqlFilterBar.setText(sqlWhereExpression)
    else:
        oredRows = sqlWhereExpressionToColumnFilters(sqlWhereExpression)
        columnFilterBar.setFilterValues(oredRows)

    # Refilter
    tableView.refilter(sqlWhereExpression)

# + }}}

# + Game table view {{{

# + + dan/math/Rect2.js {{{

def fitLetterboxed(i_rect, i_container, i_align=0.5):
    """
    Reposition and (without changing its aspect ratio) resize a rectangle
    to fit fully inside a container rectangle with letterboxing,
    ie. one pair of this rectangle's opposing edges will touch the container's edges precisely,
    such that the other pair of this rectangle's opposing edges will lie inside the container's
    edges leaving some unused 'black borders' space.

    Params:
     i_rect:
      (dict)
      The rectangle to fit. [Is really only the aspect ratio used here?...]
      Dictionary has specific properties:
       x, y, width, height:
        (float)
     i_container:
      (dict)
      The rectangle to fit i_rect within.
      Dictionary has specific properties:
       x, y, width, height:
        (float)
     i_align:
      Either (float)
       How to align the resulting rectangle in the underfitting dimension;
       or in other words, the relative size of the letterbox borders.
       0.5:
        align in centre; make both borders the same size
       0:
        align at left or top; make the left or top border zero and the opposite
        border full size
       1:
        align at right or bottom; make the right or bottom border zero and the
        opposite border full size
      or (None)
       Use default of 0.5.

    Returns:
     (dict)
     Dictionary has specific properties:
      x, y, width, height:
       (float)
    """
    # Find the scaling required to make the horizontal edges fit exactly,
    # and the vertical edges fit exactly
    requiredHorizontalScale = float(i_container["width"]) / float(i_rect["width"])
    requiredVerticalScale = float(i_container["height"]) / float(i_rect["height"])
    # Use the smaller of the two
    if requiredHorizontalScale < requiredVerticalScale:
        i_rect["left"] = i_container["left"]
        i_rect["width"] = i_container["width"]
        combinedBorderSize = i_container["height"] - i_rect["height"] * requiredHorizontalScale
        i_rect["top"] = i_container["top"] + i_align * combinedBorderSize
        i_rect["height"] = i_container["height"] - combinedBorderSize
    else:
        i_rect["top"] = i_container["top"]
        i_rect["height"] = i_container["height"]
        combinedBorderSize = i_container["width"] - i_rect["width"] * requiredVerticalScale
        i_rect["left"] = i_container["left"] + i_align * combinedBorderSize
        i_rect["width"] = i_container["width"] - combinedBorderSize

    return i_rect

def fitPanned(i_rect, i_container, i_align=0.5):
    """
    Reposition and (without changing its aspect ratio) resize a rectangle
    to fit inside a container rectangle with panning,
    ie. one pair of this rectangle's opposing edges will touch the container's edges precisely,
    such that the other pair of this rectangle's opposing edges will lie outside the container's
    edges causing some of the rectangle to be cropped by the container.

    Params:
     i_rect:
      (dict)
      The rectangle to fit.
      Dictionary has specific properties:
       x, y, width, height:
        (float)
     i_container:
      (dict)
      The rectangle to fit i_rect within.
      Dictionary has specific properties:
       x, y, width, height:
        (float)
     i_align:
      Either (float)
       How to align the resulting rectangle in the overfitting dimension;
       or in other words, the relative size of the cropped areas.
       0.5:
        align in centre; crop equal amounts on both sides
       0:
        align at / pan to left or top;
        crop nothing from the left or top and crop fully from the right or bottom
       1:
        align at / pan to right or bottom;
        crop nothing from the right or bottom and crop fully from the left or top
      or (None)
       Use default of 0.5.

    Returns:
     (dict)
     Dictionary has specific properties:
      x, y, width, height:
       (float)
    """
    # Find the scaling required to make the horizontal edges fit exactly,
    # and the vertical edges fit exactly
    requiredHorizontalScale = float(i_container["width"]) / float(i_rect["width"])
    requiredVerticalScale = float(i_container["height"]) / float(i_rect["height"])
    # Use the larger of the two
    if requiredHorizontalScale > requiredVerticalScale:
        i_rect["left"] = i_container["left"]
        i_rect["width"] = i_container["width"]
        combinedBorderSize = i_container["height"] - i_rect["height"] * requiredHorizontalScale
        i_rect["top"] = i_container["top"] + i_align * combinedBorderSize
        i_rect["height"] = i_container["height"] - combinedBorderSize
    else:
        i_rect["top"] = i_container["top"]
        i_rect["height"] = i_container["height"]
        combinedBorderSize = i_container["width"] - i_rect["width"] * requiredVerticalScale
        i_rect["left"] = i_container["left"] + i_align * combinedBorderSize
        i_rect["width"] = i_container["width"] - combinedBorderSize

    return i_rect

#fitLetterboxed({"left": 0, "top": 0, "width": 426, "height": 1034}, {"left": 0, "top": 0, "width": 4.0, "height": 3.0}, 0.5)

def qrectToDanrect(i_qrect):
    return { "left": i_qrect.left(), "top": i_qrect.top(), "width": i_qrect.width(), "height": i_qrect.height() }
def danrectToQrect(i_danrect):
    return QRect(i_danrect["left"], i_danrect["top"], i_danrect["width"], i_danrect["height"])

# + + }}}

def dbRow_getNumberedScreenshotFullPath(i_row, i_picNo):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

     i_picNo:
      (int)
      0: first picture

    Returns:
     Either (str)
      Absolute (resolved via the config's 'config_screenshotsBaseDirPath') path of image.
     or (None)
      There is no screenshot at this numeric position.
    """
    screenshotPath = None
    if i_picNo == 0:
        screenshotPath = dbRow_getScreenshotRelativePath(i_row)
    else:
        screenshotPaths = dbRow_getSupplementaryScreenshotPaths(i_row)
        if i_picNo-1 < len(screenshotPaths):
            screenshotPath = screenshotPaths[i_picNo-1]
    if screenshotPath == None:
        return None

    if not hasattr(gamebase, "config_screenshotsBaseDirPath"):
        return None

    return normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath

def dbRow_getPhotoFullPath(i_row):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Absolute (resolved via the config's 'config_photosBaseDirPath') path of image.
     or (None)
      There is no photo.
    """
    photoPath = dbRow_getPhotoRelativePath(i_row)
    if photoPath == None:
        return None

    if not hasattr(gamebase, "config_photosBaseDirPath"):
        return None

    return normalizeDirPathFromConfig(gamebase.config_photosBaseDirPath + "/" + photoPath)

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

        column = columns.tableColumn_getByPos(i_index.column())

        # Screenshot (unnumbered, old)
        if column["id"] == "pic":
            screenshotFullPath = dbRow_getNumberedScreenshotFullPath(self.parent().dbRows[i_index.row()], 0)
            if screenshotFullPath != None:
                pixmap = QPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.drawPixmap(destRect, pixmap)

        # Screenshot
        elif column["id"].startswith("pic[") and column["id"].endswith("]"):
            picNo = int(column["id"][4:-1])

            screenshotFullPath = dbRow_getNumberedScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            if screenshotFullPath != None:
                pixmap = QPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.drawPixmap(destRect, pixmap)

        # Musician photo
        elif column["id"] == "musician_photo":
            photoFullPath = dbRow_getPhotoFullPath(self.parent().dbRows[i_index.row()])
            if photoFullPath != None:
                pixmap = QPixmap(photoFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.drawPixmap(destRect, pixmap)

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
        return columns.tableColumn_count()

    #https://stackoverflow.com/questions/7988182/displaying-an-image-from-a-qabstracttablemodel
    #https://forum.qt.io/topic/5195/qtableview-extra-column-space-solved/8
    def data(self, i_index, i_role):  # override from QAbstractTableModel
        if not i_index.isValid():
            return None

        column = columns.tableColumn_getByPos(i_index.column())

        # Detail
        if column["id"] == "detail":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                return "+"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Play
        elif column["id"] == "play":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                if self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("Games.Filename")] == None:
                    return ""
                return "▶"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Music
        elif column["id"] == "music":
            if i_role == Qt.DisplayRole or i_role == MyTableModel.FilterRole:
                if self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("Games.SidFilename")] == None:
                    return ""
                return "M"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Screenshot
        elif column["id"] == "pic" or (column["id"].startswith("pic[") and column["id"].endswith("]")):
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    screenshotPath = self.parent().dbRows[i_index.row()][self.parent().dbColumnNames.index("Games.ScrnshotFilename")]
            #    pixmap = QPixmap(normalizeDirPathFromConfig(gamebase.config_screenshotsBaseDirPath) + "/" + screenshotPath)
            #    return pixmap;
            pass
        #
        else:
            usableColumn = columns.usableColumn_getById(column["id"])
            # Enum field
            if "type" in usableColumn and usableColumn["type"] == "enum":
                if i_role == MyTableModel.FilterRole:
                    return self.parent().dbRows[i_index.row()][usableColumn["dbIdentifiers"][0]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][usableColumn["dbIdentifiers"][0]]
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
                    return self.parent().dbRows[i_index.row()][usableColumn["dbIdentifiers"][0]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][usableColumn["dbIdentifiers"][0]]
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
                    return self.parent().dbRows[i_index.row()][usableColumn["dbIdentifiers"][0]]
                elif i_role == Qt.TextAlignmentRole:
                    if column["textAlignment"] == "center":
                        return Qt.AlignCenter
                    elif column["textAlignment"] == "left":
                        return Qt.AlignLeft

        return None

    # [Not used anymore since the native QTableView headers are hidden]
    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            column = columns.tableColumn_getByPos(i_columnNo)
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

import collections
class DbRecordDict(collections.UserDict):
    """
    A dictionary intended to hold keys which are fully qualified '<table name>.<column name>' names,
    and overrides __getitem__ so that you can get items by either that full name or just '<column name>'.
    """
    def __getitem__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return self.data[i_key]

        # Try matching just the last name component
        for realKey, value in self.data.items():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return value

        # Raise KeyError
        return self.data[i_key]

    def __contains__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return True

        # Try matching just the last name component
        for realKey in self.data.keys():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return True

        #
        return False

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

    def queryDb(self, i_whereExpression, i_whereExpressionMightUseNonVisibleColumns=True):
        """
        Params:
         i_whereExpression:
          (str)
         i_whereExpressionMightUseNonVisibleColumns:
          (bool)
        """
        # Start with fields that are always selected
        selectTerms = [
            "Games.GA_Id AS [Games.GA_Id]"
        ]

        fromTerms = [
            "Games"
        ]

        # Determine what extra fields to select
        neededTableNames = set()
        neededSelects = set()

        #  For all visible table columns,
        #  collect tables that need to be joined to and the SELECT expression
        for tableColumn in columns.tableColumn_getBySlice():
            usableColumn = columns.usableColumn_getById(tableColumn["id"])
            if "dbTableNames" in usableColumn:
                for dbTableName in usableColumn["dbTableNames"]:
                    neededTableNames.add(dbTableName)
            if "dbSelect" in usableColumn:
                neededSelects.add(usableColumn["dbSelect"])

        #  If needed, parse WHERE expression for column names and add those too
        if i_whereExpressionMightUseNonVisibleColumns:
            parsedNeededTableNames, parsedNeededSelects = sqlWhereExpressionToTableNamesAndSelects(i_whereExpression)
            neededTableNames = neededTableNames.union(parsedNeededTableNames)
            neededSelects = neededSelects.union(parsedNeededSelects)

        # Add the extra fromTerms
        tableConnections = copy.deepcopy(connectionsFromGamesTable)
        for neededTableName in neededTableNames:
            fromTerms += getJoinTermsToTable(neededTableName, tableConnections)

        # Add the extra selectTerms
        for neededSelect in neededSelects:
            if neededSelect == "Games.GA_Id" or neededSelect == "GA_Id":  # TODO use a set for this too
                continue
            selectTerms.append(neededSelect)

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
                usableColumn = columns.usableColumn_getById(columnId)
                term = usableColumn["dbIdentifiers"][0]
                if direction == -1:
                    term += " DESC"
                orderByTerms.append(term)
            sql += ", ".join(orderByTerms)

        # Execute
        #print(sql)
        try:
            cursor = g_db.execute(sql)
        except sqlite3.OperationalError as e:
            # TODO if i_whereExpressionMightUseNonVisibleColumns and error was 'no such column', maybe retry with SELECT * and all tables (see getGameRecord())
            raise

        self.dbColumnNames = [column[0]  for column in cursor.description]
        self.dbRows = cursor.fetchall()

        label_statusbar.setText("Showing " + str(len(self.dbRows)) + " games.")

    def selectedGameId(self):
        """
        Returns:
         (int)
        """
        selectedIndex = self.selectionModel().currentIndex()
        return self.dbRows[selectedIndex.row()][self.dbColumnNames.index("Games.GA_Id")]

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

            messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
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
            idColumnNo = self.dbColumnNames.index("Games.GA_Id")
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
        columnNo = columns.tableColumn_idToPos(i_id)
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
        columnId = columns.tableColumn_getByPos(i_modelIndex.column())["id"]

        if columnId == "detail":
            detailPaneWasAlreadyVisible = detailPane_height() > 0
            detailPane_show()
            self.scrollTo(i_modelIndex, QAbstractItemView.PositionAtTop)
            gameId = self.dbRows[i_modelIndex.row()][self.dbColumnNames.index("Games.GA_Id")]
            if gameId != detailPane_currentGameId:
                detailPane_populate(gameId)
            if i_keyboardOriented and detailPaneWasAlreadyVisible:
                detailPane_webEngineView.setFocus(Qt.OtherFocusReason)

        elif columnId == "play":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = getGameRecord(gameId)
            gameRecord = DbRecordDict(gameRecord)

            try:
                gamebase.runGame(gameRecord["Games.Filename"], gameRecord["Games.FileToRun"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
                messageBox.setText("<big><b>In runGame():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                messageBox.resizeToContent()
                messageBox.exec()

        elif columnId == "music":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = getGameRecord(gameId)
            gameRecord = DbRecordDict(gameRecord)

            try:
                gamebase.runMusic(gameRecord["Games.SidFilename"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
                messageBox.setText("<big><b>In runMusic():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                messageBox.resizeToContent()
                messageBox.exec()

        # Screenshot (unnumbered, old)
        elif columnId == "pic":
            rowNo = i_modelIndex.row()
            screenshotFullPath = dbRow_getNumberedScreenshotFullPath(self.dbRows[rowNo], 0)
            if screenshotFullPath != None:
                frontend_utils.openInDefaultApplication(screenshotFullPath)

        # Screenshot
        elif columnId == "pic" or (columnId.startswith("pic[") and columnId.endswith("]")):
            picNo = int(columnId[4:-1])

            rowNo = i_modelIndex.row()
            screenshotFullPath = dbRow_getNumberedScreenshotFullPath(self.dbRows[rowNo], picNo)
            if screenshotFullPath != None:
                frontend_utils.openInDefaultApplication(screenshotFullPath)

        # Musician photo
        elif columnId == "musician_photo":
            rowNo = i_modelIndex.row()
            photoFullPath = dbRow_getPhotoFullPath(self.dbRows[rowNo])
            if photoFullPath != None:
                frontend_utils.openInDefaultApplication(photoFullPath)

        else:
            usableColumn = columns.usableColumn_getById(columnId)
            if "type" in usableColumn and usableColumn["type"] == "gameId":
                # Get the target game ID
                rowNo = i_modelIndex.row()
                gameId = self.dbRows[rowNo][self.dbColumnNames.index(usableColumn["dbIdentifiers"][0])]
                if gameId != 0:
                    self.selectGameWithId(gameId)

    def findGameWithId(self, i_id):
        idColumnNo = self.dbColumnNames.index("Games.GA_Id")
        for rowNo, row in enumerate(self.dbRows):
            if row[idColumnNo] == i_id:
                return rowNo
        return None

    def selectGameWithId(self, i_gameId):
        # Look for row in table,
        # and if not found then clear filter and look again
        rowNo = self.findGameWithId(i_gameId)
        if rowNo == None:
            if sqlFilterBar.isVisible():
                sqlFilterBar.userSetText("")
            else:
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
        column = columns.tableColumn_getByPos(selectedIndex.column())
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

        columnId = columns.tableColumn_getByPos(selectedIndex.column())["id"]
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
        allColumnsWidth = sum([column["width"]  for column in columns.tableColumn_getBySlice()])
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
                    #self.resize_selectedRowId = self.dbRows[selectedIndex.row()][self.dbColumnNames.index("Games.GA_Id")]
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

import main_window
mainWindow = main_window.MainWindow(application)
mainWindow.resize(800, 600)
mainWindow.move(QApplication.desktop().rect().center() - mainWindow.rect().center())
mainWindow.move(QApplication.desktop().rect().center() - mainWindow.rect().center())
if hasattr(gamebase, "config_title"):
    mainWindow.setWindowTitle(gamebase.config_title + " - GameBase")
else:
    mainWindow.setWindowTitle(param_configModuleFilePath + " - GameBase")

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
        selectedColumn = columns.tableColumn_getByPos(selectedIndex.column())
        if tableView.hasFocus() and selectedColumn != None and selectedColumn["filterable"]:
            targetColumn = selectedColumn
        # Else target the first visible and filterable column
        else:
            for column in columns.tableColumn_getBySlice():
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
mainWindow.layout.addWidget(menuBar)

def menu_file_openDatabaseInExternalProgram_onTriggered(i_checked):
    frontend_utils.openInDefaultApplication([gamebase.config_databaseFilePath])

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

    # Scan operands,
    # and attempt to pick out one and only one identifier token to be the column name,
    # and one and only one token of another type to be the value
    columnName = None
    value = None
    for child in i_node["children"]:
        # If the operand is itself a child operator
        if type(child) == dict:
            # If it's an 'ESCAPE' operator (an adjunct to 'LIKE'),
            # pull the actual value (as opposed to the escape character) from out of it
            if "op" in child and child["op"] == ("operator", "ESCAPE"):
                value = child["children"][0][1]  # TODO unescape?
            # If it's an 'AND' operator beneath a 'BETWEEN',
            # assemble the two values with a tilde between them
            elif operator == "BETWEEN" and child["op"] == ("operator", "AND"):
                value = child["children"][0][1] + "~" + child["children"][1][1]
            # If it's some other child operator,
            # don't know how to deal with this so far
            else:
                return None, None, None
        #
        elif type(child) == tuple:
            # If it's an identifier,
            # consider it the column name,
            # but fail if we already have one
            if child[0] == "identifier":
                if columnName != None:
                    return None, None, None
                columnName = child[1]
            # Else if it's not an identifier,
            # consider it the value,
            # but fail if we already have one
            else:
                if value != None:
                    return None, None, None
                value = child[1]

    if operator == None or columnName == None or value == None:
        return None, None, None
    return operator, columnName, value

def sqlWhereExpressionToColumnFilters(i_whereExpression, i_skipFailures=False):
    """
    Parse SQL WHERE expression
    and get it as an equivalent set of column names and texts to enter into those boxes on the column filter bar.

    Params:
     i_whereExpression:
      (str)
     i_skipFailures:
      (bool)

    Returns:
     Either (list)
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
     or (None)
      Failed to get SQL expression into the simple column filter bar-compatible form.
      Perhaps it is too complex for that UI, too complex for the simple SQL parser, etc.
    """
    # Tokenize, parse and postprocess it
    tokenized = sql.tokenizeWhereExpr(i_whereExpression)
    if len(tokenized) == 0:
        return []
    sql.initializeOperatorTable()
    parsed = sql.parseExpression(tokenized)
    #print(parsed)
    if parsed == None:
        label_statusbar.setText("Failed to parse")
        return None
    parsed = sql.flattenOperator(parsed, "AND")
    parsed = sql.flattenOperator(parsed, "OR")

    # Get or simulate a top-level OR array from the input parse tree
    if "op" in parsed and parsed["op"] == ("operator", "OR"):
        orExpressions = parsed["children"]
    else:
        orExpressions = [parsed]

    # Initialize an output top-level OR array,
    # and then for every input OR expression
    oredRows = []
    for orExpressionNo, orExpression in enumerate(orExpressions):

        # Get or simulate a second-level AND array from the input parse tree
        if "op" in orExpression and orExpression["op"] == ("operator", "AND"):
            andExpressions = orExpression["children"]
        else:
            andExpressions = [orExpression]

        # Initialize an output second-level AND dict,
        # and then for every input AND expression
        andedFields = {}
        for andExpression in andExpressions:
            # Get important parts of term
            operator, columnName, value = interpretColumnOperation(andExpression)
            #print("operator, columnName, value: " + str((operator, columnName, value)))

            # If that failed,
            # either skip this term or fail the whole extraction
            # [though maybe we should just skip over this andExpression as it could be just a useless term like "1=1"]
            if operator == None and columnName == None and value == None:
                if i_skipFailures:
                    continue
                else:
                    label_statusbar.setText("Failed to interpret column")
                    return None

            # If the column name actually corresponds to a database field
            usableColumn = columns.usableColumn_getByDbIdentifier(columnName)
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

def sqlWhereExpressionToTableNamesAndSelects(i_whereExpression):
    """
    Parse SQL WHERE expression
    and get database table names and select terms needed to get the columns being referenced in it.

    Params:
     i_sqlWhereExpression:
      (str)

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (set)
       Table names
      1:
       (set)
       Identifiers
    """
    try:
        oredRows = sqlWhereExpressionToColumnFilters(i_whereExpression, True)
    except:
        return []
    if oredRows == None:
        return []

    dbTableNames = set()
    dbSelects = set()
    for oredRow in oredRows:
        for andedFieldId in oredRow.keys():
            usableColumn = columns.usableColumn_getById(andedFieldId)
            for dbTableName in usableColumn["dbTableNames"]:
                dbTableNames.add(dbTableName)
            dbSelects.add(usableColumn["dbSelect"])
    return dbTableNames, dbSelects

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
    if oredRows == None:
        columnFilterBar.resetFilterRowCount(1)
    else:
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
filterMenu_back_action.setShortcut(QKeySequence("Alt+Left"))
filterMenu_forward_action = filterMenu.addAction("Go &forward")
filterMenu_forward_action.triggered.connect(filterHistory_goForward)
filterMenu_forward_action.setShortcut(QKeySequence("Alt+Right"))

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
def viewMenu_toolbar_onTriggered(i_checked):
    toolbar.setVisible(i_checked)
viewMenu_toolbar_action.triggered.connect(viewMenu_toolbar_onTriggered)

viewMenu.addSeparator()

def splitter_setHorizontal():
    splitter.setOrientation(Qt.Horizontal)
def splitter_setVertical():
    splitter.setOrientation(Qt.Vertical)
#viewMenu_splitMenu = QMenu("&Split")
#viewMenu_toolbar_action = viewMenu.addMenu(viewMenu_splitMenu)
viewMenu_verticalAction = viewMenu.addAction("Split &vertically")
viewMenu_verticalAction.setCheckable(True)
viewMenu_verticalAction.setChecked(True)
viewMenu_verticalAction.triggered.connect(splitter_setVertical)
viewMenu_horizontalAction = viewMenu.addAction("Split &horizontally")
viewMenu_horizontalAction.setCheckable(True)
viewMenu_horizontalAction.triggered.connect(splitter_setHorizontal)
actionGroup = QActionGroup(filterMenu)
actionGroup.setExclusive(True)
actionGroup.addAction(viewMenu_horizontalAction)
actionGroup.addAction(viewMenu_verticalAction)

viewMenu.addSeparator()

class TableColumnsMenu(qt_extras.StayOpenMenu):
    def __init__(self, i_parent=None):
        qt_extras.StayOpenMenu.__init__(self, i_parent)

        self.aboutToShow.connect(self.onAboutToShow)

    def populateMenu(self):
        # Add all the usable columns
        for usableColumn in columns.usableColumn_getBySlice():
            action = self.addAction(usableColumn["screenName"])
            action.setCheckable(True)
            columnId = usableColumn["id"]
            action.setChecked(columns.tableColumn_getById(columnId) != None)
            action.triggered.connect(functools.partial(self.action_onTriggered, columnId))

    def onAboutToShow(self):
        for usableColumnNo, usableColumn in enumerate(columns.usableColumn_getBySlice()):
            action = self.actions()[usableColumnNo]
            columnId = usableColumn["id"]
            action.setChecked(columns.tableColumn_getById(columnId) != None)

    def action_onTriggered(self, i_selectedColumnId):
        # Toggle the visibility of the selected column
        columns.tableColumn_toggle(i_selectedColumnId, viewMenu_tableColumnsMenu.context)

        # Update GUI
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
        tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])

viewMenu_tableColumnsMenu = TableColumnsMenu("&Table columns")
viewMenu_tableColumnsMenu_action = viewMenu.addMenu(viewMenu_tableColumnsMenu)
def viewMenu_tableColumnsMenu_action_onHovered():
    viewMenu_tableColumnsMenu.context = None
viewMenu_tableColumnsMenu_action.hovered.connect(viewMenu_tableColumnsMenu_action_onHovered)

viewMenu.addSeparator()

viewMenu_saveLayout = viewMenu.addAction("&Save layout")
def viewMenu_saveLayout_onTriggered():
    configColumns = []
    for tableColumn in g_tableColumns:
        configColumns.append({
            "id": tableColumn["id"],
            "width": tableColumn["width"]
        })

    configDict = {
        "tableColumns": configColumns
    }

    settingsFilePath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation) + os.sep + "pyGamebase.json"
    with open(settingsFilePath, "wb") as f:
        f.write(json.dumps(configDict, indent=4).encode("utf-8"))
viewMenu_saveLayout.triggered.connect(viewMenu_saveLayout_onTriggered)

# + }}}

# + Toolbar {{{

toolbar = QToolBar()
toolbar_back_action = toolbar.addAction(QIcon(application.style().standardIcon(QStyle.SP_ArrowLeft)), "Back")
toolbar_back_action.triggered.connect(filterHistory_goBack)
toolbar_forward_action = toolbar.addAction(QIcon(application.style().standardIcon(QStyle.SP_ArrowRight)), "Forward")
toolbar_forward_action.triggered.connect(filterHistory_goForward)
mainWindow.layout.addWidget(toolbar)

# + }}}

# Create splitter
splitter = QSplitter(Qt.Vertical)
mainWindow.layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
splitter_lastPosition = 200
def splitter_onSplitterMoved(i_pos, i_index):
    global splitter_lastPosition
    splitter_lastPosition = i_pos
splitter.splitterMoved.connect(splitter_onSplitterMoved)

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

def refilterFromCurrentlyVisibleBar():
    if sqlFilterBar.isVisible():
        sqlWhereExpression = sqlFilterBar.text()
    else:
        sqlWhereExpression = columnFilterBar.getSqlWhereExpression()

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

sqlFilterBar = sql_filter_bar.SqlFilterBar()
sqlFilterBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
sqlFilterBar.setFixedHeight(30)
sqlFilterBar.hide()
gameTable_layout.addWidget(sqlFilterBar)

def sqlFilterBar_onEditingFinished(i_modified):
    if not i_modified:
        tableView.setFocus()
    else:
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
sqlFilterBar.editingFinished.connect(sqlFilterBar_onEditingFinished)

# + }}}

# + Table view {{{

# Create table
tableView = MyTableView()
gameTable_layout.addWidget(tableView)
# Set vertical size policy to 'Ignored' which lets widget shrink to zero
#  https://stackoverflow.com/questions/18342590/setting-qlistwidget-minimum-height
tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

#  Set initial column widths
tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])

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
    if (splitter.orientation() == Qt.Vertical):
        # Position splitter so that the table view shows exactly one row
        if sqlFilterBar.isVisible():
            filterBarHeight = sqlFilterBar.geometry().height()
        else:
            filterBarHeight = columnFilterBar.geometry().height()
        topPaneHeight = columnNameBar.geometry().height() + filterBarHeight + tableView.rowHeight()
        if tableView.horizontalScrollBar().isVisible():
            topPaneHeight += application.style().pixelMetric(QStyle.PM_ScrollBarExtent)  # Scrollbar height
        splitter.setSizes([topPaneHeight, splitter.geometry().height() - topPaneHeight])
        # Switch table view scroll mode so that an item will stay aligned at the top,
        # to fit neatly into the area we resized above
        tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
    else:
        splitter.setSizes([splitter_lastPosition, splitter.geometry().width() - splitter_lastPosition])

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
#detailPane_margin.setFixedWidth(columns.tableColumn_getByPos(0)["width"])
detailPane_margin.setFixedWidth(columns.usableColumn_getById("detail")["defaultWidth"])
#print(columns.tableColumn_getByPos(0)["width"])

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
    detailPane_currentGameId = gameRow["Games.GA_Id"]

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
    if "Games.CloneOf_Name" in gameRow and gameRow["Games.CloneOf_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Clone of: '
        html += '<a href="game:///' + str(gameRow["Games.CloneOf"]) + '">' + gameRow["Games.CloneOf_Name"] + '</a>'
        html += '</p>'

    if "Games.Prequel_Name" in gameRow and gameRow["Games.Prequel_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Prequel: '
        html += '<a href="game:///' + str(gameRow["Games.Prequel"]) + '">' + gameRow["Games.Prequel_Name"] + '</a>'
        html += '</p>'

    if "Games.Sequel_Name" in gameRow and gameRow["Games.Sequel_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Sequel: '
        html += '<a href="game:///' + str(gameRow["Games.Sequel"]) + '">' + gameRow["Games.Sequel_Name"] + '</a>'
        html += '</p>'

    if "Games.Related_Name" in gameRow and gameRow["Games.Related_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Related: '
        html += '<a href="game:///' + str(gameRow["Games.Related"]) + '">' + gameRow["Games.Related_Name"] + '</a>'
        html += '</p>'

    # Insert memo text
    if gameRow["Games.MemoText"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += gameRow["Games.MemoText"]
        html += '</p>'

    # Insert comment
    if gameRow["Games.Comment"] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += gameRow["Games.Comment"]
        html += '</p>'

    # Insert weblink(s)
    if "Games.WebLink_Name" in gameRow and gameRow["Games.WebLink_Name"] != None:
        html += '<p style="white-space: pre-wrap;">'

        html += gameRow["Games.WebLink_Name"] + ": "
        url = gameRow["Games.WebLink_URL"]
        html += '<a href="' + url + '">'
        html += url
        html += '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #    electron.shell.openExternal(this.href);
        #});

        # If it's a World Of Spectrum link then insert a corresponding Spectrum Computing link
        if gameRow["Games.WebLink_Name"] == "WOS":
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
    extrasRows = getExtrasRecords(str(gameRow["Games.GA_Id"]))

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
                    gameInfo = DbRecordDict(gameInfo)

                    try:
                        gamebase.runExtra(extraPath, extraInfo, gameInfo)
                    except Exception as e:
                        import traceback
                        print(traceback.format_exc())
                        messageBox = qt_extras.ResizableMessageBox(application.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
                        messageBox.setText("<big><b>In runExtra():</b></big>")
                        messageBox.setInformativeText(traceback.format_exc())
                        messageBox.resizeToContent()
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
#mainWindow.layout.addSpacing(8)
mainWindow.layout.addWidget(label_statusbar)
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
#mainWindow.layout.addWidget(zzz)
#zzz.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#zzz.setAutoFillBackground(True)
#zzz.setFixedSize(300, 120)

detailPane_hide()

#
mainWindow.show()

openDb()

viewMenu_tableColumnsMenu.populateMenu()

# Create initial table columns
if "tableColumns" in g_frontendSettings:
    initialColumns = g_frontendSettings["tableColumns"]
else:
    initialColumns = [
        { "id": "detail",
          "width": 35,
        },
        { "id": "play",
          "width": 35,
        },
        { "id": "pic",
          "width": 320,
        },
        { "id": "id",
          "width": 50,
        },
        { "id": "name",
          "width": 250,
        },
        { "id": "year",
          "width": 75,
        },
        { "id": "publisher",
          "width": 250,
        },
        { "id": "developer",
          "width": 250,
        },
        { "id": "programmer",
          "width": 250,
        },
        { "id": "parent_genre",
          "width": 150,
        },
        { "id": "genre",
          "width": 150,
        }
    ]

for initialColumn in initialColumns:
    columns.tableColumn_add(initialColumn["id"], initialColumn["width"])

columnNameBar.initFromColumns()
columnFilterBar.initFromColumns()
refilterFromCurrentlyVisibleBar()
tableView.requery()
tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])

if columns.tableColumn_getById("name") != None:
    columnNameBar.sort("name", False)

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
