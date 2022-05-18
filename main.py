#!/usr/bin/python
# -*- coding: utf-8 -*-


# Python std
import sys
import sqlite3
import functools
import os.path
import re

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



# + Column visibility {{{

g_columns = [
    { "id": "detail",
      "headingText": "",
      "visible": True,
      "width": 35,
      "sortable": False,
      "filterable": False
    },
    { "id": "play",
      "headingText": "",
      "visible": True,
      "width": 35,
      "sortable": False,
      "filterable": False
    },
    { "id": "pic",
      "headingText": "",#"Pic",
      "visible": True,
      "width": 320,
      "sortable": False,
      "filterable": False
    },
    #{ "id": "pic2",
    #  "headingText": "Pic",
    #  "visible": True,
    #  "width": 320,
    #  "sortable": False,
    #  "filterable": False
    #},
    { "id": "id",
      "headingText": "",#"ID",
      "visible": True,
      "width": 40,
      "sortable": False,
      "filterable": False,
      "qualifiedDbFieldName": "Games.GA_Id",
      "unqualifiedDbFieldName": "GA_Id"
    },
    { "id": "name",
      "headingText": "Name",
      "visible": True,
      "width": 250,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "Games.Name",
      "unqualifiedDbFieldName": "Name"
    },
    { "id": "year",
      "headingText": "Year",
      "visible": True,
      "width": 75,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "Years.Year",
      "unqualifiedDbFieldName": "Year"
    },
    { "id": "publisher",
      "headingText": "Publisher",
      "visible": True,
      "width": 250,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "Publishers.Publisher",
      "unqualifiedDbFieldName": "Publisher"
    },
    { "id": "programmer",
      "headingText": "Programmer",
      "visible": True,
      "width": 250,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "Programmers.Programmer",
      "unqualifiedDbFieldName": "Programmer"
    },
    { "id": "parent_genre",
      "headingText": "Parent genre",
      "visible": True,
      "width": 150,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "PGenres.ParentGenre",
      "unqualifiedDbFieldName": "ParentGenre"
    },
    { "id": "genre",
      "headingText": "Genre",
      "visible": True,
      "width": 150,
      "sortable": True,
      "filterable": True,
      "qualifiedDbFieldName": "Genres.Genre",
      "unqualifiedDbFieldName": "Genre"
    }
]
# (list of Column)

# Type: Column
#  (dict)
#  Has keys:
#   headingText:
#    (str)
#   visible:
#    (bool)
#   width:
#    (int)
#    In pixels

# + }}}

# + Screenshot file/URL resolving {{{

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
    return gamebase.config_screenshotsBaseDirPath + "/" + i_relativePath

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

def openDb():
    global g_db
    #g_db = sqlite3.connect(gamebase.config_databaseFilePath)
    #print("file:" + gamebase.config_databaseFilePath + "?mode=ro")
    g_db = sqlite3.connect("file:" + gamebase.config_databaseFilePath + "?mode=ro", uri=True)

    # Add REGEXP function
    def functionRegex(i_pattern, i_value):
        #print("functionRegex(" + i_value + ", " + i_pattern + ")")
        #c_pattern = re.compile(r"\b" + i_pattern.lower() + r"\b")
        compiledPattern = re.compile(i_pattern)
        return compiledPattern.search(str(i_value)) is not None
    g_db.create_function("REGEXP", 2, functionRegex)

    # Get columns in Games table
    cursor = g_db.execute("PRAGMA table_info(Games)")
    global g_db_gamesColumnNames
    g_db_gamesColumnNames = [row[1]  for row in cursor.fetchall()]

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

