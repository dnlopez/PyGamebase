
# Python std
import functools

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
#from PySide2.QtWebEngineWidgets import *

# This program
import columns


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

            #self.setContextMenuPolicy(Qt.CustomContextMenu)
            #self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

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

    """
        # + Context menu {{{

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenuRequested)

        # + }}}

    # + Context menu {{{

    def onCustomContextMenuRequested(self, i_pos):
        # Get context menu invocation position (normally mouse position, but could also be centre of header button if pressed keyboard menu button) relative to the ColumnNameBar
        # and adjust for horizontal scroll amount
        #invocationPos = self.mapTo(self.parent(), i_pos)
        i_pos.setX(i_pos.x() - self.scrollX)
        # Get the specific column on which the context menu was invoked,
        # so if we end up showing any new columns, they can be inserted at that position
        contextColumn = self._columnAtPixelX(i_pos.x())
        print(contextColumn)

        # Inform the table columns menu of the column
        # and pop it up
        viewMenu_tableColumnsMenu.context = contextColumn["id"]
        viewMenu_tableColumnsMenu.popup(self.mapToGlobal(i_pos))

    # + }}}
    """

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
                headingButton = ColumnNameBar.HeadingButton(column["headingName"], column["filterable"], self)
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
        self.sort(i_columnId, QApplication.queryKeyboardModifiers() == Qt.ControlModifier)

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

                newCaption = column["headingName"]

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
