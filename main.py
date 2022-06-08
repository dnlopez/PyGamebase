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
import sql
import db
import frontend_utils
import frontend
import utils
import sql_filter_bar
import column_filter_bar


# + Parse command line {{{

COMMAND_NAME = "PyGamebase"

def printUsage(i_outputStream):
    i_outputStream.write('''\
''' + COMMAND_NAME + ''' by Daniel Lopez, 03/05/2022
GameBase frontend

Usage:
======
''' + COMMAND_NAME + ''' <Gamebase adapter file> [options...]

Params:
 Gamebase adapter file:
  Path of Gamebase adapter file.
  eg. "adapters/c64.py"

Options:
 --help
  Show this help.
''')

#
param_gamebaseAdapterFilePath = None

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
        if param_gamebaseAdapterFilePath == None:
            param_gamebaseAdapterFilePath = arg
        else:
            print("ERROR: Too many arguments.")
            print("(Run with --help to show command usage.)")
            #sys.exit(-1)

#param_gamebaseAdapterFilePath = "/mnt/gear/dan/docs/code/c/gamebase/c64.py"
if param_gamebaseAdapterFilePath == None:
    print("ERROR: Insufficient arguments.")
    print("(Run with --help to show command usage.)")
    sys.exit(-1)

# + }}}


# Import specified adapter module
import gamebase
gamebase.importAdapter(param_gamebaseAdapterFilePath)


# Load frontend configuration settings
g_frontendSettings = {}
settingsFilePath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation) + os.sep + "pyGamebase.json"
if os.path.exists(settingsFilePath):
    try:
        with open(settingsFilePath, "rb") as f:
            g_frontendSettings = json.loads(f.read().decode("utf-8"))
    except Exception as e:
        import traceback
        print("Failed to read frontend settings file: " + "\n".join(traceback.format_exception_only(e)))


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

    sortChanged = Signal()
    # Emitted when
    #  The sort order/columns change

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

        self.sortChanged.emit()

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

    requestHorizontalScroll = Signal(int)
    # Emitted when
    #  The column name bar wants to be horizontally scrolled, because a widget within it that is off the side of the window is getting focused
    #
    # Params:
    #  i_dx:
    #   (int)
    #   The horizontal scroll amount in pixels

    columnResized = Signal(str, int)
    # Emitted when
    #  A column is resized
    #
    # Params:
    #  i_columnId:
    #   (str)
    #  i_newWidth:
    #   (int)
    #   The new column width in pixels

    columnReordered = Signal()
    # Emitted when
    #  A column is moved to a different place in the order

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

                #
                self.columnResized.emit(self.resize_column["id"], newWidth)

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

                #
                self.columnReordered.emit()
                #self.reorderIndicator_widget.setFrameRect(QRect(edgeX - 2, 0, 4, 20))
                #self.reorderIndicator_widget.setFrameRect(QRect(2, 2, 50, 10))
                #print(leftColumn["id"], rightColumn["id"], edgeX)

                #
                return True

        elif i_event.type() == QEvent.FocusIn:
            # If this widget is off the side of the header bar / window,
            # ask for horizontal scroll
            positionOnBar = i_watched.mapTo(self, QPoint(0, 0))
            if positionOnBar.x() < 0:
                self.requestHorizontalScroll.emit(positionOnBar.x())
            elif positionOnBar.x() + i_watched.geometry().width() > self.geometry().width():
                self.requestHorizontalScroll.emit(positionOnBar.x() + i_watched.geometry().width() - self.geometry().width())

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
        oredRows = sql.sqlWhereExpressionToColumnFilters(sqlWhereExpression)
        columnFilterBar.setFilterValues(oredRows)

    # Refilter
    tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations)

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
        oredRows = sql.sqlWhereExpressionToColumnFilters(sqlWhereExpression)
        columnFilterBar.setFilterValues(oredRows)

    # Refilter
    tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations)

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
            screenshotFullPath = gamebase.dbRow_getNumberedScreenshotFullPath(self.parent().dbRows[i_index.row()], 0)
            if screenshotFullPath != None:
                pixmap = QPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.drawPixmap(destRect, pixmap)

        # Screenshot
        elif column["id"].startswith("pic[") and column["id"].endswith("]"):
            picNo = int(column["id"][4:-1])

            screenshotFullPath = gamebase.dbRow_getNumberedScreenshotFullPath(self.parent().dbRows[i_index.row()], picNo)
            if screenshotFullPath != None:
                pixmap = QPixmap(screenshotFullPath)
                destRect = danrectToQrect(fitLetterboxed(qrectToDanrect(pixmap.rect()), qrectToDanrect(i_option.rect)))
                i_painter.drawPixmap(destRect, pixmap)

        # Musician photo
        elif column["id"] == "musician_photo":
            photoFullPath = gamebase.dbRow_getPhotoFullPath(self.parent().dbRows[i_index.row()])
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
            #    pixmap = QPixmap(gamebase.normalizeDirPathFromAdapter(gamebase.adapter.config_screenshotsBaseDirPath) + "/" + screenshotPath)
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