def queryDb():
    # SELECT
    sql = """
SELECT
 Games.GA_Id,
 Games.Name,
 Games.Comment,
 Games.Gemus,
 Years.Year,
 Games.Filename,
 Games.FileToRun,
 Games.ScrnshotFilename,
 Genres.Genre,
 PGenres.ParentGenre,
 Publishers.Publisher,
 Programmers.Programmer,
 Games.MemoText"""
    if "CloneOf" in g_db_gamesColumnNames:
        sql += ", CloneOfGame.Name AS CloneOfName"
    if "WebLink_Name" in g_db_gamesColumnNames:
        sql += ", Games.WebLink_Name"
    if "WebLink_URL" in g_db_gamesColumnNames:
        sql += ", Games.WebLink_URL"

    # FROM
    sql += """
FROM
 Games
 LEFT JOIN Years ON Games.YE_Id = Years.YE_Id
 LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id
 LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id
 LEFT JOIN Publishers ON Games.PU_Id = Publishers.PU_Id
 LEFT JOIN Programmers ON Games.PR_Id = Programmers.PR_Id"""
    if "CloneOf" in g_db_gamesColumnNames:
        sql += "\nLEFT JOIN Games AS CloneOfGame ON Games.CloneOf = CloneOfGame.GA_Id"

    # WHERE
    andGroups = []

    for filterRow in headerBar.filterRows:
        andTerms = []

        for column in g_columns:
            if column["filterable"]:
                value = filterRow["columnFilterEdits"][column["id"]].text()
                value = value.strip()
                if value != "":
                    # If range operator
                    betweenValues = value.split("~")
                    if len(betweenValues) == 2 and stringLooksLikeNumber(betweenValues[0]) and stringLooksLikeNumber(betweenValues[1]):
                        andTerms.append(column["qualifiedDbFieldName"] + " BETWEEN " + betweenValues[0] + " AND " + betweenValues[1])

                    # Else if regular expression
                    elif len(value) > 2 and value.startswith("/") and value.endswith("/"):
                        # Get regexp
                        value = value[1:-1]

                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(column["qualifiedDbFieldName"] + " REGEXP " + value)
                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                    # Else if 2 character comparison operator
                    elif value.startswith(">=") or value.startswith("<=") or value.startswith("<>"):
                        # Get operator and value
                        operator = value[:2]
                        value = value[2:]

                        # If value doesn't look like a number, format it as a string
                        if not stringLooksLikeNumber(value):
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                        #
                        andTerms.append(column["qualifiedDbFieldName"] + " " + operator + " " + value)

                    # Else if 1 character comparison operator
                    elif value.startswith(">") or value.startswith("<") or value.startswith("="):
                        # Get operator and value
                        operator = value[:1]
                        value = value[1:]

                        # If value doesn't look like a number, format it as a string
                        if not stringLooksLikeNumber(value):
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                        #
                        andTerms.append(column["qualifiedDbFieldName"] + " " + operator + " " + value)

                    # Else if LIKE expression (contains an unescaped %)
                    elif value.replace("\\%", "").find("%") != -1:
                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(column["qualifiedDbFieldName"] + " LIKE " + value + " ESCAPE '\\'")

                    # Else if a plain string
                    else:
                        value = "%" + value + "%"

                        # Format value as a string
                        value = value.replace("'", "''")
                        value = "'" + value + "'"

                        #
                        andTerms.append(column["qualifiedDbFieldName"] + " LIKE " + value + " ESCAPE '\\'")

        if len(andTerms) > 0:
            andGroups.append(andTerms)

    if len(andGroups) > 0:
        sql += "\nWHERE "
        sql += " OR ".join(["(" + andGroupStr + ")"  for andGroupStr in [" AND ".join(andGroup)  for andGroup in andGroups]])

    # ORDER BY
    if headerBar.sort_columnNo != None:
        sql += "\nORDER BY "
        sql += g_columns[headerBar.sort_columnNo]["qualifiedDbFieldName"]
        if headerBar.sort_direction == -1:
            sql += " DESC"

    #print(sql)
    cursor = g_db.execute(sql)

    global g_dbColumnNames
    g_dbColumnNames = [column[0]  for column in cursor.description]
    global g_dbRows
    g_dbRows = cursor.fetchall()

    label_statusbar.setText("Showing " + str(len(g_dbRows)) + " games.")

