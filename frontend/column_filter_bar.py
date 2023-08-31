
# Python std
import functools

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras
import columns


# + Column filter bar {{{

def stringLooksLikeNumber(i_str):
    try:
        float(i_str)
        return True
    except ValueError:
        return False

class ColumnFilterBar(QWidget):
    """
    One or more rows of text box controls for entering filter criteria per column.
    """
    filterRowHeight = 30

    editingFinished = Signal(bool, str)
    # Emitted when any of the following happen:
    #  A line edit has focus and the Return or Enter key is pressed
    #  A line edit loses focus after its text has been modified
    #  The clear button is clicked
    #
    # Params:
    #  i_modified:
    #   (bool)
    #   True: the text was modified
    #  i_columnId:
    #   (str)
    #   If a line edit has focus and the Return or Enter key is pressed, the ID of the column that that line edit widget belongs to;
    #   else if a line edit loses focus after its text has been modified, the ID of the column that that line edit widget belongs to;
    #   else if the clear button is clicked, ""

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
        #     (list of qt_extras.LineEditWithClearButton)

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
            tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
            if tableColumnSpec["filterable"] and \
               (column["id"] not in self.columnWidgets):

                # Create an object for its header widgets
                widgetDict = {}

                # Create filter edits
                widgetDict["filterEdits"] = []
                for filterRowNo in range(0, len(self.filterRows)):
                    # Create special line edit widget
                    filterEdit = qt_extras.LineEditWithClearButton(ColumnFilterBar.filterRowHeight, self)
                    # Set its fixed properties (apart from position)
                    filterEdit.setVisible(True)
                    filterEdit.editingFinished.connect(functools.partial(self.lineEdit_onEditingFinished, column["id"]))
                    #  Filter events to facilitate scroll to upon focus
                    filterEdit.lineEdit.installEventFilter(self)
                    # Save in object
                    widgetDict["filterEdits"].append(filterEdit)

                # Save the object of header widgets
                self.columnWidgets[column["id"]] = widgetDict

        # For each object of header widgets
        # which no longer corresponds to an existing, filterable, visible column
        columnIds = list(self.columnWidgets.keys())
        for columnId in columnIds:
            column = columns.tableColumn_getById(columnId)
            if column != None:
                tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
                if not tableColumnSpec["filterable"]:
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
            tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
            if tableColumnSpec["filterable"]:
                # Create special line edit widget
                filterEdit = qt_extras.LineEditWithClearButton(ColumnFilterBar.filterRowHeight, self)
                # Set its fixed properties (apart from position)
                filterEdit.setVisible(True)
                filterEdit.editingFinished.connect(functools.partial(self.lineEdit_onEditingFinished, column["id"]))
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
            tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
            if tableColumnSpec["filterable"]:
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
            tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
            if tableColumnSpec["filterable"]:
                self.columnWidgets[column["id"]]["filterEdits"][i_position].setText("")

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
            self.editingFinished.emit(True, "")

    def deleteRow_pushButton_onClicked(self, i_filterRow):
        if len(self.filterRows) == 1:
            self.clearFilterRow(0)
        else:
            for filterRowNo, filterRow in enumerate(self.filterRows):
                if filterRow == i_filterRow:
                    self.deleteFilterRow(filterRowNo)
                    self.repositionFilterEdits()
                    #self.repositionTabOrder()
        self.editingFinished.emit(True, "")

    def insertRow_pushButton_onClicked(self):
        self.appendFilterRow()
        #self.repositionHeadingButtons()
        self.repositionFilterEdits()
        self.repositionTabOrder()

    def lineEdit_onEditingFinished(self, i_columnId, i_modified):
        self.editingFinished.emit(i_modified, i_columnId)

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
                tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
                if tableColumnSpec["filterable"]:
                    value = self.columnWidgets[column["id"]]["filterEdits"][filterRowNo].text()
                    value = value.strip()
                    if value != "":
                        # If range operator
                        betweenValues = value.split("~")
                        if len(betweenValues) == 2 and stringLooksLikeNumber(betweenValues[0]) and stringLooksLikeNumber(betweenValues[1]):
                            andTerms.append(tableColumnSpec["dbIdentifiers"][0] + " BETWEEN " + betweenValues[0] + " AND " + betweenValues[1])

                        # Else if regular expression
                        elif len(value) > 2 and value.startswith("/") and value.endswith("/"):
                            # Get regexp
                            value = value[1:-1]

                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerms.append(tableColumnSpec["dbIdentifiers"][0] + " REGEXP " + value)
                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                        # Else if a comparison operator (=, <>, >, <, >=, <=)
                        elif value.startswith("=") or value.startswith(">") or value.startswith("<") or value.startswith("!="):
                            # Get operator and value
                            if value.startswith(">=") or value.startswith("<=") or value.startswith("<>") or value.startswith("!="):
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
                            andTerms.append(tableColumnSpec["dbIdentifiers"][0] + " " + operator + " " + value)

                        # Else if a LIKE expression (contains an unescaped %)
                        elif value.replace("\\%", "").find("%") != -1:
                            # Format value as a string
                            value = value.replace("'", "''")
                            value = "'" + value + "'"

                            #
                            andTerm = tableColumnSpec["dbIdentifiers"][0] + " LIKE " + value
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
                            andTerms.append(tableColumnSpec["dbIdentifiers"][0] + " LIKE " + value)

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

    requestHorizontalScroll = Signal(int)
    # Emitted when
    #  The column filter bar wants to be horizontally scrolled, because a widget within it that is off the side of the window is getting focused
    #
    # Params:
    #  i_dx:
    #   (int)
    #   The horizontal scroll amount in pixels

    def eventFilter(self, i_watched, i_event):
        #print(i_event.type())

        if i_event.type() == QEvent.FocusIn:
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

    def repositionFilterEdits(self):
        y = 0

        for filterRowNo, filterRow in enumerate(self.filterRows):
            x = 0
            x += self.scrollX  # Adjust for horizontal scroll amount
            for columnNo, column in enumerate(columns.tableColumn_getBySlice()):
                tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
                if tableColumnSpec["filterable"]:
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
                tableColumnSpec = columns.tableColumnSpec_getById(column["id"])
                if tableColumnSpec["filterable"]:
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