class MyTableView(QTableView):
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

    doneQuery = Signal(int)
    # Emitted when
    #  queryDb() has finished a DB query and updated the game list
    #
    # Params:
    #  i_rowCount:
    #   (int)
    #   The new row/game count in the list

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
            parsedNeededTableNames, parsedNeededSelects = sql.sqlWhereExpressionToTableNamesAndSelects(i_whereExpression)
            neededTableNames = neededTableNames.union(parsedNeededTableNames)
            neededSelects = neededSelects.union(parsedNeededSelects)

        # Add the extra fromTerms
        tableConnections = copy.deepcopy(db.connectionsFromGamesTable)
        for neededTableName in neededTableNames:
            fromTerms += db.getJoinTermsToTable(neededTableName, tableConnections)

        # Add the extra selectTerms
        for neededSelect in neededSelects:
            if neededSelect == "Games.GA_Id" or neededSelect == "GA_Id":  # TODO use a set for this too
                continue
            selectTerms.append(neededSelect)

        # SELECT
        sqlText = "SELECT " + ", ".join(selectTerms)
        sqlText += "\nFROM " + " ".join(fromTerms)

        # WHERE
        i_whereExpression = i_whereExpression.strip()
        if i_whereExpression != "":
            sqlText += "\nWHERE " + i_whereExpression

        # ORDER BY
        if len(i_sortOperations) > 0:
            sqlText += "\nORDER BY "

            orderByTerms = []
            for columnId, direction in i_sortOperations:
                usableColumn = columns.usableColumn_getById(columnId)
                term = usableColumn["dbIdentifiers"][0]
                if direction == -1:
                    term += " DESC"
                orderByTerms.append(term)
            sqlText += ", ".join(orderByTerms)

        # Execute
        #print(sqlText)
        try:
            cursor = db.g_db.execute(sqlText)
        except sqlite3.OperationalError as e:
            # TODO if i_whereExpressionMightUseNonVisibleColumns and error was 'no such column', maybe retry with SELECT * and all tables (see getGameRecord())
            raise

        self.dbColumnNames = [column[0]  for column in cursor.description]
        self.dbRows = cursor.fetchall()

        self.doneQuery.emit(len(self.dbRows))

    def selectedGameId(self):
        """
        Returns:
         (int)
        """
        selectedIndex = self.selectionModel().currentIndex()
        return self.dbRows[selectedIndex.row()][self.dbColumnNames.index("Games.GA_Id")]

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
            selectedGameId = None
        else:
            selectedGameId = self.selectedGameId()
            selectedRowTopY = self.rowViewportPosition(selectedIndex.row())

        # Query database
        sqlValid = True
        try:
            self.queryDb(i_sqlWhereExpression, i_sortOperations)
        except sqlite3.OperationalError as e:
            sqlValid = False

            import traceback
            print(traceback.format_exc())

            messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
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
            if gameId != detail_pane.detailPane_currentGameId:
                detailPane.populate(gameId)
            if i_keyboardOriented and detailPaneWasAlreadyVisible:
                detailPane.setFocus(Qt.OtherFocusReason)

        elif columnId == "play":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = db.getGameRecord(gameId)
            gameRecord = db.DbRecordDict(gameRecord)

            try:
                gamebase.adapter.runGame(gameRecord["Games.Filename"], gameRecord["Games.FileToRun"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
                messageBox.setText("<big><b>In runGame():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                messageBox.resizeToContent()
                messageBox.exec()

        elif columnId == "music":
            rowNo = i_modelIndex.row()
            gameId = self.dbRows[rowNo][self.dbColumnNames.index("Games.GA_Id")]
            gameRecord = db.getGameRecord(gameId)
            gameRecord = db.DbRecordDict(gameRecord)

            try:
                gamebase.adapter.runMusic(gameRecord["Games.SidFilename"], gameRecord)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
                messageBox.setText("<big><b>In runMusic():</b></big>")
                messageBox.setInformativeText(traceback.format_exc())
                messageBox.resizeToContent()
                messageBox.exec()

        # Screenshot (unnumbered, old)
        elif columnId == "pic":
            rowNo = i_modelIndex.row()
            screenshotFullPath = gamebase.dbRow_getNumberedScreenshotFullPath(self.dbRows[rowNo], 0)
            if screenshotFullPath != None:
                frontend_utils.openInDefaultApplication(screenshotFullPath)

        # Screenshot
        elif columnId == "pic" or (columnId.startswith("pic[") and columnId.endswith("]")):
            picNo = int(columnId[4:-1])

            rowNo = i_modelIndex.row()
            screenshotFullPath = gamebase.dbRow_getNumberedScreenshotFullPath(self.dbRows[rowNo], picNo)
            if screenshotFullPath != None:
                frontend_utils.openInDefaultApplication(screenshotFullPath)

        # Musician photo
        elif columnId == "musician_photo":
            rowNo = i_modelIndex.row()
            photoFullPath = gamebase.dbRow_getPhotoFullPath(self.dbRows[rowNo])
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

    requestClearFilter = Signal()

    def selectGameWithId(self, i_gameId):
        # Look for row in table,
        # and if not found then clear filter and look again
        rowNo = self.findGameWithId(i_gameId)
        if rowNo == None:
            self.requestClearFilter.emit()
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
            if self.selectedGameId() != detail_pane.detailPane_currentGameId:
                detailPane.populate(self.selectedGameId())

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
if hasattr(gamebase.adapter, "config_title"):
    mainWindow.setWindowTitle(gamebase.adapter.config_title + " - GameBase")
else:
    mainWindow.setWindowTitle(param_gamebaseAdapterFilePath + " - GameBase")

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

        if tableView.selectedGameId() != detail_pane.detailPane_currentGameId:
            detailPane.populate(self.selectedGameId())

        detailPane.setFocus(Qt.OtherFocusReason)
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
    frontend_utils.openInDefaultApplication([gamebase.adapter.config_databaseFilePath])

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

def filterFormat_perColumn():
    # Show column filter bar instead of SQL filter bar
    columnFilterBar.show()
    sqlFilterBar.hide()

    # Convert SQL text to per-column filters
    # and set it in the per-column widgets

    # Get the expression text
    whereExpression = sqlFilterBar.text().strip()

    #
    oredRows = sql.sqlWhereExpressionToColumnFilters(whereExpression)
    if oredRows == None:
        columnFilterBar.resetFilterRowCount(1)
    else:
        columnFilterBar.setFilterValues(oredRows)

    columnFilterBar.repositionFilterEdits()
    columnFilterBar.repositionTabOrder()
    columnFilterBar.editingFinished.emit(True, "")

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

def columnNameBar_onRequestHorizontalScroll(i_dx):
    tableView.scrollBy(i_dx, 0)
columnNameBar.requestHorizontalScroll.connect(columnNameBar_onRequestHorizontalScroll)

def columnNameBar_onColumnResized(i_columnId, i_newWidth):
    columnFilterBar.repositionFilterEdits()
    tableView.horizontalHeader().resizeSection(columns.tableColumn_idToPos(i_columnId), i_newWidth)
    #tableView.selectionModel().setCurrentIndex(self.selectionModel().model().index(rowNo, selectedIndex.column()), QItemSelectionModel.ClearAndSelect)
columnNameBar.columnResized.connect(columnNameBar_onColumnResized)

def columnNameBar_onColumnReordered():
    columnFilterBar.repositionFilterEdits()
    columnFilterBar.repositionTabOrder()
    #
    tableView.requery()
    #
    tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])
columnNameBar.columnReordered.connect(columnNameBar_onColumnReordered)

def columnNameBar_onSortChanged():
    # Requery DB in new order
    refilterFromCurrentlyVisibleBar()
    tableView.requery()
columnNameBar.sortChanged.connect(columnNameBar_onSortChanged)

# + }}}

def refilterFromCurrentlyVisibleBar():
    if sqlFilterBar.isVisible():
        sqlWhereExpression = sqlFilterBar.text()
    else:
        sqlWhereExpression = columnFilterBar.getSqlWhereExpression()

    tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations)

