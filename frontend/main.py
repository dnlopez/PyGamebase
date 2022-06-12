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
import settings
import qt_extras
import columns
import sql
import db
import frontend_utils
import frontend
import utils
import sql_filter_bar
import column_filter_bar
import column_name_bar
import game_table_view
import preferences_window


# Create a Qt application
# (or reuse old one if it already exists; ie. when re-running in REPL during development)
# and do this before parsing the command line in order for it to filter Qt-specific arguments out
if not QApplication.instance():
    application = QApplication(sys.argv)
else:
    application = QApplication.instance()
filteredArgv = application.arguments()

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
while argNo < len(filteredArgv):
    arg = filteredArgv[argNo]
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

# If no adapter file was specified
# then prompt with a file picker
if param_gamebaseAdapterFilePath == None:
    param_gamebaseAdapterFilePath, filter = QFileDialog.getOpenFileName(None, "Select Gamebase adapter file")
    if param_gamebaseAdapterFilePath == "":
        sys.exit(0)

# + }}}


# Import specified adapter module
import gamebase
gamebase.importAdapter(param_gamebaseAdapterFilePath)


# Load frontend configuration settings
settings.loadPreferences()
settings.loadViewSettings()


# + Filter history {{{

g_filterHistory = [""]
g_filterHistory_pos = 1

def filterHistory_add(i_sqlWhereExpression):
    """
    Params:
     i_sqlWhereExpression:
      (str)
    """
    # If expression is the same as the last history item at the current position,
    # do nothing
    global g_filterHistory
    global g_filterHistory_pos
    if g_filterHistory[g_filterHistory_pos - 1] == i_sqlWhereExpression:
        return

    # Else truncate history at current position and append new item
    del(g_filterHistory[g_filterHistory_pos:])
    g_filterHistory.append(i_sqlWhereExpression)
    g_filterHistory_pos += 1

    # Update back/forward toolbar buttons
    toolbar_back_toolButton.setEnabled(True)
    toolbar_forward_toolButton.setEnabled(False)

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

    # Update back/forward toolbar buttons
    toolbar_back_toolButton.setEnabled(g_filterHistory_pos > 1)
    toolbar_forward_toolButton.setEnabled(True)

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

    # Update back/forward toolbar buttons
    toolbar_forward_toolButton.setEnabled(g_filterHistory_pos < len(g_filterHistory))
    toolbar_back_toolButton.setEnabled(True)

# + }}}



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
        tableView.scrollToSelection()

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
#fileMenu.addAction("New")
#fileMenu.addAction("Open")
#fileMenu.addAction("Save")
#fileMenu.addSeparator()
#fileMenu.addAction("Quit")

editMenu = menuBar.addMenu("&Edit")
editMenu.addAction("Copy")
editMenu.addSeparator()
editMenu_preferences_action = editMenu.addAction("&Preferences...")
g_preferencesWindow = None
def editMenu_preferences_onTriggered():
    global g_preferencesWindow
    g_preferencesWindow = preferences_window.PreferencesWindow()
    g_preferencesWindow.show()
editMenu_preferences_action.triggered.connect(editMenu_preferences_onTriggered)

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
def filterMenu_filterFormat_copySql_onTriggered():
    QGuiApplication.clipboard().setText(columnFilterBar.getSqlWhereExpression())
filterMenu_filterFormat_copySql_action.triggered.connect(filterMenu_filterFormat_copySql_onTriggered)

viewMenu = menuBar.addMenu("&View")
viewMenu_toolbar_action = viewMenu.addAction("&Toolbar")
viewMenu_toolbar_action.setCheckable(True)
if not "toolbarVisible" in settings.viewSettings:
    settings.viewSettings["toolbarVisible"] = True
viewMenu_toolbar_action.setChecked(settings.viewSettings["toolbarVisible"])
def viewMenu_toolbar_onTriggered(i_checked):
    toolbar.setVisible(i_checked)
viewMenu_toolbar_action.triggered.connect(viewMenu_toolbar_onTriggered)

viewMenu.addSeparator()

if not "splitHorizontally" in settings.viewSettings:
    settings.viewSettings["splitHorizontally"] = False
def splitter_setHorizontal():
    splitter.setOrientation(Qt.Horizontal)
def splitter_setVertical():
    splitter.setOrientation(Qt.Vertical)
#viewMenu_splitMenu = QMenu("&Split")
#viewMenu_toolbar_action = viewMenu.addMenu(viewMenu_splitMenu)
viewMenu_verticalAction = viewMenu.addAction("Split &vertically")
viewMenu_verticalAction.setCheckable(True)
viewMenu_verticalAction.setChecked(not settings.viewSettings["splitHorizontally"])
viewMenu_verticalAction.triggered.connect(splitter_setVertical)
viewMenu_horizontalAction = viewMenu.addAction("Split &horizontally")
viewMenu_horizontalAction.setCheckable(True)
viewMenu_horizontalAction.setChecked(settings.viewSettings["splitHorizontally"])
viewMenu_horizontalAction.triggered.connect(splitter_setHorizontal)
actionGroup = QActionGroup(filterMenu)
actionGroup.setExclusive(True)
actionGroup.addAction(viewMenu_horizontalAction)
actionGroup.addAction(viewMenu_verticalAction)