def dbRow_getScreenshotRelativePath(i_row):
    """
    Get the path of a game's first screenshot picture.
    This comes from the 'ScrnshotFilename' database field.

    Params:
     i_row:
      (tuple)
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
        screenshotRelativePath = i_row[g_dbColumnNames.index("ScrnshotFilename")]
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
      (tuple)
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
      (tuple)
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

    class FilterEdit(QWidget):  # TODO rename to FilterEdit
        # Emitted after the text is changed
        textChange = Signal()

        def __init__(self, i_parent=None):
            QWidget.__init__(self, i_parent)

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
            self.clearButton.setStyleSheet("QPushButton { border: none; }");
            #self.clearButton.setFlat(True)
            self.clearButton.setFixedHeight(HeaderBar.filterRowHeight)
            self.clearButton.setFixedWidth(HeaderBar.filterRowHeight)
            self.clearButton.setVisible(False)
            self.layout.addWidget(self.clearButton)
            self.layout.setStretch(1, 0)
            self.clearButton.clicked.connect(self.clearButton_onClicked)

            self.lineEdit.textEdited.connect(self.lineEdit_onTextEdited)

        def lineEdit_onEditingFinished(self):
            self.textChange.emit()

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

        self.columnHeadingButtons = {}
        # (dict)
        # Dictionary has arbitrary key-value properties:
        #  Keys:
        #   (str)
        #   Column id
        #  Values:
        #   (HeadingButton)

        self.filterRows = []
        # (list)
        # Each element is:
        #  (dict)
        #  Dictionary has specific key-value properties:
        #   deleteRow_pushButton:
        #    (QPushButton)
        #   columnFilterEdits:
        #    (dict)
        #    Dictionary has arbitrary key-value properties:
        #     Keys:
        #      (str)
        #      Column id
        #     Values:
        #      (FilterEdit)

        # Resizing of columns by mouse dragging
        self.installEventFilter(self)
        #  Receive mouse move events even if button isn't held down
        self.setMouseTracking(True)
        #  State used while resizing
        self.resize_columnNo = None
        self.resize_mouseToEdgeOffset = None

        # State of column sorting
        self.sort_columnNo = None
        self.sort_direction = None

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

        # Create header buttons
        global g_columns
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                # Create header button
                headingButton = HeadingButton(column["headingText"], column["filterable"], self)
                self.columnHeadingButtons[column["id"]] = headingButton
                #column["headingButton"] = headingButton
                # Set its basic properties (apart from position)
                headingButton.clicked.connect(functools.partial(self.button_onClicked, columnNo))

        self.insertRow_pushButton = QPushButton("+", self)
        self.insertRow_pushButton.clicked.connect(self.insertRow_pushButton_onClicked)

        self.insertFilterRow(0)

        # Initially set all widget positions
        self.repositionHeadingButtons()
        self.repositionFilterEdits()

    # + Filter rows {{{

    def insertFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """
        newRow = {}

        # Add widgets to GUI
        deleteRow_pushButton = QPushButton("x", self)
        newRow["deleteRow_pushButton"] = deleteRow_pushButton
        deleteRow_pushButton.clicked.connect(functools.partial(self.deleteRow_pushButton_onClicked, newRow))
        deleteRow_pushButton.setVisible(True)

        newRow["columnFilterEdits"] = {}
        global g_columns
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                # Create FilterEdit
                headerFilter = HeaderBar.FilterEdit(self)
                newRow["columnFilterEdits"][column["id"]] = headerFilter
                # Set its basic properties (apart from position)
                headerFilter.setVisible(True)
                headerFilter.textChange.connect(functools.partial(self.lineEdit_onTextChange, columnNo))

        # Add entry to filterRows list
        self.filterRows.insert(i_position, newRow)

        # Resize header to accommodate the current number of filter rows
        self.setFixedHeight(HeaderBar.headingButtonHeight + HeaderBar.filterRowHeight*len(self.filterRows) - 1)

    def appendFilterRow(self):
        self.insertFilterRow(len(self.filterRows))

    def deleteFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """
        # Remove widgets from GUI
        filterRow = self.filterRows[i_position]
        for columnFilterEdit in filterRow["columnFilterEdits"].values():
            columnFilterEdit.setParent(None)
        filterRow["deleteRow_pushButton"].setParent(None)

        # Remove entry from filterRows list
        del(self.filterRows[i_position])

        # Resize header to accommodate the current number of filter rows
        self.setFixedHeight(HeaderBar.headingButtonHeight + HeaderBar.filterRowHeight*len(self.filterRows) - 1)

    def clearFilterRow(self, i_position):
        """
        Params:
         i_position:
          (int)
        """
        filterRow = self.filterRows[i_position]
        for columnFilterEdit in filterRow["columnFilterEdits"].values():
            columnFilterEdit.setText("")

    def deleteRow_pushButton_onClicked(self, i_filterRow):
        if len(self.filterRows) == 1:
            self.clearFilterRow(0)
        else:
            for filterRowNo, filterRow in enumerate(self.filterRows):
                if filterRow == i_filterRow:
                    self.deleteFilterRow(filterRowNo)
                    self.repositionFilterEdits()
        self.filterChange.emit()

    def insertRow_pushButton_onClicked(self):
        self.appendFilterRow()
        #self.repositionHeadingButtons()
        self.repositionFilterEdits()

    # + }}}

    #def sizeHint(self):
    #    return QSize(10000, 59)

    # + Scrolling {{{

    def scroll(self, i_dx, i_dy):
        self.scrollX += i_dx
        self.scrollY += i_dy
        QWidget.scroll(self, i_dx, i_dy)

    # + }}}

    def button_onClicked(self, i_columnNo):
        # If column isn't sortable,
        # bail
        if not g_columns[i_columnNo]["sortable"]:
            return

        # Remove old sort arrow from heading
        if self.sort_columnNo != None:
            headingButton = self.columnHeadingButtons[g_columns[self.sort_columnNo]["id"]]
            if headingButton.text().endswith("▲") or headingButton.text().endswith("▼"):
                headingButton.setText(g_columns[self.sort_columnNo]["headingText"])

        #
        if self.sort_columnNo == i_columnNo:
            self.sort_direction = -self.sort_direction
        else:
            self.sort_direction = 1
            self.sort_columnNo = i_columnNo

        # Add new sort arrow to heading
        headingButton = self.columnHeadingButtons[g_columns[self.sort_columnNo]["id"]]
        if self.sort_direction > 0:
            headingButton.setText(headingButton.text() + "  ▲")
        else:
            headingButton.setText(headingButton.text() + "  ▼")

        #
        queryDb()
        tableView.requery()

    def lineEdit_onTextChange(self, i_columnNo):
        self.filterChange.emit()

    # + Resizing columns by mouse dragging {{{

    def _columnBoundaryAtPixelX(self, i_x):
        """
        Params:
         i_x:
          (int)
          Relative to the left of the window.
        """
        x = 0

        for columnNo, column in enumerate(g_columns):
            columnEdgeX = x + column["width"]
            if abs(i_x - columnEdgeX) <= HeaderBar.resizeMargin:
                return columnNo, column, columnEdgeX

            x += column["width"]

        return None, None, None

    def eventFilter(self, i_watched, i_event):
        #print(i_event.type())

        if i_event.type() == QEvent.MouseMove:
            # If not currently resizing,
            # then depending on whether cursor is near a draggable vertical edge,
            # set cursor shape
            if self.resize_columnNo == None:
                # Get mouse pos relative to HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                #
                columnNo, _, _ = self._columnBoundaryAtPixelX(mousePos.x())
                if columnNo != None:
                    self.setCursor(Qt.SizeHorCursor)
                else:
                    self.unsetCursor()
            # Else if currently resizing,
            # do the resize
            else:
                # Get mouse pos relative to HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # Get new width
                newRightEdge = mousePos.x() + self.resize_mouseToEdgeOffset
                columnLeft = sum([column["width"]  for column in g_columns[0 : self.resize_columnNo]])
                newWidth = newRightEdge - columnLeft
                if newWidth < HeaderBar.minimumColumnWidth:
                    newWidth = HeaderBar.minimumColumnWidth
                # Resize column
                column = g_columns[self.resize_columnNo]
                column["width"] = newWidth

                # Move/resize buttons and lineedits
                self.repositionHeadingButtons()
                self.repositionFilterEdits()
                #
                tableView.horizontalHeader().resizeSection(self.resize_columnNo, newWidth)

                return True

        elif i_event.type() == QEvent.MouseButtonPress:
            # If pressed the left button
            if i_event.button() == Qt.MouseButton.LeftButton:
                # Get mouse pos relative to HeaderBar
                # and adjust for horizontal scroll amount
                mousePos = i_watched.mapTo(self, i_event.pos())
                mousePos.setX(mousePos.x() - self.scrollX)
                # If cursor is near a draggable vertical edge
                columnNo, column, edgeX = self._columnBoundaryAtPixelX(mousePos.x())
                if columnNo != None:
                    #
                    self.resize_columnNo = columnNo

                    # Get horizontal distance from mouse to the draggable vertical edge (ie. the right edge of the button being resized)
                    #button = column["headingButton"]
                    #buttonBottomRight = button.mapTo(self, QPoint(button.size().width(), button.size().height()))
                    self.resize_mouseToEdgeOffset = edgeX - mousePos.x()

                    #
                    return True

        elif i_event.type() == QEvent.MouseButtonRelease:
            # If currently resizing and released the left button
            if self.resize_columnNo != None and i_event.button() == Qt.MouseButton.LeftButton:
                # Stop resizing
                self.resize_columnNo = None

                #
                return True

        # Let event continue
        return False

    # + }}}

    def repositionHeadingButtons(self):
        x = 0
        x += self.scrollX  # Adjust for horizontal scroll amount
        y = 0
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                self.columnHeadingButtons[column["id"]].setGeometry(x, y, column["width"], HeaderBar.headingButtonHeight)
            x += column["width"]

    def repositionFilterEdits(self):
        y = HeaderBar.headingButtonHeight

        for filterRow in self.filterRows:
            x = 0
            x += self.scrollX  # Adjust for horizontal scroll amount
            for columnNo, column in enumerate(g_columns):
                if column["filterable"]:
                    filterRow["columnFilterEdits"][column["id"]].setGeometry(x, y, column["width"], HeaderBar.filterRowHeight)
                x += column["width"]

            filterRow["deleteRow_pushButton"].setGeometry(x, y, HeaderBar.filterRowHeight, HeaderBar.filterRowHeight)
            x += HeaderBar.filterRowHeight

            y += HeaderBar.filterRowHeight

        y -= HeaderBar.filterRowHeight
        self.insertRow_pushButton.setGeometry(x, y, HeaderBar.filterRowHeight, HeaderBar.filterRowHeight)

class MyStyledItemDelegate(QStyledItemDelegate):
    def __init__(self, i_parent=None):
        QStyledItemDelegate.__init__(self, i_parent)

    def paint(self, i_painter, i_option, i_index):
        #print(i_painter, i_option, i_index)

        if i_option.state & QStyle.State_Selected:
            i_painter.fillRect(i_option.rect, i_option.palette.highlight())

        if i_index.column() == 2:
            screenshotPath = dbRow_getScreenshotRelativePath(g_dbRows[i_index.row()])
            if screenshotPath != None:
                if hasattr(gamebase, "config_screenshotsBaseDirPath"):
                    pixmap = QPixmap(gamebase.config_screenshotsBaseDirPath + "/" + screenshotPath)
                    i_painter.drawPixmap(i_option.rect, pixmap)
        else:
            QStyledItemDelegate.paint(self, i_painter, i_option, i_index)

class MyTableModel(QAbstractTableModel):
    def __init__(self, i_parent, *args):
        QAbstractTableModel.__init__(self, i_parent, *args)

    def rowCount(self, i_parent):
        if g_dbRows == None:
            return 0
        return len(g_dbRows)

    def columnCount(self, i_parent):
        return len(g_columns)

    #https://stackoverflow.com/questions/7988182/displaying-an-image-from-a-qabstracttablemodel
    #https://forum.qt.io/topic/5195/qtableview-extra-column-space-solved/8
    def data(self, i_index, i_role):
        if not i_index.isValid():
            return None

        # Detail
        if i_index.column() == 0:
            if i_role == Qt.DisplayRole:
                return "+"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Play
        elif i_index.column() == 1:
            if i_role == Qt.DisplayRole:
                if g_dbRows[i_index.row()][g_dbColumnNames.index("Filename")] == None:
                    return ""
                return "▶"
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        # Screenshot
        elif i_index.column() == 2:
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    screenshotPath = g_dbRows[i_index.row()][g_dbColumnNames.index("ScrnshotFilename")]
            #    pixmap = QPixmap(gamebase.config_screenshotsBaseDirPath + "/" + screenshotPath)
            #    return pixmap;
            pass
        # ID
        elif i_index.column() == 3:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("GA_Id")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Name
        elif i_index.column() == 4:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("Name")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Year
        elif i_index.column() == 5:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("Year")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Publisher
        elif i_index.column() == 6:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("Publisher")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Programmer
        elif i_index.column() == 7:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("Programmer")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Parent genre
        elif i_index.column() == 8:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("ParentGenre")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
        # Genre
        elif i_index.column() == 9:
            if i_role == Qt.DisplayRole:
                return g_dbRows[i_index.row()][g_dbColumnNames.index("Genre")]
            elif i_role == Qt.TextAlignmentRole:
                return Qt.AlignLeft

        return None

    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            # Detail
            if i_columnNo == 0:
                pass
            # Play
            elif i_columnNo == 1:
                pass
            # Screenshot
            elif i_columnNo == 2:
                pass
            # ID
            elif i_columnNo == 3:
                return "ID"
            # Name
            elif i_columnNo == 4:
                return "Name"
            # Year
            elif i_columnNo == 5:
                return "Year"
            # Publisher
            elif i_columnNo == 6:
                return "Publisher"
            # Programmer
            elif i_columnNo == 7:
                return "Programmer"
            # Parent genre
            elif i_columnNo == 8:
                return "Parent genre"
            # Genre
            elif i_columnNo == 9:
                return "Genre"

        return None

def getGameInfoDict(i_dbRow):
    """
    Params:
     i_dbRow:
      (list)
    """
    rv = {}
    rv["id"] = i_dbRow[g_dbColumnNames.index("GA_Id")]
    rv["name"] = i_dbRow[g_dbColumnNames.index("Name")]
    rv["year"] = i_dbRow[g_dbColumnNames.index("Year")]
    rv["publisher"] = i_dbRow[g_dbColumnNames.index("Publisher")]

    for columnNo, columnName in enumerate(g_dbColumnNames):
        rv[columnName] = i_dbRow[columnNo]

    return rv

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
        self.verticalHeader().hide()

        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setDefaultSectionSize(200)
        self.horizontalHeader().resizeSection(0, 20)
        self.horizontalHeader().resizeSection(1, 20)
        self.horizontalHeader().resizeSection(2, 300)
        self.horizontalHeader().resizeSection(3, 50)
        self.horizontalHeader().hide()

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # + Context menu {{{

        self.contextMenu = QMenu(self)

        self.contextMenu_filter = QMenu("Filter", self.contextMenu)

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

        self.contextMenu.addMenu(self.contextMenu_filter)

        self.contextMenu.addSeparator()
        action = self.contextMenu.addAction("Copy")
        action.triggered.connect(self.clipboardCopy)
        action.setShortcut(QKeySequence("Ctrl+C"))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # + }}}

        #
        self.clicked.connect(self.onActivatedOrClicked)
        self.activated.connect(self.onActivatedOrClicked)

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

    def onActivatedOrClicked(self, i_modelIndex):
        """
        Params:
         i_modelIndex:
          (QModelIndex)
        """
        if i_modelIndex.column() == 0:
            self.scrollTo(i_modelIndex, QAbstractItemView.PositionAtTop)
            detailPane_show()
            detailPane_populate(i_modelIndex.row())

        elif i_modelIndex.column() == 1:
            rowNo = i_modelIndex.row()
            gamebase.runGame(g_dbRows[rowNo][g_dbColumnNames.index("Filename")],
                             g_dbRows[rowNo][g_dbColumnNames.index("FileToRun")],
                             getGameInfoDict(g_dbRows[rowNo]))

    # + Context menu {{{

    def onCustomContextMenuRequested(self, i_pos):
        self.contextMenu.popup(self.viewport().mapToGlobal(i_pos))

    def contextMenu_filter_item_onTriggered(self, i_combiner, i_comparisonOperation): #, i_checked):
        print("contextMenu_filter_item_onTriggered")
        print(i_comparisonOperation)
        selectedIndex = self.selectionModel().currentIndex()
        selectedValue = self.tableModel.data(selectedIndex, Qt.DisplayRole)

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

        columnId = g_columns[selectedIndex.column()]["id"]
        headerBar.filterRows[-1]["columnFilterEdits"][columnId].setText(formattedCriteria)
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
        allColumnsWidth = sum([column["width"]  for column in g_columns])
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

# Window layout
mainWindow_layout = QVBoxLayout()
mainWindow_layout.setSpacing(0)
mainWindow_layout.setContentsMargins(0, 0, 0, 0)
mainWindow.setLayout(mainWindow_layout)

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

#
gameTable = QWidget()
mainWindow_layout.addWidget(gameTable)
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

# Create header
headerBar = HeaderBar()
headerBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
gameTable_layout.addWidget(headerBar)

def headerBar_onFilterChange():
    queryDb()
    tableView.requery()
headerBar.filterChange.connect(headerBar_onFilterChange)

splitter = QSplitter(Qt.Vertical)
gameTable_layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

def splitter_onSplitterMoved(i_pos, i_index):
    # If detail pane has been dragged closed,
    # call detailPane_hide() to keep track
    if splitter.sizes()[1] == 0:
        detailPane_hide()
splitter.splitterMoved.connect(splitter_onSplitterMoved)

# Create table
tableView = MyTableView()
splitter.addWidget(tableView)
splitter.setStretchFactor(0, 0)  # Don't stretch table view when window is resized
tableView.setItemDelegate(MyStyledItemDelegate())

for columnNo, column in enumerate(g_columns):
    tableView.horizontalHeader().resizeSection(columnNo, column["width"])

# Create detail pane
class DetailPane(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        QShortcut(QKeySequence("Escape"), self, activated=self.escapeShortcut_onActivated)
        #QShortcut(QKeySequence("Page Up"), self, activated=self.pageUpShortcut_onActivated)
    def escapeShortcut_onActivated(self):
        detailPane_hide()
    #def pageUpShortcut_onActivated(self):
    #    detailPane_hide()

detailPane_widget = DetailPane()
detailPane_widget.setProperty("class", "detailPane")
splitter.addWidget(detailPane_widget)
splitter.setStretchFactor(1, 1)  # Do stretch detail pane when window is resized
detailPane_layout = QHBoxLayout()
detailPane_layout.setSpacing(0)
detailPane_layout.setContentsMargins(0, 0, 0, 0)
detailPane_widget.setLayout(detailPane_layout)

def detailPane_show():
    # Position splitter so that the table view shows exactly one row
    topPaneHeight = 200  # Row height
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

detailPane_margin = QPushButton("x")
detailPane_margin.clicked.connect(detailPane_hide)
#detailPane_margin = QWidget()
detailPane_layout.addWidget(detailPane_margin)
#detailPane_margin_layout = QVBoxLayout()
#detailPane_margin.setLayout(detailPane_margin_layout)

detailPane_margin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
#detailPane_margin.setGeometry(0, 0, g_columns[0]["width"], 100)
detailPane_margin.setFixedWidth(g_columns[0]["width"])
#print(g_columns[0]["width"])

#detailPane_margin_layout.addWidget(QPushButton())
#detailPane_margin_layout.addWidget(QPushButton())
#detailPane_margin_layout.addWidget(QPushButton())

detailPane_webEngineView = QWebEngineView()
detailPane_webEngineView.setProperty("class", "webEngineView")
detailPane_layout.addWidget(detailPane_webEngineView)

def detailPane_populate(i_rowNo):
    """
    Params:
     i_rowNo:
      (int)
    """
    row = g_dbRows[i_rowNo]

    html = ""

    html += '<link rel="stylesheet" type="text/css" href="file://' + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + '/detail_pane.css">'

    # Insert screenshots after the first one
    supplementaryScreenshotRelativePaths = dbRow_getSupplementaryScreenshotPaths(row)
    for relativePath in supplementaryScreenshotRelativePaths:
        screenshotUrl = getScreenshotUrl(relativePath)
        if screenshotUrl != None:
            html += '<img src="' + screenshotUrl + '">'

    # If this game is a clone,
    # insert a link to the original
    if "CloneOfName" in g_dbColumnNames and row[g_dbColumnNames.index("CloneOfName")] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += 'Clone of: '

        html += '<a href="#">' + row[g_dbColumnNames.index("CloneOfName")] + '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #
        #    for (var columnNo = 0, columnCount = g_columns.length; columnNo < columnCount; ++columnNo)
        #    {
        #        var column = g_columns[columnNo];
        #
        #        if (column.filterable)
        #        {
        #            if (column.id == "name")
        #                column.headerFilter.setValue(i_row.CloneOfName);
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
    if row[g_dbColumnNames.index("MemoText")] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += row[g_dbColumnNames.index("MemoText")]
        html += '</p>'

    # Insert comment
    if row[g_dbColumnNames.index("Comment")] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += row[g_dbColumnNames.index("Comment")]
        html += '</p>'

    # Insert weblink(s)
    if "WebLink_Name" in g_dbColumnNames and row[g_dbColumnNames.index("WebLink_Name")] != None:
        html += '<p style="white-space: pre-wrap;">'

        html += row[g_dbColumnNames.index("WebLink_Name")] + ": "
        url = row[g_dbColumnNames.index("WebLink_URL")]
        html += '<a target="_blank" href="' + url + '">'
        html += url
        html += '</a>'
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #    electron.shell.openExternal(this.href);
        #});

        # If it's a World Of Spectrum link then insert a corresponding Spectrum Computing link
        if "WebLink_Name" in g_dbColumnNames and row[g_dbColumnNames.index("WebLink_Name")] == "WOS":
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
    sql = """