# + Column filter bar {{{

columnFilterBar = column_filter_bar.ColumnFilterBar()
columnFilterBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
gameTable_layout.addWidget(columnFilterBar)

def columnFilterBar_onEditingFinished(i_modified, i_columnId):
    if not i_modified:
        tableView.setFocus()
        tableView.selectCellInColumnWithId(i_columnId)
    else:
        sqlWhereExpression = columnFilterBar.getSqlWhereExpression()
        if not tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations):
            return

        # If expression is different from the last history item at the current position,
        # truncate history at current position and append new item
        global g_filterHistory
        global g_filterHistory_pos
        if g_filterHistory[g_filterHistory_pos - 1] != sqlWhereExpression:
            del(g_filterHistory[g_filterHistory_pos:])
            g_filterHistory.append(sqlWhereExpression)
            g_filterHistory_pos += 1
columnFilterBar.editingFinished.connect(columnFilterBar_onEditingFinished)

def columnFilterBar_onRequestHorizontalScroll(i_dx):
    tableView.scrollBy(i_dx, 0)
columnFilterBar.requestHorizontalScroll.connect(columnFilterBar_onRequestHorizontalScroll)

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
        if not tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations):
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
tableView = MyTableView(column_filter_bar.ColumnFilterBar.filterRowHeight*2)
gameTable_layout.addWidget(tableView)
# Set vertical size policy to 'Ignored' which lets widget shrink to zero
#  https://stackoverflow.com/questions/18342590/setting-qlistwidget-minimum-height
tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