viewMenu.addSeparator()

class TableColumnsMenu(qt_extras.StayOpenMenu):
    # + Init {{{

    def __init__(self, i_title=None, i_parent=None):
        qt_extras.StayOpenMenu.__init__(self, i_title, i_parent)

        self.setToolTipsVisible(True)

        self.submenus = {}
        # (dict)
        # Dictionary has:
        #  Keys:
        #   (str)
        #   Submenu title
        #  Values:
        #   (TableColumnsMenu)

        self.actions = {}
        # (dict)
        # Dictionary has:
        #  Keys:
        #   (str)
        #   Column ID
        #  Values:
        #   (QAction)

        self.aboutToShow.connect(self.onAboutToShow)

    def populateMenu(self):
        # Add all the usable columns
        for usableColumn in columns.usableColumn_getBySlice():
            self.addActionForColumn(usableColumn, usableColumn["menuPath"])

    def addActionForColumn(self, i_usableColumn, i_menuPath):
        # If the column is in a submenu
        if len(i_menuPath) > 1:
            # If don't have the next submenu yet,
            # create one
            if i_menuPath[0] not in self.submenus:
                submenu = TableColumnsMenu(i_menuPath[0], self)
                self.submenus[i_menuPath[0]] = submenu
                self.addMenu(submenu)
            else:
                submenu = self.submenus[i_menuPath[0]]
            # Pass on to the submenu
            submenu.addActionForColumn(i_usableColumn, i_menuPath[1:])

        # Else if the column is in this menu
        else:
            # Create action and save it in self.actions under the column id
            columnId = i_usableColumn["id"]
            action = self.addAction(i_menuPath[0])
            self.actions[columnId] = action
            #
            if "tooltip" in i_usableColumn:
                action.setToolTip(i_usableColumn["tooltip"])
            elif "mdbComment" in i_usableColumn:
                action.setToolTip(i_usableColumn["mdbComment"])
            action.setCheckable(True)
            action.setChecked(columns.tableColumn_getById(columnId) != None)
            action.triggered.connect(functools.partial(self.action_onTriggered, columnId))

    # + }}}

    # + On show {{{

    def onAboutToShow(self):
        for columnId, action in self.actions.items():
            action.setChecked(columns.tableColumn_getById(columnId) != None)

    # + }}}

    # + On action triggered {{{

    def action_onTriggered(self, i_selectedColumnId):
        # Toggle the visibility of the selected column,
        # and if it was now hidden then remove from sort operations
        if not columns.tableColumn_toggle(i_selectedColumnId, viewMenu_tableColumnsMenu.context):
            foundSortOperationNo = None
            for sortOperationNo, sortOperation in enumerate(columnNameBar.sort_operations):  # TODO columnNameBar reference
                if sortOperation[0] == i_selectedColumnId:
                    foundSortOperationNo = sortOperationNo
                    break
            if foundSortOperationNo != None:
                del(columnNameBar.sort_operations[foundSortOperationNo])
                columnNameBar.sort_updateGui()

        # Update GUI
        columnNameBar.recreateWidgets()
        columnNameBar.repositionHeadingButtons()
        columnNameBar.repositionTabOrder()
        columnFilterBar.recreateWidgets()
        columnFilterBar.repositionFilterEdits()
        columnFilterBar.repositionTabOrder()

        # Remember currently selected game ID and column number
        selectedGameId = tableView.selectedGameId()
        selectedColumnNo = tableView.selectionModel().currentIndex().column()

        # Requery DB in case filter criteria have changed
        refilterFromCurrentlyVisibleBar()
        tableView.requery()
        #
        tableView.resizeAllColumns([column["width"]  for column in columns.tableColumn_getBySlice()])

        # Reselect same game and column in table, if it's still there
        rowNo = tableView.findGameWithId(selectedGameId)
        if rowNo != None:
            tableView.selectionModel().setCurrentIndex(tableView.selectionModel().model().index(rowNo, selectedColumnNo), QItemSelectionModel.ClearAndSelect)

    # + }}}

viewMenu_tableColumnsMenu = TableColumnsMenu("&Table columns")
viewMenu_tableColumnsMenu_action = viewMenu.addMenu(viewMenu_tableColumnsMenu)
def viewMenu_tableColumnsMenu_action_onHovered():
    viewMenu_tableColumnsMenu.context = None
