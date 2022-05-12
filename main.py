#!/usr/bin/python


# Python std
import sys
import sqlite3
import functools
import os.path

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import frontend



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

def getColumnByHeaderButton(i_headerButton):
    """
    Params:
     i_headerButton:
      (HeaderButton)
    Returns:
     (tuple)
     Tuple has elements:
      0:
       (int)
      1:
       (Column)
    """
    for columnNo, column in enumerate(g_columns):
        if "headerButton" in column and column["headerButton"] == i_headerButton:
            return columnNo, column
    return None, None

# + }}}

# + Screenshot file/URL resolving {{{

def getScreenshotAbsolutePath(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     (str)
    """
    return gamebase.config_screenshotsBaseDirPath + "/" + i_relativePath

def getScreenshotUrl(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     (str)
    """
    i_relativePath = i_relativePath.replace(" ", "%20")
    i_relativePath = i_relativePath.replace("#", "%23")
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
    filters = []

    for column in g_columns:
        if column["filterable"]:
            value = column["filterControl"].text()
            value = value.strip()
            if value != "":
                # TODO: escape '%', "'" etc in value

                #value = value.toUpperCase();
                #filters.push("UPPER(" + column["qualifiedDbFieldName"] + ") LIKE '%" + value + "%'")
                filters.append(column["qualifiedDbFieldName"] + " LIKE '%" + value + "%'")

    if len(filters) > 0:
        sql += "\nWHERE " + (" AND ".join(filters))

    # ORDER BY
    if header.sort_columnNo != None:
        sql += "\nORDER BY "
        sql += g_columns[header.sort_columnNo]["qualifiedDbFieldName"]
        if header.sort_direction == -1:
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
     (list of string)
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
                    if not os.path.exists(screenshotAbsolutePath):
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


class Header3(QWidget):
    """
    A top row of buttons to act as table headings and controls for column resizing and sorting,
    and a second row of text box controls for entering filter criteria.
    """
    # Within this many pixels either side of a vertical boundary between header buttons, allow dragging to resize a column.
    resizeMargin = 10
    # Minimum number of pixels that a column can be resized to by dragging.
    minimumColumnWidth = 30

    # Emitted after the text in one of the filter text boxes is changed
    filterChange = Signal(int)

    #print(tableView.geometry())
    #print(tableView.frameGeometry())
    #print(tableView.contentsMargins())
    #print(tableView.contentsRect())
    #tableView.horizontalHeader().resizeSection(self.parent().resize_columnNo, newWidth)

    def __init__(self, i_parent=None):
        QWidget.__init__(self, i_parent)

        # Allow this custom widget derived from a QWidget to be fully styled by stylesheets
        # https://stackoverflow.com/a/49179582
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setFixedHeight(59)

        #pal = QPalette()
        #pal.setColor(QPalette.Window, Qt.red)
        #self.setPalette(pal)
        #self.setAutoFillBackground(True)

        #self.container = QWidget(self)
        #self.container.setGeometry(0, 0, 800, 90)

        #self.setStyleSheet("* { border: 1px solid red; }");

        # Resizing columns by mouse dragging
        self.installEventFilter(self)
        #  Receive mouse move events even if button isn't held down
        self.setMouseTracking(True)
        #  State used while resizing
        self.resize_columnNo = None
        self.resize_mouseToEdgeOffset = None

        # State of column sorting
        self.sort_columnNo = None
        self.sort_direction = None

        class HeaderButton(QPushButton):
            def __init__(self, i_text, i_hasBorder, i_parent=None):
                QPushButton.__init__(self, i_text, i_parent)

                if not i_hasBorder:
                    self.setStyleSheet("QPushButton { border: none; }");
                    self.setFlat(True)
                    self.setFocusPolicy(Qt.NoFocus)
                    #self.setStyleSheet("QPushButton { background-color: red; color: black;}");

                # Receive mouse move events even if button isn't held down
                # and install event filter to let parent Header3 see all events first
                self.setMouseTracking(True)
                self.installEventFilter(self.parent())

        # Create widgets (HeaderButton and QLineEdit objects) for columns
        global g_columns
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                # Create button
                column["headerButton"] = HeaderButton(column["headingText"], column["filterable"], self)
                # Set its basic properties (apart from position)
                column["headerButton"].clicked.connect(functools.partial(self.button_onClicked, columnNo))

            if column["filterable"]:
                # Create lineedit
                column["filterControl"] = QLineEdit(self)
                # Set its basic properties (apart from position)
                column["filterControl"].editingFinished.connect(functools.partial(self.lineEdit_onEditingFinished, columnNo))

        # Initially set all widget positions
        self.repositionHeaderButtons()
        self.repositionLineEdits()

    #def sizeHint(self):
    #    return QSize(10000, 59)

    def button_onClicked(self, i_columnNo):
        # If column isn't sortable,
        # bail
        if not g_columns[i_columnNo]["sortable"]:
            return

        # Remove old sort arrow from heading
        if self.sort_columnNo != None:
            headerButton = g_columns[self.sort_columnNo]["headerButton"]
            if headerButton.text().endswith("▲") or headerButton.text().endswith("▼"):
                headerButton.setText(g_columns[self.sort_columnNo]["headingText"])

        #
        if self.sort_columnNo == i_columnNo:
            self.sort_direction = -self.sort_direction
        else:
            self.sort_direction = 1
            self.sort_columnNo = i_columnNo

        # Add new sort arrow to heading
        headerButton = g_columns[self.sort_columnNo]["headerButton"]
        if self.sort_direction > 0:
            headerButton.setText(headerButton.text() + "  ▲")
        else:
            headerButton.setText(headerButton.text() + "  ▼")

        #
        queryDb()
        tableView.requery()

    def lineEdit_onEditingFinished(self, i_columnNo):
        self.filterChange.emit(i_columnNo)

    # + Resizing columns by mouse dragging {{{

    def _columnBoundaryAtPixelX(self, i_x):
        x = 0

        for columnNo, column in enumerate(g_columns):
            columnEdgeX = x + column["width"]
            if abs(i_x - columnEdgeX) <= Header3.resizeMargin:
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
                # Get mouse pos relative to Header3
                mousePos = i_watched.mapTo(self, i_event.pos())
                #
                columnNo, _, _ = self._columnBoundaryAtPixelX(mousePos.x())
                if columnNo != None:
                    self.setCursor(Qt.SizeHorCursor)
                else:
                    self.unsetCursor()
            # Else if currently resizing,
            # do the resize
            else:
                # Get mouse pos relative to Header3
                mousePos = i_watched.mapTo(self, i_event.pos())
                # Get new width
                newRightEdge = mousePos.x() + self.resize_mouseToEdgeOffset
                columnLeft = sum([column["width"]  for column in g_columns[0 : self.resize_columnNo]])
                newWidth = newRightEdge - columnLeft
                if newWidth < Header3.minimumColumnWidth:
                    newWidth = Header3.minimumColumnWidth
                # Resize column
                column = g_columns[self.resize_columnNo]
                column["width"] = newWidth

                # Move/resize buttons and lineedits
                self.repositionHeaderButtons()
                self.repositionLineEdits()
                #
                tableView.horizontalHeader().resizeSection(self.resize_columnNo, newWidth)

                return True

        elif i_event.type() == QEvent.MouseButtonPress:
            # If pressed the left button
            if i_event.button() == Qt.MouseButton.LeftButton:
                # Get mouse pos relative to Header3
                mousePos = i_watched.mapTo(self, i_event.pos())
                # If cursor is near a draggable vertical edge
                columnNo, column, edgeX = self._columnBoundaryAtPixelX(mousePos.x())
                if columnNo != None:
                    #
                    self.resize_columnNo = columnNo

                    # Get horizontal distance from mouse to the draggable vertical edge (ie. the right edge of the button being resized)
                    #button = column["headerButton"]
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

    def repositionHeaderButtons(self):
        x = 0
        y = 0
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                button = column["headerButton"]
                button.setGeometry(x, y, column["width"], 30)
            x += column["width"]

    def repositionLineEdits(self):
        #for columnNo, column in enumerate(g_columns):
        #    if column["filterable"]:
        #        button = column["headerButton"]
        #        column["filterControl"].setGeometry(button.geometry().left(), button.geometry().bottom(), button.width(), 30)
        x = 0
        y = 30
        for columnNo, column in enumerate(g_columns):
            if column["filterable"]:
                column["filterControl"].setGeometry(x, y, column["width"], 30)
            x += column["width"]


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

        #
        def onClick(i_modelIndex):
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
        self.clicked.connect(onClick)

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

    def scrollContentsBy(self, i_dx, i_dy):
        # If the table view is scrolled horizontally,
        # scroll external header by the same amount
        QTableView.scrollContentsBy(self, i_dx, i_dy)
        header.scroll(i_dx, 0)

    def requery(self):
        self.tableModel.modelReset.emit()

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
mainWindow.setWindowTitle(gamebase.config_title + " - GameBase")

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
header = Header3()
header.setGeometry(0, 0, 10000, 100)  # TODO resize this exactly instead of excessively, not that it matters
header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
gameTable_layout.addWidget(header)

def header_onFilterChange(i_columnNo):
    queryDb()
    tableView.requery()
header.filterChange.connect(header_onFilterChange)

#headerView = Header3()
#mainWindow_layout.addWidget(headerView)

#headerView = QTableView()
#headerModel = HeaderModel(None)
#headerView.setModel(headerModel)
#mainWindow_layout.addWidget(headerView)

splitter = QSplitter(Qt.Vertical)
gameTable_layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# Create table
tableView = MyTableView()
splitter.addWidget(tableView)
tableView.setItemDelegate(MyStyledItemDelegate())

for columnNo, column in enumerate(g_columns):
    tableView.horizontalHeader().resizeSection(columnNo, column["width"])

# Create detail pane
detailPane_widget = QWidget()
detailPane_widget.setProperty("class", "detailPane")
splitter.addWidget(detailPane_widget)
detailPane_layout = QHBoxLayout()
detailPane_layout.setSpacing(0)
detailPane_layout.setContentsMargins(0, 0, 0, 0)
detailPane_widget.setLayout(detailPane_layout)

def detailPane_show():
    splitter.setSizes([200, splitter.geometry().height() - 200])
    tableView.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

def detailPane_hide():
    splitter.setSizes([splitter.geometry().height(), 0])
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

    html += '<link rel="stylesheet" type="text/css" href="file:///home/daniel/docs/code/python/gamebase/detail_pane.css">'

    #
    supplementaryScreenshotRelativePaths = dbRow_getSupplementaryScreenshotPaths(row);
    for relativePath in supplementaryScreenshotRelativePaths:
        html += '<img src="' + getScreenshotUrl(relativePath) + '">'

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
        #                column.filterControl.setValue(i_row.CloneOfName);
        #            else
        #                column.filterControl.setValue("");
        #        }
        #    }
        #
        #    queryDb();
        #    //showDetailPane(0);
        #    g_dynamicTable.scrollTop = 0;
        #});
        html += '</p>'

    if row[g_dbColumnNames.index("MemoText")] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += row[g_dbColumnNames.index("MemoText")]
        html += '</p>'

    if row[g_dbColumnNames.index("Comment")] != None:
        html += '<p style="white-space: pre-wrap;">'
        html += row[g_dbColumnNames.index("Comment")]
        html += '</p>'

    if "WebLink_Name" in g_dbColumnNames and row[g_dbColumnNames.index("WebLink_Name")] != None:
        #var url = row.WebLink_URL;
        #
        #var container = document.createElement("p");
        #container.appendChild(document.createTextNode(row.WebLink_Name + ": "));
        #
        #var link = document.createElement("a");
        #link.setAttribute("href", url);
        #//link.setAttribute("target", "_blank");
        #link.appendChild(document.createTextNode(url));
        #link.addEventListener("click", function (i_event) {
        #    i_event.preventDefault();
        #    electron.shell.openExternal(this.href);
        #});
        #container.appendChild(link);
        #g_detailPane.appendChild(container);
        #
        #if (row.WebLink_Name == "WOS")
        #{
        #    url = url.replace("http://www.worldofspectrum.org/infoseekid.cgi?id=", "https://spectrumcomputing.co.uk/entry/");
        #
        #    //container.appendChild(document.createTextNode(" | "));
        #    var separator = document.createElement("span");
        #    separator.style.marginLeft = "8px";
        #    separator.style.marginRight = "8px";
        #    separator.style.borderLeft = "1px dotted #666";
        #
        #    container.appendChild(separator);
        #
        #    container.appendChild(document.createTextNode("Spectrum Computing: "));
        #
        #    var link = document.createElement("a");
        #    link.setAttribute("href", url);
        #    //link.setAttribute("target", "_blank");
        #    link.appendChild(document.createTextNode(url));
        #    link.addEventListener("click", function (i_event) {
        #        i_event.preventDefault();
        #        electron.shell.openExternal(this.href);
        #    });
        #    container.appendChild(link);
        pass


    #
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

            html += '<a href="extra:///' + nonImageRow[extrasColumnNames.index("Path")] + '>'
            html += nonImageRow[extrasColumnNames.index("Name")]
            html += '</a>'

        html += "</div>"


    # For each image, insert an image
    if len(imageRows) > 0:
        html += '<div id="imageExtras">'

        for imageRowNo, imageRow in enumerate(imageRows):
            print("imageRow: " + str(imageRow))
            #var cell = document.createElement("div");

            html += '<a href="extra:///' + imageRow[extrasColumnNames.index("Path")] + '" style="display: inline-block; text-align: center;">'
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



# Enter Qt application main loop
exitCode = application.exec_()
sys.exit(exitCode)