SELECT
 Extras.EX_Id,
 Extras.Name,
 Extras.Path
FROM
 Extras
WHERE
 Extras.GA_Id = """ + str(row[g_dbColumnNames.index("GA_Id")]) + """
ORDER BY
 Extras.DisplayOrder"""

    dbCursor = g_db.execute(sql)

    extrasColumnNames = [column[0]  for column in dbCursor.description]
    extrasRows = dbCursor.fetchall()

    # Seperate extras which are and aren't images
    imageRows = []
    nonImageRows = []
    for extrasRow in extrasRows:
        path = extrasRow[extrasColumnNames.index("Path")]
        if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg") or path.lower().endswith(".gif") or path.lower().endswith(".png"):
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

            html += '<a href="extra:///' + nonImageRow[extrasColumnNames.index("Path")] + '">'
            html += nonImageRow[extrasColumnNames.index("Name")]
            html += '</a>'

        html += "</div>"


    # For each image, insert an image
    if len(imageRows) > 0:
        html += '<div id="imageExtras">'

        for imageRowNo, imageRow in enumerate(imageRows):
            #print("imageRow: " + str(imageRow))
            #var cell = document.createElement("div");

            html += '<a href="extra:///' + imageRow[extrasColumnNames.index("Path")] + '" style="display: inline-block; text-align: center;">'
            if hasattr(gamebase, "config_extrasBaseDirPath"):
                html += '<img src="file://' + gamebase.config_extrasBaseDirPath + "/" + imageRow[extrasColumnNames.index("Path")] + '" style="height: 300px;">'
            #html += '<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" style="height: 300px;">'
            html += '<div>' + imageRow[extrasColumnNames.index("Name")] + '</div>'
            html += '</a>'

            #cell.appendChild(link);

        html += "</div>"

    print(html)

    #detailPane_webEngineView.setHtml(html, QUrl("file:///"))
    # Load HTML into a QWebEnginePage with a handler for link clicks
    class WebEnginePage(QWebEnginePage):
        def acceptNavigationRequest(self, i_qUrl, i_requestType, i_isMainFrame):
            if i_requestType == QWebEnginePage.NavigationTypeLinkClicked:
                #print(i_isMainFrame)

                # If it's a link to an extra,
                # pass it to the config file's runExtra()
                url = i_qUrl.toString()
                if url.startswith("extra:///"):
                    gamebase.runExtra(url[9:],
                                      getGameInfoDict(g_dbRows[i_rowNo]))
                # Else if it's a normal link,
                # open it with the default browser
                else:
                    QDesktopServices.openUrl(i_qUrl)

                # Refuse navigation
                return False

            else:
                return True
    webEnginePage = WebEnginePage(detailPane_webEngineView)
    webEnginePage.setHtml(html, QUrl("file:///"))
    # Let background of application show through to stop white flash on page loads
    webEnginePage.setBackgroundColor(Qt.transparent)

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
queryDb()
tableView.requery()

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