viewMenu_tableColumnsMenu_action.hovered.connect(viewMenu_tableColumnsMenu_action_onHovered)

viewMenu_detailPaneItems_action = viewMenu.addAction("&Detail pane items...")

viewMenu.addSeparator()

viewMenu_saveLayout = viewMenu.addAction("&Save layout")
def viewMenu_saveLayout_onTriggered():
    configColumns = []
    for tableColumn in columns.tableColumn_getBySlice():
        configColumns.append({
            "id": tableColumn["id"],
            "width": tableColumn["width"]
        })
    settings.viewSettings["tableColumns"] = configColumns

    settings.viewSettings["toolbarVisible"] = toolbar.isVisible()
    settings.viewSettings["splitHorizontally"] = splitter.orientation() == Qt.Horizontal
    settings.viewSettings["horizontalSplitPosition"] = splitter_lastPosition
    settings.viewSettings["detailPaneItems"] = detail_pane.g_detailPaneItems

    settings.saveViewSettings()
viewMenu_saveLayout.triggered.connect(viewMenu_saveLayout_onTriggered)

# + }}}

# + Toolbar {{{

toolbar = QToolBar()

toolbar_back_toolButton = QToolButton()
#toolbar_back_toolButton.setArrowType(Qt.LeftArrow)
toolbar_back_toolButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
toolbar_back_toolButton.setText("◀")
toolbar_back_toolButton.setToolTip("Go back in filter")
toolbar_back_toolButton.clicked.connect(filterHistory_goBack)
toolbar_back_toolButton.setEnabled(False)
toolbar_back_action2 = toolbar.addWidget(toolbar_back_toolButton)
toolbar_forward_toolButton = QToolButton()
#toolbar_forward_toolButton.setArrowType(Qt.RightArrow)
toolbar_forward_toolButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
toolbar_forward_toolButton.setText("▶")
toolbar_forward_toolButton.setToolTip("Go forward in filter")
toolbar_forward_toolButton.clicked.connect(filterHistory_goForward)
toolbar_forward_toolButton.setEnabled(False)
toolbar_forward_action2 = toolbar.addWidget(toolbar_forward_toolButton)

toolbar.setVisible(settings.viewSettings["toolbarVisible"])
mainWindow.layout.addWidget(toolbar)

# + }}}

# Create splitter
if settings.viewSettings["splitHorizontally"]:
    splitter = QSplitter(Qt.Horizontal)
else:
    splitter = QSplitter(Qt.Vertical)
mainWindow.layout.addWidget(splitter)
splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
if not ("horizontalSplitPosition" in settings.viewSettings):
    settings.viewSettings["horizontalSplitPosition"] = 200
splitter_lastPosition = settings.viewSettings["horizontalSplitPosition"]
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

columnNameBar = column_name_bar.ColumnNameBar()
columnNameBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
columnNameBar.setFixedHeight(30)
gameTable_layout.addWidget(columnNameBar)

# + + Context menu {{{

def columnNameBar_onCustomContextMenuRequested(i_pos):
    # Get context menu invocation position (normally mouse position, but could also be centre of header button if pressed keyboard menu button) relative to the ColumnNameBar
    # and adjust for horizontal scroll amount
    #invocationPos = self.mapTo(self.parent(), i_pos)
    i_pos.setX(i_pos.x() - columnNameBar.scrollX)
    # Get the specific column on which the context menu was invoked,
    # so if we end up showing any new columns, they can be inserted at that position
    contextColumn = columnNameBar._columnAtPixelX(i_pos.x())

    # Inform the table columns menu of the column
    # and pop it up
    viewMenu_tableColumnsMenu.context = contextColumn["id"]
    viewMenu_tableColumnsMenu.popup(columnNameBar.mapToGlobal(i_pos))

columnNameBar.setContextMenuPolicy(Qt.CustomContextMenu)
columnNameBar.customContextMenuRequested.connect(columnNameBar_onCustomContextMenuRequested)

# + + }}}

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

        filterHistory_add(sqlWhereExpression)
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
        tableView.scrollToSelection()
    else:
        sqlWhereExpression = sqlFilterBar.text()
        if not tableView.refilter(sqlWhereExpression, columnNameBar.sort_operations):
            return

        filterHistory_add(sqlWhereExpression)
sqlFilterBar.editingFinished.connect(sqlFilterBar_onEditingFinished)

# + }}}

# + Table view {{{

# Create table
tableView = game_table_view.GameTableView(column_filter_bar.ColumnFilterBar.filterRowHeight*2)
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

def tableView_onSelectionHasChanged():
    # If detail pane is open,
    # repopulate it from the new row
    if detailPane_height() > 0:
        selectedIndex = tableView.selectionModel().currentIndex()
        if tableView.selectedGameId() != detail_pane.detailPane_currentGameId:
            detailPane.populate(tableView.selectedGameId())