#  Set initial column widths
tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])

def tableView_onRequestClearFilter():
    if sqlFilterBar.isVisible():
        sqlFilterBar.userSetText("")
    else:
        columnFilterBar.resetFilterRowCount(1)
tableView.requestClearFilter.connect(tableView_onRequestClearFilter)

def tableView_onRequestQuickFilter(i_combiner, i_columnId, i_text):
    if i_combiner == "OR":
        columnFilterBar.appendFilterRow()
        columnFilterBar.repositionFilterEdits()
        columnFilterBar.repositionTabOrder()

    columnFilterBar.columnWidgets[i_columnId]["filterEdits"][-1].setText(i_text)
    columnFilterBar.editingFinished.emit(True, i_columnId)
tableView.requestQuickFilter.connect(tableView_onRequestQuickFilter)

def tableView_onHorizontalScroll(i_dx):
    columnNameBar.scroll(i_dx, 0)
    columnFilterBar.scroll(i_dx, 0)
tableView.horizontalScroll.connect(tableView_onHorizontalScroll)

# + }}}

# + Detail pane {{{

import detail_pane

detailPane = detail_pane.DetailPane()

splitter.addWidget(detailPane)
splitter.setStretchFactor(1, 1)  # Do stretch detail pane when window is resized

def detailPane_show():
    if splitter.orientation() == Qt.Vertical:
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
detailPane.requestClose.connect(detailPane_hide)

def detailPane_height():
    """
    Returns:
     (int)
    """
    return splitter.sizes()[1]

def detailPane_onLinkHovered(i_url):
    if i_url == "":
        label_statusbar.setText("Showing " + str(len(tableView.dbRows)) + " games.")
    else:
        label_statusbar.setText(i_url)
detailPane.linkHovered.connect(detailPane_onLinkHovered)

# + }}}

# + Statusbar {{{

# Create statusbar
label_statusbar = QLabel()
label_statusbar.setProperty("class", "statusbar")
#mainWindow.layout.addSpacing(8)
mainWindow.layout.addWidget(label_statusbar)
label_statusbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
label_statusbar.setContentsMargins(8, 8, 8, 8)

def tableView_onDoneQuery(i_gameCount):
    label_statusbar.setText("Showing " + str(i_gameCount) + " games.")
tableView.doneQuery.connect(tableView_onDoneQuery)

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

#
if not hasattr(gamebase.adapter, "config_databaseFilePath"):
    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
    messageBox.setText("<big><b>Missing adapter setting:</b></big>")
    messageBox.setInformativeText("config_databaseFilePath")
    messageBox.resizeToContent()
    messageBox.exec()
    sys.exit(1)

try:
    db.openDb(gamebase.normalizeDirPathFromAdapter(gamebase.adapter.config_databaseFilePath))
except Exception as e:
    import traceback
    print(traceback.format_exc())
    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
    messageBox.setText("<big><b>When opening database file:</b></big>")
    messageBox.setInformativeText("With path:\n" + gamebase.adapter.config_databaseFilePath + "\n\nAn error occurred:\n" + "\n".join(traceback.format_exception_only(e)))
    messageBox.resizeToContent()
    messageBox.exec()
    sys.exit(1)

#
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
