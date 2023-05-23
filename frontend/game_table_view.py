# Python std
import sqlite3
import functools
import copy
import random
import os
import zipfile
import tempfile

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras
import columns
import db
import frontend_utils
#import utils
import sql
import gamebase
import settings


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

def screenshotPathToPixmap(i_screenshotPath):
    """
    Params:
     i_screenshotPath:
      (str)

    Returns:
     Either (QPixmap)
     or (None)
    """
    # If it's an ordinary path to an image (ie. not referencing a zip file member),
    # simply construct and return the pixmap using that path
    zipExtensionPos = i_screenshotPath.lower().find(".zip/")
    if zipExtensionPos == -1:
        return QPixmap(i_screenshotPath)

    # Else if the path is referencing a zip file member,
    # extract the file and construct the pixmap from that data
    zipFilePath = i_screenshotPath[:zipExtensionPos + 4]
    memberPath = i_screenshotPath[zipExtensionPos + 5:]

    pixmap = QPixmap()
    try:
        pixmap.loadFromData(gamebase.getZipMemberBytes(zipFilePath, memberPath))
        return pixmap
    except:
        return None

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

        # If painting screenshot column
        if column["id"].startswith("pic[") and column["id"].endswith("]"):
            picNo = int(column["id"][4:-1])

            screenshotFullPath = gamebase.dbRow_nthScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            if screenshotFullPath != None:
                pixmap = screenshotPathToPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
                i_painter.drawPixmap(destRect, pixmap)

        # Else if painting random screenshot column
        elif column["id"].startswith("random_pic[") and column["id"].endswith("]"):
            picNo = int(column["id"][11:-1])

            screenshotFullPath = gamebase.dbRow_nthRandomScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            if screenshotFullPath != None:
                pixmap = screenshotPathToPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
                i_painter.drawPixmap(destRect, pixmap)

        # Else if painting schema column
        elif column["id"] == "schema":
            schemaName = self.parent().dbRows[i_index.row()]["SchemaName"]

            #i_option.rect.setTop(i_option.rect.top() + 16)

            # If the adapter specifies a system image,
            # draw it
            adapterId = gamebase.schemaAdapterIds[schemaName]
            gamebaseImageFilePath = gamebase.gamebaseImageFilePath(adapterId)
            if gamebaseImageFilePath != None:
                pixmap = QPixmap(gamebaseImageFilePath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect.adjusted(8, 8, -8, -8))))
                i_painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
                i_painter.drawPixmap(destRect, pixmap)
            # Else draw some text
            else:
                # If the adapter specifies a title, use that,
                # else use the symbolic schema name
                if hasattr(gamebase.adapters[adapterId]["module"], "config_title"):
                    text = gamebase.adapters[adapterId]["module"].config_title
                else:
                    text = schemaName

                # Draw it rotated 90 degrees and centred in cell
                i_painter.translate(i_option.rect.x(), i_option.rect.y() + i_option.rect.height())
                i_painter.rotate(-90)
                i_painter.drawText(QRect(0, 0, i_option.rect.height(), i_option.rect.width()), Qt.AlignVCenter|Qt.AlignHCenter|Qt.TextWordWrap, text)
                i_painter.resetTransform()

        # Else if painting musician photo column
        elif column["id"] == "musician_photo":
            photoFullPath = gamebase.dbRow_photoFullPath(self.parent().dbRows[i_index.row()])
            if photoFullPath != None:
                pixmap = QPixmap(photoFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.setRenderHints(QPainter.SmoothPixmapTransform, True)
                i_painter.drawPixmap(destRect, pixmap)

        # Else if painting any other column,
        # fall back to the default behaviour (ie. will use data() from table model)
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
        elif column["id"].startswith("pic[") and column["id"].endswith("]"):
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    picNo = int(column["id"][4:-1])
            #
            #    screenshotFullPath = gamebase.dbRow_nthScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            #    if screenshotFullPath != None:
            #        return screenshotPathToPixmap(screenshotFullPath)
            pass
        # Random screenshot
        elif column["id"].startswith("random_pic[") and column["id"].endswith("]"):
            # (Done via delegate)
            #if i_role == Qt.DecorationRole:
            #    picNo = int(column["id"][11:-1])
            #
            #    screenshotFullPath = gamebase.dbRow_nthRandomScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            #    if screenshotFullPath != None:
            #        return screenshotPathToPixmap(screenshotFullPath)
            pass
        #
        else:
            tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
            # Enum field
            if "type" in tableColumnSpec and tableColumnSpec["type"] == "enum":
                if i_role == MyTableModel.FilterRole:
                    return self.parent().dbRows[i_index.row()][tableColumnSpec["dbIdentifiers"][0]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][tableColumnSpec["dbIdentifiers"][0]]
                    if value in tableColumnSpec["enumMap"]:
                        value = str(value) + ": " + tableColumnSpec["enumMap"][value]
                    return value
                elif i_role == Qt.TextAlignmentRole:
                    if column["textAlignment"] == "center":
                        return Qt.AlignCenter
                    elif column["textAlignment"] == "left":
                        return Qt.AlignLeft
            # Game ID field
            if "type" in tableColumnSpec and tableColumnSpec["type"] == "gameId":
                if i_role == MyTableModel.FilterRole:
                    return self.parent().dbRows[i_index.row()][tableColumnSpec["dbIdentifiers"][0]]
                elif i_role == Qt.DisplayRole:
                    value = self.parent().dbRows[i_index.row()][tableColumnSpec["dbIdentifiers"][0]]
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
                    return self.parent().dbRows[i_index.row()][tableColumnSpec["dbIdentifiers"][0]]
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
            return column["headingName"]

        return None

class GameTableView(QTableView):
    def __init__(self, i_extraHorizontalScrollSpaceNeeded, i_parent=None):
        """
        Params:
         i_extraHorizontalScrollSpaceNeeded:
          (int)
        """
        QTableView.__init__(self, i_parent)

        self.extraHorizontalScrollSpaceNeeded = i_extraHorizontalScrollSpaceNeeded

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
        #print("aaaaaaa")
        self.setModel(self.tableModel)

        self.setItemDelegate(MyStyledItemDelegate(self))

        # Set row height
        if "rowHeight" not in settings.viewSettings:
            settings.viewSettings["rowHeight"] = 200
        #self.rowHeight(200)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(settings.viewSettings["rowHeight"])
        self.verticalHeader().setMinimumSectionSize(2)
        self.verticalHeader().hide()

        #self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        #self.horizontalHeader().setDefaultSectionSize(200)
        #self.horizontalHeader().resizeSection(0, 20)
        #self.horizontalHeader().resizeSection(1, 20)
        #self.horizontalHeader().resizeSection(2, 300)
        #self.horizontalHeader().resizeSection(3, 50)
        self.horizontalHeader().hide()

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # For scroll wheel
        self.singleStepSize = 30
        self.verticalScrollBar().setSingleStep(self.singleStepSize)

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

    def alignItemToTop(self, i_on):
        """
        Params:
         i_on:
          (bool)
        """
        if i_on:
            self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        else:
            self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
            # Reassert singleStepSize (for scroll wheel)
            # since otherwise it gets lost when turning this off
            self.verticalScrollBar().setSingleStep(self.singleStepSize)

    doneQuery = Signal(int)
    # Emitted when
    #  queryDb() has finished a DB query and updated the game list
    #
    # Params:
    #  i_rowCount:
    #   (int)
    #   The new row/game count in the list

    def quickGetSql(self, i_sqlWhereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns=True):
        """
        Params:
         i_whereExpression:
          (str)
         i_sortOperations:
          (list)
          See ColumnNameBar.sort_operations
         i_whereExpressionMightUseNonVisibleColumns:
          (bool)

        Returns:
         (list)
         As returned from getGameList_getSql().
        """
        # Get IDs of visible table columns
        tableColumnSpecIds = [column["id"]  for column in columns.tableColumn_getBySlice()]

        #
        connectionsAndSqlTexts = db.getGameList_getSql(tableColumnSpecIds, i_sqlWhereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns)
        #print(connectionsAndSqlTexts)
        # If no SQL to execute (because no databases are open)
        #if len(connectionsAndSqlTexts) == 0:
        # Else if we have some SQL
        #else:
        #self.dbColumnNames, self.dbRows = db.getGameList_executeSqlAndFetchAll(connectionsAndSqlTexts, i_sortOperations)
        return connectionsAndSqlTexts

    def queryDb(self, i_whereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns=True):
        """
        Params:
         i_whereExpression:
          (str)
         i_sortOperations:
          (list)
          See ColumnNameBar.sort_operations
         i_whereExpressionMightUseNonVisibleColumns:
          (bool)
        """
        # Get IDs of visible table columns
        tableColumnSpecIds = [column["id"]  for column in columns.tableColumn_getBySlice()]

        #
        connectionsAndSqlTexts = db.getGameList_getSql(tableColumnSpecIds, i_whereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns)
        #print(connectionsAndSqlTexts)
        # If no SQL to execute (because no databases are open)
        if len(connectionsAndSqlTexts) == 0:
            self.dbColumnNames = []
            self.dbRows = []
        # Else if we have some SQL
        else:
            # Execute
            try:
                self.dbColumnNames, self.dbRows = db.getGameList_executeSqlAndFetchAll(connectionsAndSqlTexts, i_sortOperations)
            except sqlite3.OperationalError as e:
                # TODO if i_whereExpressionMightUseNonVisibleColumns and error was 'no such column', maybe retry with SELECT * and all tables (see getGameRecord())
                raise

        self.doneQuery.emit(len(self.dbRows))

    def selectedGameSchemaNameAndId(self):
        """
        Returns:
         (tuple)
         Tuple has elements:
          0:
           (str)
           Schema name
          1:
           (int)
           Game ID
        """
        selectedIndex = self.selectionModel().currentIndex()
        dbRow = self.dbRows[selectedIndex.row()]
        return (dbRow[self.dbColumnNames.index("SchemaName")], dbRow[self.dbColumnNames.index("Games.GA_Id")])

    def refilter(self, i_sqlWhereExpression, i_sortOperations):
        """
        Params:
         i_sqlWhereExpression:
          (str)
         i_sortOperations:
          (list)
          See ColumnNameBar.sort_operations

        Returns:
         (bool)
        """
        # Remember what game is currently selected and where on the screen the row is
        selectedIndex = self.selectionModel().currentIndex()
        if selectedIndex.row() < 0 or selectedIndex.row() >= len(self.dbRows):
            selectedGameSchemaNameAndId = None
        else:
            selectedGameSchemaNameAndId = self.selectedGameSchemaNameAndId()
            selectedRowTopY = self.rowViewportPosition(selectedIndex.row())

        # Query database
        sqlValid = True
        try:
            self.queryDb(i_sqlWhereExpression, i_sortOperations)
        #except sql.SqlParseError as e:
        #    sqlValid = False
        #
        #    import traceback
        #    print(traceback.format_exc())
        #
        #    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
        #    messageBox.setText("<big><b>In SQL WHERE expression:</b></big><pre>" + "\n".join(e.args) + "</pre>")
        #    messageBox.resizeToContent()
        #    messageBox.exec()
        except sqlite3.OperationalError as e:
            sqlValid = False

            import traceback
            print(traceback.format_exc())

            messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
            messageBox.setText("<big><b>In SQL WHERE expression:</b></big><pre>" + "\n".join(traceback.format_exception_only(e.__class__, e)) + "</pre>")
            messageBox.resizeToContent()
            messageBox.exec()

        # Update table widget data
        self.requery()

        # If no Gamebases/databases loaded,
        # stop here
        if len(self.dbColumnNames) == 0:
            return True

        # If a game was previously selected,
        # search for new row number of that game
        # and if found, scroll to put that game in the same screen position it previously was
        if selectedGameSchemaNameAndId != None:
            # [TODO use findGameWithSchemaNameAndId() ?...]
            schemaNameColumnNo = self.dbColumnNames.index("SchemaName")
            idColumnNo = self.dbColumnNames.index("Games.GA_Id")
            newDbRowNo = None
            for dbRowNo, dbRow in enumerate(self.dbRows):
                if dbRow[schemaNameColumnNo] == selectedGameSchemaNameAndId[0] and dbRow[idColumnNo] == selectedGameSchemaNameAndId[1]:
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
        # [Disabled for now because for some reason can also get here when starting to use the scroll bar
        #  and may cause a disorienting jump]
        #self.scrollTo(selectedIndex)

    def scrollToSelection(self):
        self.scrollTo(self.selectionModel().currentIndex())

    def selectCellInColumnWithId(self, i_id):
        """
        Params:
         i_id:
          (str)
        """
        columnNo = columns.tableColumn_idToPos(i_id)
        selectedIndex = self.selectionModel().currentIndex()
        self.selectionModel().setCurrentIndex(self.selectionModel().model().index(selectedIndex.row(), columnNo), QItemSelectionModel.ClearAndSelect)

    adapterRunFunctionFinished = Signal()
    # Emitted when
    #  An adapter run...() command is returned from

    externalApplicationOpened = Signal()
    # Emitted when
    #  utils.openInDefaultApplication() is returned from

    requestDetailPane = Signal(bool, QModelIndex)
    # Params:
    #  i_withKeyboardAction:
    #   (bool)
    #  i_modelIndex:
    #   (QModelIndex)

    def onActivatedOrClicked(self, i_withKeyboardAction, i_modelIndex):
        """
        Params:
         i_withKeyboardAction:
          (bool)
         i_modelIndex:
          (QModelIndex)
        """
        columnId = columns.tableColumn_getByPos(i_modelIndex.column())["id"]

        if columnId == "detail":
            self.requestDetailPane.emit(i_withKeyboardAction, i_modelIndex)

        elif columnId == "play":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = db.getGameRecord(self.dbRows[rowNo]["SchemaName"], gameId)
            gameRecord = db.DbRecordDict(gameRecord)

            adapterId = gamebase.schemaAdapterIds[gameRecord["SchemaName"]]
            try:
                gamebase.adapters[adapterId]["module"].runGame(gameRecord["Games.Filename"], gameRecord["Games.FileToRun"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
                messageBox.setText("<big><b>In runGame():</b></big><pre>" + traceback.format_exc() + "</pre>")
                messageBox.resizeToContent()
                messageBox.exec()

            self.adapterRunFunctionFinished.emit()

        elif columnId == "music":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = db.getGameRecord(self.dbRows[rowNo]["SchemaName"], gameId)
            gameRecord = db.DbRecordDict(gameRecord)

            adapterId = gamebase.schemaAdapterIds[gameRecord["SchemaName"]]
            try:
                gamebase.adapters[adapterId]["module"].runMusic(gameRecord["Games.SidFilename"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
                messageBox.setText("<big><b>In runMusic():</b></big><pre>" + traceback.format_exc() + "</pre>")
                messageBox.resizeToContent()
                messageBox.exec()

            self.adapterRunFunctionFinished.emit()

        # Screenshot
        elif columnId.startswith("pic[") and columnId.endswith("]"):
            picNo = int(columnId[4:-1])

            rowNo = i_modelIndex.row()
            screenshotFullPath = gamebase.dbRow_nthScreenshotFullPath(self.dbRows[rowNo], picNo)
            if screenshotFullPath != None:
                zipExtensionPos = screenshotFullPath.lower().find(".zip/")
                if zipExtensionPos == -1:
                    frontend_utils.openInDefaultApplication(screenshotFullPath)
                    self.externalApplicationOpened.emit()
                else:
                    zipFilePath = screenshotFullPath[:zipExtensionPos + 4]
                    memberPath = screenshotFullPath[zipExtensionPos + 5:]

                    # (Re-)create temporary directory
                    # and extract image file to it
                    tempDirPath = tempfile.gettempdir() + "/gamebase/images"
                    frontend_utils.createTree(tempDirPath)
                    zipFile = zipfile.ZipFile(zipFilePath)
                    zipFile.extract(memberPath, tempDirPath)

                    #
                    frontend_utils.openInDefaultApplication(tempDirPath + os.sep + memberPath)
                    self.externalApplicationOpened.emit()

        # Random screenshot
        elif columnId.startswith("random_pic[") and columnId.endswith("]"):
            picNo = int(columnId[11:-1])

            rowNo = i_modelIndex.row()
            screenshotFullPath = gamebase.dbRow_nthRandomScreenshotFullPath(self.dbRows[rowNo], picNo)
            if screenshotFullPath != None:
                frontend_utils.openInDefaultApplication(screenshotFullPath)
                self.externalApplicationOpened.emit()

        # Musician photo
        elif columnId == "musician_photo":
            rowNo = i_modelIndex.row()
            photoFullPath = gamebase.dbRow_photoFullPath(self.dbRows[rowNo])
            if photoFullPath != None:
                frontend_utils.openInDefaultApplication(photoFullPath)
                self.externalApplicationOpened.emit()

        else:
            tableColumnSpec = columns.tableColumnSpec_getById(columnId)
            if "type" in tableColumnSpec and tableColumnSpec["type"] == "gameId":
                # Get the target game ID
                rowNo = i_modelIndex.row()
                schemaName = self.dbRows[rowNo][self.dbColumnNames.index("SchemaName")]
                gameId = self.dbRows[rowNo][self.dbColumnNames.index(tableColumnSpec["dbIdentifiers"][0])]
                if gameId != 0:
                    self.selectGameWithSchemaNameAndId(schemaName, gameId)

    def findGameWithSchemaNameAndId(self, i_schemaName, i_id):
        """
        Params:
         i_schemaName:
          (str)
         i_id:
          (int)
        """
        schemaNameColumnNo = self.dbColumnNames.index("SchemaName")
        idColumnNo = self.dbColumnNames.index("Games.GA_Id")
        for rowNo, row in enumerate(self.dbRows):
            if row[schemaNameColumnNo] == i_schemaName and row[idColumnNo] == i_id:
                return rowNo
        return None

    requestClearFilter = Signal()

    def selectGameWithSchemaNameAndId(self, i_schemaName, i_gameId):
        """
        Params:
         i_schemaName:
          (str)
         i_id:
          (int)
        """
        # Look for row in table,
        # and if not found then clear filter and look again
        rowNo = self.findGameWithSchemaNameAndId(i_schemaName, i_gameId)
        if rowNo == None:
            self.requestClearFilter.emit()
            rowNo = self.findGameWithSchemaNameAndId(i_schemaName, i_gameId)

        # If found, select it
        if rowNo != None:
            selectedIndex = self.selectionModel().currentIndex()
            self.selectionModel().setCurrentIndex(self.selectionModel().model().index(rowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

    def selectGameOnRelativeRow(self, i_rowChange):
        """
        Params:
         i_rowChange:
          (int)
        """
        selectedIndex = self.selectionModel().currentIndex()
        newRowNo = selectedIndex.row() + i_rowChange
        if newRowNo < 0 or newRowNo >= len(self.dbRows):
            return
        self.selectionModel().setCurrentIndex(self.selectionModel().model().index(newRowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

    def selectRandomRow(self):
        """
        Params:
         i_rowNo:
          (int)
        """
        rowCount = self.tableModel.rowCount(None)
        if rowCount == 0:
            return

        newRowNo = random.randint(0, rowCount - 1)
        selectedIndex = self.selectionModel().currentIndex()
        self.selectionModel().setCurrentIndex(self.selectionModel().model().index(newRowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)

    selectionHasChanged = Signal()

    def selectionChanged(self, i_selected, i_deselected):  # override from QAbstractItemView
        QTableView.selectionChanged(self, i_selected, i_deselected)

        self.selectionHasChanged.emit()

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

    requestQuickFilter = Signal(str, str, str)
    # Params:
    #  i_combiner:
    #   (str)
    #   One of
    #    "AND"
    #    "OR"
    #  i_columnId:
    #   (str)
    #  i_text:
    #   (str)

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

        columnId = columns.tableColumn_getByPos(selectedIndex.column())["id"]

        self.requestQuickFilter.emit(i_combiner, columnId, formattedCriteria)

    # + }}}

    # + Scrolling {{{

    horizontalScroll = Signal(int)
    # Emitted when
    #  The column name bar is horizontally scrolled
    #
    # Params:
    #  i_dx:
    #   (int)
    #   The horizontal scroll amount in pixels

    def scrollContentsBy(self, i_dx, i_dy):  # override from QAbstractScrollArea
        """
        Called whenever the table view is scrolled.
        """
        # Call base class to scroll the actual table view
        QTableView.scrollContentsBy(self, i_dx, i_dy)

        # Notify main app so external bars can be scrolled horizontally by the same amount
        self.horizontalScroll.emit(i_dx)

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
        newMaximum = allColumnsWidth - self.horizontalScrollBar().pageStep() + self.extraHorizontalScrollSpaceNeeded + self.verticalScrollBar().width()
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
        if (i_event.modifiers() & Qt.ControlModifier) and i_event.key() == Qt.Key_C:
            self.clipboardCopy()
        # Else if pressed Ctrl+Home or Ctrl+End
        # workaround QTableView sort of but not fully visibly moving the selection, by calling setCurrentIndex() ourselves
        elif (i_event.modifiers() & Qt.ControlModifier) and i_event.key() == Qt.Key_Home:
            selectedIndex = self.selectionModel().model().index(0, 0)
            self.selectionModel().setCurrentIndex(selectedIndex, QItemSelectionModel.ClearAndSelect)
        elif (i_event.modifiers() & Qt.ControlModifier) and i_event.key() == Qt.Key_End:
            selectedIndex = self.selectionModel().model().index(self.tableModel.rowCount(None) - 1, self.tableModel.columnCount(None) - 1)
            self.selectionModel().setCurrentIndex(selectedIndex, QItemSelectionModel.ClearAndSelect)
        #
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

        effectiveResizeMargin = min(GameTableView.resizeMargin, self.rowHeight() / 8)

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
                # Get mouse pos relative to the GameTableView
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
                # Get mouse pos relative to the GameTableView
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
                # Get mouse pos relative to the GameTableView
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