tableView.selectionHasChanged.connect(tableView_onSelectionHasChanged)

def tableView_onRequestDetailPane(i_withKeyboardAction, i_modelIndex):
    detailPaneWasAlreadyVisible = detailPane_height() > 0
    detailPane_show()
    if splitter.orientation() == Qt.Vertical:
        tableView.scrollTo(i_modelIndex, QAbstractItemView.PositionAtTop)
    gameId = tableView.dbRows[i_modelIndex.row()][tableView.dbColumnNames.index("Games.GA_Id")]
    if gameId != detail_pane.detailPane_currentGameId:
        detailPane.populate(gameId)
    if i_withKeyboardAction and detailPaneWasAlreadyVisible:
        detailPane.setFocus(Qt.OtherFocusReason)
tableView.requestDetailPane.connect(tableView_onRequestDetailPane)

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
        tableView.alignItemToTop(True)
    else:
        splitter.setSizes([splitter_lastPosition, splitter.geometry().width() - splitter_lastPosition])

def detailPane_hide():
    # Hide detail pane
    splitter.setSizes([splitter.geometry().height(), 0])
    # Stop forcibly aligning an item to the top of the table view
    tableView.alignItemToTop(False)
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

# + + Layout {{{

g_detailPaneItems = None
def viewMenu_detailPaneItems_action_onTriggered():
    global g_detailPaneItems
    if g_detailPaneItems == None:
        g_detailPaneItems = detail_pane.DetailPaneItems()
        g_detailPaneItems.change.connect(detailPaneItems_onChange)
        g_detailPaneItems.resize(600, 600)
        g_detailPaneItems.move(QApplication.desktop().rect().center() - g_detailPaneItems.rect().center())
    g_detailPaneItems.show()
    g_detailPaneItems.activateWindow()
viewMenu_detailPaneItems_action.triggered.connect(viewMenu_detailPaneItems_action_onTriggered)

def detailPaneItems_onChange():
    # If detail pane is open,
    # repopulate it
    if detailPane_height() > 0:
        detailPane.populate(detail_pane.detailPane_currentGameId)

# + + }}}

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
    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
    messageBox.setText("<big><b>Missing adapter setting:</b></big><pre>config_databaseFilePath</pre>")
    messageBox.resizeToContent()
    messageBox.exec()
    sys.exit(1)

try:
    db.openDb(gamebase.normalizeDirPathFromAdapter(gamebase.adapter.config_databaseFilePath))
except Exception as e:
    import traceback
    print(traceback.format_exc())
    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
    messageBox.setText("<big><b>When opening database file:</b></big><p>\nWith path:<br>\n<br>\n" + gamebase.adapter.config_databaseFilePath + "<p>\nAn error occurred:<pre>" + "<br>\n".join(traceback.format_exception_only(e)) + "</pre>")
    messageBox.resizeToContent()
    messageBox.exec()
    sys.exit(1)

#
viewMenu_tableColumnsMenu.populateMenu()

# Create initial table columns
if not "tableColumns" in settings.viewSettings:
    settings.viewSettings["tableColumns"] = [
        { "id": "detail",
          "width": 35,
        },
        { "id": "play",
          "width": 35,
        },
        { "id": "pic[0]",
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

for initialColumn in settings.viewSettings["tableColumns"]:
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

class SubprocessOutput(qt_extras.PlainTextViewer):
    def __init__(self, i_parent=None):
        qt_extras.PlainTextViewer.__init__(self, i_parent)

        self.setWindowTitle("Subprocess Output")
        self.setGeometry(50, 75, 600, 400)

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
            selectionStartPos = self.plainTextEdit.textCursor().selectionStart()
            selectionEndPos = self.plainTextEdit.textCursor().selectionEnd()

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

            self.setText(text)

            textCursor = self.plainTextEdit.textCursor()
            textCursor.setPosition(selectionStartPos)
            textCursor.setPosition(selectionEndPos, QTextCursor.KeepAnchor)
            self.plainTextEdit.setTextCursor(textCursor)
        else:
            self.setText("")

subprocessOutput = None
def menu_file_showSubprocessOutput_onTriggered(i_checked):
    global subprocessOutput
    if subprocessOutput == None:
        subprocessOutput = SubprocessOutput()

    subprocessOutput.show()

action = fileMenu.addAction("Show subprocess &output")
action.triggered.connect(menu_file_showSubprocessOutput_onTriggered)

# + }}}

# If application stylesheet wasn't already set (via command line)
# and there's one specified in the preferences,
# activate it
if application.styleSheet() == "" and "applicationStylesheet" in settings.preferences and settings.preferences["applicationStylesheet"] != "":
    application.setStyleSheet("file:///" + settings.preferences["applicationStylesheet"])

# Enter Qt application main loop
exitCode = application.exec_()
sys.exit(exitCode)