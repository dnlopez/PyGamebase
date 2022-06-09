
# Python std
import os.path
import urllib.parse
import math

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras
import db
import gamebase
import columns



detailPane_currentGameId = None

g_detailPaneItems = [
    "gameName",
    "screenshots",
    "related",
    "memoText",
    "comment",
    "weblinks",
    "nonImageExtras",
    "imageExtras"
]

g_detailPaneItemsAvailable = set([
    "gameName",
    "screenshots",
    "related",
    "memoText",
    "comment",
    "weblinks",
    "nonImageExtras",
    "imageExtras"
])

class DetailPane(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        #        #QShortcut(QKeySequence("Escape"), self, activated=self.escapeShortcut_onActivated)
        #        #QShortcut(QKeySequence("Page Up"), self, activated=self.pageUpShortcut_onActivated)
        #    #def escapeShortcut_onActivated(self):
        #    #    detailPane_hide()
        #    #def pageUpShortcut_onActivated(self):
        #    #    detailPane_hide()

        #self = QWidget()
        self.setProperty("class", "detailPane")
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.margin = QPushButton("x")
        self.margin.clicked.connect(self.margin_onClicked)
        self.layout.addWidget(self.margin)

        self.margin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        #self.margin.setFixedWidth(columns.tableColumn_getByPos(0)["width"])
        self.margin.setFixedWidth(columns.usableColumn_getById("detail")["defaultWidth"])

        class MyWebEngineView(QWebEngineView):
            def __init__(self, i_parent=None):
                QWebEngineView.__init__(self, i_parent)

                self.plainTextViewer = None

            def contextMenuEvent(self, i_event):  # override from QWidget
                # Start a menu
                newMenu = QMenu(self)

                # Copy only items we want from the standard context menu
                menu = self.page().createStandardContextMenu()
                actions = menu.actions()
                for action in actions:
                    if action.text() in ["Copy", "Copy link address", "Copy image", "Copy image address"]: #, "View page source"]:
                        newMenu.addAction(action)

                # Add 'View page source' item
                if len(newMenu.actions()) > 0:
                    newMenu.addSeparator()
                viewPageSourceAction = newMenu.addAction("View page source")
                viewPageSourceAction.triggered.connect(self.viewPageSourceAction_onTriggered)

                # Show menu
                newMenu.exec_(i_event.globalPos())

            def viewPageSourceAction_onTriggered(self):
                self.page().toHtml(self.viewPageSourceAction_getHtml)
            def viewPageSourceAction_getHtml(self, i_html):
                if self.plainTextViewer == None:
                    self.plainTextViewer = qt_extras.PlainTextViewer()
                    self.plainTextViewer.setGeometry(50, 75, 600, 400)
                self.plainTextViewer.setWindowTitle("view-source: " + self.parent().gameName)
                self.plainTextViewer.setText(i_html)
                self.plainTextViewer.show()

        self.webEngineView = MyWebEngineView(self)
        self.webEngineView.setProperty("class", "webEngineView")
        self.layout.addWidget(self.webEngineView)

    requestClose = Signal()
    # Emitted when
    #  The close button is clicked

    def margin_onClicked(self):
        self.requestClose.emit()

    linkHovered = Signal(str)
    # Emitted when
    #  A link is hovered or unhovered
    #
    # Params:
    #  i_url:
    #   (str)
    #   The URL of the link hovered over
    #   "": A URL has been unhovered

    def populate(self, i_gameId):
        """
        Params:
         i_gameId:
          (int)
        """
        gameRow = db.getGameRecord(i_gameId, True)
        extrasRows = db.getExtrasRecords(str(gameRow["Games.GA_Id"]))

        #
        global detailPane_currentGameId
        detailPane_currentGameId = gameRow["Games.GA_Id"]

        # Save name for the titlebar of the view source window
        self.gameName = gameRow["Games.Name"]

        #
        html = ""

        html += '<link rel="stylesheet" type="text/css" href="file://' + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + '/styles/dark.css">'

        for item in g_detailPaneItems:
            if item == "screenshots":
                # Insert screenshots after the first one
                supplementaryScreenshotRelativePaths = gamebase.dbRow_getSupplementaryScreenshotPaths(gameRow)
                for relativePath in supplementaryScreenshotRelativePaths:
                    screenshotUrl = gamebase.getScreenshotUrl(relativePath)
                    if screenshotUrl != None:
                        html += '<img src="' + screenshotUrl + '">'

            elif item == "gameName":
                html += '<div class="game_name">' + gameRow["Games.Name"] + '</div>'

            elif item == "related":
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

            elif item == "memoText":
                # Insert memo text
                if gameRow["Games.MemoText"] != None:
                    html += '<p style="white-space: pre-wrap;">'
                    html += gameRow["Games.MemoText"]
                    html += '</p>'

            elif item == "comment":
                # Insert comment
                if gameRow["Games.Comment"] != None:
                    html += '<p style="white-space: pre-wrap;">'
                    html += gameRow["Games.Comment"]
                    html += '</p>'

            elif item == "weblinks":
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

            elif item == "nonImageExtras":
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

            elif item == "imageExtras":
                # Seperate extras which are and aren't images
                imageRows = []
                nonImageRows = []
                for extrasRow in extrasRows:
                    path = extrasRow["Path"]
                    if path != None and (path.lower().endswith(".jpg") or path.lower().endswith(".jpeg") or path.lower().endswith(".gif") or path.lower().endswith(".png")):
                        imageRows.append(extrasRow)
                    else:
                        nonImageRows.append(extrasRow)

                # For each image, insert an image
                if len(imageRows) > 0:
                    html += '<div id="imageExtras">'

                    for imageRowNo, imageRow in enumerate(imageRows):
                        #print("imageRow: " + str(imageRow))
                        #var cell = document.createElement("div");

                        html += '<a href="extra:///' + imageRow["Path"] + '" style="display: inline-block; text-align: center;">'
                        if hasattr(gamebase.adapter, "config_extrasBaseDirPath"):
                            html += '<img src="file://' + gamebase.normalizeDirPathFromAdapter(gamebase.adapter.config_extrasBaseDirPath) + "/" + imageRow["Path"] + '" style="height: 300px;">'
                        #html += '<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" style="height: 300px;">'
                        html += '<div>' + imageRow["Name"] + '</div>'
                        html += '</a>'

                        #cell.appendChild(link);

                    html += "</div>"


        #print(html)

        #self.webEngineView.setHtml(html, QUrl("file:///"))
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
                    # pass it to the adapter file's runExtra()
                    url = i_qUrl.toString()
                    if url.startswith("extra:///"):
                        extraPath = url[9:]
                        extraPath = urllib.parse.unquote(extraPath)
                        extraInfo = [row  for row in self.extrasRows  if row["Path"] == extraPath][0]
                        gameInfo = self.gameRow
                        gameInfo = db.DbRecordDict(gameInfo)

                        try:
                            gamebase.adapter.runExtra(extraPath, extraInfo, gameInfo)
                        except Exception as e:
                            import traceback
                            print(traceback.format_exc())
                            messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error", "")
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
        webEnginePage = WebEnginePage(gameRow, extrasRows, self.webEngineView)
        webEnginePage.setHtml(html, QUrl("file:///"))
        # Let background of application show through to stop white flash on page loads
        webEnginePage.setBackgroundColor(Qt.transparent)

        def webEnginePage_onLinkHovered(i_url):
            self.linkHovered.emit(i_url)
        webEnginePage.linkHovered.connect(webEnginePage_onLinkHovered)

        # Load web engine page into the web engine view
        #webEnginePage.setView(self.webEngineView)
        self.webEngineView.setPage(webEnginePage)

    def setFocus(self, i_focusReason):
        self.webEngineView.setFocus(i_focusReason)


# + Layout editor {{{

def detailPaneItems_move(i_rowNo, i_toBeforeRowNo):
    """
    Params:
     i_rowNo:
      (int)
     i_toBeforeRowNo:
      (int)

    Returns:
     (int)
     The new position of the row.
     -1: The row wasn't moved
    """
    if i_rowNo == i_toBeforeRowNo or i_rowNo + 1 == i_toBeforeRowNo:
        return -1

    item = g_detailPaneItems.pop(i_rowNo)
    if i_rowNo < i_toBeforeRowNo:
        i_toBeforeRowNo -= 1
    g_detailPaneItems.insert(i_toBeforeRowNo, item)
    return i_toBeforeRowNo

def detailPaneItems_unuse(i_rowNo):
    """
    Params:
     i_rowNo:
      (int)
    """
    g_detailPaneItems.pop(i_rowNo)

def detailPaneItems_use(i_item, i_beforeRowNo):
    """
    Params:
     i_item:
      (str)
     i_beforeRowNo:
      (int)
    """
    g_detailPaneItems.insert(i_beforeRowNo, i_item)

# + + Available {{{

class DetailPaneAvailableItemsTableModel(QAbstractTableModel):
    def __init__(self, i_parent, *args):
        QAbstractTableModel.__init__(self, i_parent, *args)

    def rowCount(self, i_parent):  # override from QAbstractTableModel
        return len(g_detailPaneItemsAvailable) - len(g_detailPaneItems)

    def columnCount(self, i_parent):  # override from QAbstractTableModel
        return 1

    def data(self, i_index, i_role):  # override from QAbstractTableModel
        if not i_index.isValid():
            return None

        if i_index.column() == 0:
            if i_role == Qt.DisplayRole:
                unusedItems = sorted(list(g_detailPaneItemsAvailable - set(g_detailPaneItems)))
                return unusedItems[i_index.row()]
            elif i_role == Qt.TextAlignmentRole:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            if i_columnNo == 0:
                return "Available items"

        return None

class DetailPaneAvailableItemsTableView(QTableView):
    def __init__(self, i_parent=None):
        QTableView.__init__(self, i_parent)

        # Create model and set it in the table view
        self.tableModel = DetailPaneAvailableItemsTableModel(self)
        self.setModel(self.tableModel)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        #self.setDragDropMode(QAbstractItemView.InternalMove)
        #self.setDragEnabled(True)
        #self.setDropIndicatorShown(True)
        #self.setDragDropOverwriteMode(False)
        #self.setDefaultDropAction(Qt.MoveAction)
        #
        self.doubleClicked.connect(self.onDoubleClicked)
        #self.activated.connect(functools.partial(self.onActivatedOrClicked, True))

    requestMove = Signal(int)
    # Emitted when
    #  Item is double-clicked on.
    #
    # Params:
    #  i_rowNo:
    #   (int)

    def onDoubleClicked(self, i_modelIndex):
        """
        Params:
         i_modelIndex:
          (QModelIndex)
        """
        self.requestMove.emit(i_modelIndex.row())

# + + }}}

# + + Visible {{{

class DetailPaneVisibleItemsTableModel(QAbstractTableModel):
    def __init__(self, i_parent, *args):
        QAbstractTableModel.__init__(self, i_parent, *args)

    def rowCount(self, i_parent):  # override from QAbstractTableModel
        return len(g_detailPaneItems)

    def columnCount(self, i_parent):  # override from QAbstractTableModel
        return 1

    def data(self, i_index, i_role):  # override from QAbstractTableModel
        if not i_index.isValid():
            return None

        if i_index.column() == 0:
            if i_role == Qt.DisplayRole:
                return g_detailPaneItems[i_index.row()]
            elif i_role == Qt.TextAlignmentRole:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            if i_columnNo == 0:
                return "Visible items"

        return None

class DetailPaneVisibleItemsTableView(QTableView):
    def __init__(self, i_parent=None):
        QTableView.__init__(self, i_parent)

        # Create model and set it in the table view
        self.tableModel = DetailPaneVisibleItemsTableModel(self)
        self.setModel(self.tableModel)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        #self.setDragDropMode(QAbstractItemView.InternalMove)
        #self.setDragEnabled(True)
        #self.setDropIndicatorShown(True)
        #self.setDragDropOverwriteMode(False)
        #self.setDefaultDropAction(Qt.MoveAction)
        #
        self.doubleClicked.connect(self.onDoubleClicked)
        #self.activated.connect(functools.partial(self.onActivatedOrClicked, True))

        # + Mouse drag to reorder rows {{{

        self.viewport().installEventFilter(self)

        ## Receive mouse move events even if button isn't held down
        #self.setMouseTracking(True)

        # State used while reordering
        self.reorder_rowNo = None
        #  Either (int)
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

    requestMove = Signal(int)
    # Emitted when
    #  Item is double-clicked on.
    #
    # Params:
    #  i_rowNo:
    #   (int)

    def onDoubleClicked(self, i_modelIndex):
        """
        Params:
         i_modelIndex:
          (QModelIndex)
        """
        self.requestMove.emit(i_modelIndex.row())

    # + Mouse drag to reorder rows {{{

    def eventFilter(self, i_watched, i_event):
        if i_watched != self.viewport():
            return False
        #print(i_event.type())

        if i_event.type() == QEvent.MouseButtonPress:
            # If pressed the left button
            if i_event.button() == Qt.MouseButton.LeftButton:
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for vertical scroll amount
                mousePos = i_watched.mapTo(self.viewport(), i_event.pos())
                mousePos.setY(mousePos.y() + self.verticalScrollBar().value())

                self.reorder_rowNo = math.floor(mousePos.y() / self.verticalHeader().defaultSectionSize())
                if self.reorder_rowNo >= len(g_detailPaneItems):
                    self.reorder_rowNo = None
                else:
                    self.selectionModel().setCurrentIndex(self.selectionModel().model().index(self.reorder_rowNo, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

                    self.reorder_dropBeforeRowNo = self.reorder_rowNo

                    # Show drop indicator
                    dropIndicatorWidth = self.horizontalHeader().sectionSize(0) + self.horizontalHeader().sectionSize(1)
                    self.reorderIndicator_widget.setGeometry(0, self.horizontalHeader().height() + self.reorder_rowNo * self.verticalHeader().defaultSectionSize() - self.verticalScrollBar().value(), dropIndicatorWidth, self.verticalHeader().defaultSectionSize())
                    self.reorderIndicator_widget.show()
                    self.reorderIndicator_widget.raise_()

                    return True

        elif i_event.type() == QEvent.MouseMove:
            #print(i_event.type())
            # If currently reordering,
            # draw line at nearest horizontal edge
            if self.reorder_rowNo != None:
                # Get mouse pos relative to the ColumnNameBar
                # and adjust for vertical scroll amount
                mousePos = i_watched.mapTo(self.viewport(), i_event.pos())
                mousePos.setY(mousePos.y() + self.verticalScrollBar().value())

                #
                self.reorder_dropBeforeRowNo = math.floor(mousePos.y() / self.verticalHeader().defaultSectionSize() + 0.5)
                if self.reorder_dropBeforeRowNo > len(g_detailPaneItems):
                    self.reorder_dropBeforeRowNo = len(g_detailPaneItems)
                if self.reorder_dropBeforeRowNo < 0:
                    self.reorder_dropBeforeRowNo = 0

                # Move drop indicator
                dropIndicatorWidth = self.horizontalHeader().sectionSize(0) + self.horizontalHeader().sectionSize(1)
                if self.reorder_dropBeforeRowNo == self.reorder_rowNo or self.reorder_dropBeforeRowNo == self.reorder_rowNo + 1:
                    self.reorderIndicator_widget.setGeometry(0, self.horizontalHeader().height() + self.reorder_rowNo * self.verticalHeader().defaultSectionSize() - self.verticalScrollBar().value(), dropIndicatorWidth, self.verticalHeader().defaultSectionSize())
                else:
                    self.reorderIndicator_widget.setGeometry(0, self.horizontalHeader().height() + self.reorder_dropBeforeRowNo * self.verticalHeader().defaultSectionSize() - self.verticalScrollBar().value() - 2, dropIndicatorWidth, 6)

                return True

        elif i_event.type() == QEvent.MouseButtonRelease:
            # If currently reordering and released the left button
            if self.reorder_rowNo != None and i_event.button() == Qt.MouseButton.LeftButton:
                newPosition = detailPaneItems_move(self.reorder_rowNo, self.reorder_dropBeforeRowNo)

                # Stop reordering
                self.reorder_rowNo = None

                #
                self.reorderIndicator_widget.hide()
                self.repaint()

                #
                if newPosition != -1:
                    self.selectionModel().setCurrentIndex(self.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                    self.parent().change.emit()

                #
                return True

        # Let event continue
        return False

    # + }}}

# + + }}}

class DetailPaneItems(QWidget):
    change = Signal()

    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle("Detail pane items")
        self.setProperty("class", "detailPaneItems")

        # Window layout
        self.layout = QGridLayout()
        #self.layout.setSpacing(0)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.availableItemsLabel = QLabel("Available items")
        self.layout.addWidget(self.availableItemsLabel, 0, 0, 1, 1, Qt.AlignHCenter)

        self.availableItemsTableView = DetailPaneAvailableItemsTableView()
        self.layout.addWidget(self.availableItemsTableView, 1, 0, 2, 1)
        self.availableItemsTableView.requestMove.connect(self.useItemAtRowNo)

        #self.useItemButton = QPushButton(QApplication.style().standardIcon(QStyle.SP_ArrowRight), "")
        self.useItemButton = QToolButton()
        self.useItemButton.setArrowType(Qt.RightArrow)
        self.layout.addWidget(self.useItemButton, 1, 1, 1, 1, Qt.AlignBottom)
        self.useItemButton.clicked.connect(self.useItemButton_onClicked)

        self.unuseItemButton = QToolButton()
        self.unuseItemButton.setArrowType(Qt.LeftArrow)
        self.layout.addWidget(self.unuseItemButton, 2, 1, 1, 1, Qt.AlignTop)
        self.unuseItemButton.clicked.connect(self.unuseItemButton_onClicked)

        self.visibleItemsLabel = QLabel("Visible items")
        self.layout.addWidget(self.visibleItemsLabel, 0, 2, 1, 2, Qt.AlignHCenter)

        self.visibleItemsTableView = DetailPaneVisibleItemsTableView()
        self.layout.addWidget(self.visibleItemsTableView, 1, 2, 2, 2)
        self.visibleItemsTableView.requestMove.connect(self.unuseItem)

        self.moveVisibleItemUpButton = QToolButton()
        self.moveVisibleItemUpButton.setArrowType(Qt.UpArrow)
        self.layout.addWidget(self.moveVisibleItemUpButton, 4, 2, 1, 1, Qt.AlignRight)
        self.moveVisibleItemUpButton.clicked.connect(self.moveVisibleItemUpButton_onClicked)
        
        self.moveVisibleItemDownButton = QToolButton()
        self.moveVisibleItemDownButton.setArrowType(Qt.DownArrow)
        self.layout.addWidget(self.moveVisibleItemDownButton, 4, 3, 1, 1, Qt.AlignLeft)
        self.moveVisibleItemDownButton.clicked.connect(self.moveVisibleItemDownButton_onClicked)
        
        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)

        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 0)

    def useItem(self, i_item):
        detailPaneItems_use(i_item, len(g_detailPaneItems))

        #
        self.visibleItemsTableView.model().modelReset.emit()
        self.availableItemsTableView.model().modelReset.emit()
        self.change.emit()

    def useItemAtRowNo(self, i_rowNo):
        unusedItems = sorted(list(g_detailPaneItemsAvailable - set(g_detailPaneItems)))
        self.useItem(unusedItems[i_rowNo])

    def unuseItem(self, i_rowNo):
        detailPaneItems_unuse(i_rowNo)

        #
        self.visibleItemsTableView.model().modelReset.emit()
        self.availableItemsTableView.model().modelReset.emit()
        self.change.emit()

    def useItemButton_onClicked(self):
        unusedRowNo = self.availableItemsTableView.selectionModel().currentIndex().row()
        unusedItems = sorted(list(g_detailPaneItemsAvailable - set(g_detailPaneItems)))
        if unusedRowNo >= 0 and unusedRowNo < len(unusedItems):
            #insertAtRowNo = self.visibleItemsTableView.selectionModel().currentIndex().row()
            insertAtRowNo = len(g_detailPaneItems)
            self.useItem(unusedItems[unusedRowNo])

            #
            self.visibleItemsTableView.model().modelReset.emit()
            self.availableItemsTableView.model().modelReset.emit()
            self.change.emit()

    def unuseItemButton_onClicked(self):
        rowNo = self.visibleItemsTableView.selectionModel().currentIndex().row()
        if rowNo >= 0 and rowNo < len(g_detailPaneItems):
            self.unuseItem(rowNo)

    def moveVisibleItemUpButton_onClicked(self):
        rowNoToMove = self.visibleItemsTableView.selectionModel().currentIndex().row()
        if rowNoToMove > 0:
            newPosition = detailPaneItems_move(rowNoToMove, rowNoToMove - 1)

            #
            self.visibleItemsTableView.repaint()
            self.visibleItemsTableView.selectionModel().setCurrentIndex(self.visibleItemsTableView.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.change.emit()

    def moveVisibleItemDownButton_onClicked(self):
        rowNoToMove = self.visibleItemsTableView.selectionModel().currentIndex().row()
        if rowNoToMove < len(g_detailPaneItems) - 1:
            newPosition = detailPaneItems_move(rowNoToMove, rowNoToMove + 2)

            #
            self.visibleItemsTableView.repaint()
            self.visibleItemsTableView.selectionModel().setCurrentIndex(self.visibleItemsTableView.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.change.emit()

# + }}}
