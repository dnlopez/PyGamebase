
# Python std
import os.path
import urllib.parse
import math
import base64
import io
import tempfile
import zipfile

# Pillow
try:
    import PIL.Image
    g_havePil = True
except ImportError:
    g_havePil = False

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
import frontend_utils
import settings


detailPane_currentGameSchemaNameAndId = None

if "detailPaneItems" not in settings.viewSettings:
    settings.viewSettings["detailPaneItems"] = [
        "Name",
        "Year",
        "Screenshots (which aren't in table)",
        "Related games",
        "Memo text",
        "Comment",
        "Web links",
        "Non-image extras",
        "Image extras"
    ]
g_detailPaneItems = settings.viewSettings["detailPaneItems"]

g_detailPaneItemsAvailable = set([
    "Gamebase name",
    "Gamebase title",
    "Gamebase image",
    "Name",
    "Year",
    "Publisher",
    "Developer",
    "Programmer",
    "Genre",
    "Screenshots (all)",
    "Screenshots (which aren't in table)",
    "Related games",
    "Memo text",
    "Comment",
    "Web links",
    "Non-image extras",
    "Image extras"
])

class DetailPane(QWidget):

    requestGameSwitch = Signal(int)
    # Emitted when
    #  The detail pane wants to navigate to another game (the mouse was over the close button and the wheel was rolled)
    #
    # Params:
    #  i_direction:
    #   (int)
    #   1: Go to the next game
    #   -1: Go to the previous game

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

        # Default background colour if no stylesheet
        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        class Margin(QPushButton):
            def __init__(self, i_parent=None):
                super().__init__("x", i_parent)
            def wheelEvent(self, i_event):
                if i_event.pixelDelta().y() > 0:
                    self.parent().requestGameSwitch.emit(-1)
                elif i_event.pixelDelta().y() < 0:
                    self.parent().requestGameSwitch.emit(1)
        self.margin = Margin(self)
        self.margin.clicked.connect(self.margin_onClicked)
        self.layout.addWidget(self.margin)

        self.margin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        #self.margin.setFixedWidth(columns.tableColumn_getByPos(0)["width"])
        self.margin.setFixedWidth(columns.tableColumnSpec_getById("detail")["defaultWidth"])

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
                i_html = i_html.replace("<html><head>", "<html>\n<head>\n\n")
                i_html = i_html.replace("</head><body>", "\n</head>\n<body>\n\n  ")
                i_html = i_html.replace("</body></html>", "</body>\n</html>")
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

    requestGameNavigation = Signal(str, int)
    # Emitted when
    #  User clicks in the detail view on a link to another game
    #
    # Params:
    #  i_schemaName:
    #   (str)
    #  i_gameId:
    #   (int)

    adapterRunFunctionFinished = Signal()
    # Emitted when
    #  An adapter run...() command is returned from

    externalApplicationOpened = Signal()
    # Emitted when
    #  utils.openInDefaultApplication() is returned from

    def populateAG(self, i_adapterId, i_gameId):
        """
        Params:
         i_adapterId:
          (str)
         i_gameId:
          (int)
        """
        schemaName = gamebase.adapters[i_adapterId]["schemaName"]
        self.populateSAG(schemaName, i_adapterId, i_gameId)

    def populateSG(self, i_schemaName, i_gameId):
        """
        Params:
         i_schemaName:
          (str)
         i_gameId:
          (int)
        """
        adapterId = gamebase.schemaAdapterIds[i_schemaName]
        self.populateSAG(i_schemaName, adapterId, i_gameId)

    def populateSAG(self, i_schemaName, i_adapterId, i_gameId):
        """
        Params:
         i_adapterId:
          (str)
         i_gameId:
          (int)
        """
        self.webEngineView.setPage(None)
        if hasattr(self, "webEnginePage"):
            self.webEnginePage.setParent(None)
            #self.webEnginePage.deleteLater()
            #del(self.webEnginePage)
            self.webEnginePage = None

        gameRow = db.getGameRecord(i_schemaName, i_gameId, True)
        extrasRows = db.getExtrasRecords(i_schemaName, str(gameRow["Games.GA_Id"]))

        #
        global detailPane_currentGameSchemaNameAndId
        detailPane_currentGameSchemaNameAndId = (gameRow["SchemaName"], gameRow["Games.GA_Id"])

        # Save name for the titlebar of the view source window
        self.gameName = gameRow["Games.Name"]

        #
        html = ""

        if "detailPaneStylesheet" in settings.preferences and settings.preferences["detailPaneStylesheet"] != "":
            html += '  <link rel="stylesheet" type="text/css" href="file://' + urllib.parse.quote((settings.preferences["detailPaneStylesheet"]).replace("\\", "/")) + '">\n'

        def extraIsAnImage(i_extrasRow):
            """
            Params:
             i_extrasRow:
              (dict)

            Returns:
             (bool)
            """
            # If "Path" is an image,
            # return True
            path = i_extrasRow["Path"]
            if path != None:
                if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg") or path.lower().endswith(".gif") or path.lower().endswith(".png"):
                    return True
                # Else if "Path" is a zip, we can support images inside it
                elif path.lower().endswith(".zip"):
                    # If "FileToRun" is an image,
                    # return True
                    fileToRun = i_extrasRow.get("FileToRun", None)
                    if fileToRun != None:
                        if fileToRun.lower().endswith(".jpg") or fileToRun.lower().endswith(".jpeg") or fileToRun.lower().endswith(".gif") or fileToRun.lower().endswith(".png"):
                            return True
            #
            return False

        for item in g_detailPaneItems:
            if item == "Screenshots (all)":
                html += '  <div id="screenshots">\n'

                allScreenshotRelativePaths = gamebase.dbRow_allScreenshotRelativePaths(gameRow)
                for relativePath in allScreenshotRelativePaths:
                    screenshotUrl = gamebase.screenshotPath_relativeToUrl(i_adapterId, relativePath)
                    if screenshotUrl != None:
                        html += '    <a href="screenshot:///' + i_schemaName + '/' + relativePath + '"><img src="' + screenshotUrl + '"></a>\n'

                html += '  </div>'
                html += '\n\n'

            elif item == "Screenshots (which aren't in table)":
                html += '  <div id="screenshots">\n'

                randomPicColumns = [column  for column in columns.tableColumn_getBySlice()  if column["id"].startswith("random_pic[")]
                if len(randomPicColumns) == 0:
                    allScreenshotRelativePaths = gamebase.dbRow_allScreenshotRelativePaths(gameRow)
                    for screenshotNo, relativePath in enumerate(allScreenshotRelativePaths):
                        if columns.tableColumn_getById("pic[" + str(screenshotNo) + "]") == None:
                            screenshotUrl = gamebase.screenshotPath_relativeToUrl(i_adapterId, relativePath)
                            if screenshotUrl != None:
                                html += '    <a href="screenshot:///' + i_schemaName + '/' + relativePath + '"><img src="' + screenshotUrl + '"></a>\n'
                else:
                    relativePathsInTable = set()

                    randomScreenshotRelativePaths = gamebase.dbRow_allRandomScreenshotRelativePaths(gameRow)
                    for randomPicColumn in randomPicColumns:
                        randomPicNo = int(randomPicColumn["id"][11:-1])
                        if randomPicNo < len(randomScreenshotRelativePaths):
                            relativePathsInTable.add(randomScreenshotRelativePaths[randomPicNo])

                    picColumns = [column  for column in columns.tableColumn_getBySlice()  if column["id"].startswith("pic[")]
                    allScreenshotRelativePaths = gamebase.dbRow_allScreenshotRelativePaths(gameRow)
                    for picColumn in picColumns:
                        picNo = int(picColumn["id"][4:-1])
                        if picNo < len(allScreenshotRelativePaths):
                            relativePathsInTable.add(allScreenshotRelativePaths[picNo])

                    for screenshotNo, relativePath in enumerate(allScreenshotRelativePaths):
                        if relativePath not in relativePathsInTable:
                            screenshotUrl = gamebase.screenshotPath_relativeToUrl(i_adapterId, relativePath)
                            if screenshotUrl != None:
                                html += '    <a href="screenshot:///' + i_schemaName + '/' + relativePath + '"><img src="' + screenshotUrl + '"></a>\n'

                html += '  </div>'
                html += '\n\n'

            elif item == "Gamebase name":
                html += '  <div id="gamebase_name">' + i_schemaName + '</div>'
                html += '\n\n'

            elif item == "Gamebase title":
                html += '  <div id="gamebase_title">' + gamebase.gamebaseTitle(i_adapterId) + '</div>'
                html += '\n\n'

            elif item == "Gamebase image":
                gamebaseImageFilePath = gamebase.gamebaseImageFilePath(i_adapterId)
                if gamebaseImageFilePath != None:
                    html += '  <img id="gamebase_image" src="' + gamebaseImageFilePath + '" />'
                html += '\n\n'

            elif item == "Name":
                html += '  <div id="name">' + gameRow["Games.Name"] + '</div>'
                html += '\n\n'

            elif item == "Year":
                html += '  <div id="year">' + str(gameRow["Years.Year"]) + '</div>'
                html += '\n\n'

            elif item == "Publisher":
                html += '  <div id="publisher">' + str(gameRow["Publishers.Publisher"]) + '</div>'
                html += '\n\n'

            elif item == "Developer":
                html += '  <div id="developer">' + str(gameRow["Developers.Developer"]) + '</div>'
                html += '\n\n'

            elif item == "Programmer":
                html += '  <div id="programmer">' + str(gameRow["Programmers.Programmer"]) + '</div>'
                html += '\n\n'

            elif item == "Genre":
                html += '  <div id="genre">' + str(gameRow["PGenres.ParentGenre"]) + " : " + str(gameRow["Genres.Genre"]) + '</div>'
                html += '\n\n'

            elif item == "Related games":
                if ("Games.CloneOf_Name" in gameRow and gameRow["Games.CloneOf_Name"] != None) or \
                   ("Games.Prequel_Name" in gameRow and gameRow["Games.Prequel_Name"] != None) or \
                   ("Games.Sequel_Name" in gameRow and gameRow["Games.Sequel_Name"] != None) or \
                   ("Games.Related_Name" in gameRow and gameRow["Games.Related_Name"] != None):
                    html += '  <div id="related">\n'

                    # If there are related games,
                    # insert links to the originals
                    if "Games.CloneOf_Name" in gameRow and gameRow["Games.CloneOf_Name"] != None:
                        html += '    <p style="white-space: pre-wrap;">'
                        html += 'Clone of: '
                        html += '<a href="game:///' + i_schemaName + '/' + str(gameRow["Games.CloneOf"]) + '">' + gameRow["Games.CloneOf_Name"] + '</a>'
                        html += '</p>\n'

                    if "Games.Prequel_Name" in gameRow and gameRow["Games.Prequel_Name"] != None:
                        html += '    <p style="white-space: pre-wrap;">'
                        html += 'Prequel: '
                        html += '<a href="game:///' + i_schemaName + '/' + str(gameRow["Games.Prequel"]) + '">' + gameRow["Games.Prequel_Name"] + '</a>'
                        html += '</p>\n'

                    if "Games.Sequel_Name" in gameRow and gameRow["Games.Sequel_Name"] != None:
                        html += '    <p style="white-space: pre-wrap;">'
                        html += 'Sequel: '
                        html += '<a href="game:///' + i_schemaName + '/' + str(gameRow["Games.Sequel"]) + '">' + gameRow["Games.Sequel_Name"] + '</a>'
                        html += '</p>\n'

                    if "Games.Related_Name" in gameRow and gameRow["Games.Related_Name"] != None:
                        html += '    <p style="white-space: pre-wrap;">'
                        html += 'Related: '
                        html += '<a href="game:///' + i_schemaName + '/' + str(gameRow["Games.Related"]) + '">' + gameRow["Games.Related_Name"] + '</a>'
                        html += '</p>\n'

                    html += '  </div>'
                    html += '\n\n'

            elif item == "Memo text":
                # Insert memo text
                if gameRow["Games.MemoText"] != None:
                    html += '  <p id="memo_text" style="white-space: pre-wrap;">'
                    html += gameRow["Games.MemoText"]
                    html += '</p>'
                    html += '\n\n'

            elif item == "Comment":
                # Insert comment
                if gameRow["Games.Comment"] != None:
                    html += '  <p id="comment" style="white-space: pre-wrap;">'
                    html += gameRow["Games.Comment"]
                    html += '</p>'
                    html += '\n\n'

            elif item == "Web links":
                # Insert weblink(s)
                if "Games.WebLink_Name" in gameRow and gameRow["Games.WebLink_Name"] != None:
                    html += '  <p id="weblinks">\n'

                    html += "    " + gameRow["Games.WebLink_Name"] + ": "
                    url = gameRow["Games.WebLink_URL"]
                    html += '<a href="' + url + '">'
                    html += url
                    html += '</a>\n'
                    #link.addEventListener("click", function (i_event) {
                    #    i_event.preventDefault();
                    #    electron.shell.openExternal(this.href);
                    #});

                    # If it's a World Of Spectrum link then insert a corresponding Spectrum Computing link
                    if gameRow["Games.WebLink_Name"] == "WOS":
                        # Separator
                        html += '    <span style="margin-left: 8px; margin-right: 8px; border-left: 1px dotted #666;"></span>'
                        # Label
                        html += 'Spectrum Computing: '
                        # Link
                        url = url.replace("http://www.worldofspectrum.org/infoseekid.cgi?id=", "https://spectrumcomputing.co.uk/entry/")
                        html += '<a href="' + url + '">'
                        html += url
                        html += '</a>'
                        html += '</span>\n'
                        #link.addEventListener("click", function (i_event) {
                        #    i_event.preventDefault();
                        #    electron.shell.openExternal(this.href);
                        #});

                    html += '  </p>'
                    html += '\n\n'

            elif item == "Non-image extras":
                # Get only the extras which aren't images
                nonImageRows = [extrasRow  for extrasRow in extrasRows  if not extraIsAnImage(extrasRow)]

                # For each non-image, insert a link
                if len(nonImageRows) > 0:
                    html += '  <div id="nonImageExtras">\n'

                    for nonImageRowNo, nonImageRow in enumerate(nonImageRows):
                        html += "    "

                        if nonImageRowNo > 0:
                            #container.appendChild(document.createTextNode(" | "));
                            html += '<span style="margin-left: 8px; margin-right: 8px; border-left: 1px dotted #666;"></span>'

                        url = "extra:///" + i_schemaName
                        if nonImageRow["Path"] != None:
                            url += ":" + nonImageRow["Path"]
                            if nonImageRow.get("FileToRun", None) != None:
                                url += ":" + nonImageRow["FileToRun"]

                        html += '<a href="' + url + '" style="display: inline-block; text-align: center;">'
                        html += nonImageRow["Name"]
                        html += '</a>\n'

                    html += "  </div>"
                    html += '\n\n'

            elif item == "Image extras":
                # Get only the extras which are images
                imageRows = [extrasRow  for extrasRow in extrasRows  if extraIsAnImage(extrasRow)]

                # For each image extra, insert an image
                if len(imageRows) > 0:
                    html += '  <div id="imageExtras">\n'

                    for imageRowNo, imageRow in enumerate(imageRows):
                        html += "    "

                        url = "extra:///" + i_schemaName
                        url += ":" + imageRow["Path"]
                        if imageRow.get("FileToRun", None) != None:
                            url += ":" + imageRow["FileToRun"]

                        html += '<a href="' + url + '" style="display: inline-block; text-align: center;">'

                        if hasattr(gamebase.adapters[i_adapterId]["module"], "config_extrasBaseDirPath"):
                            if imageRow["Path"].lower().endswith(".zip"):
                                zipFilePath = gamebase.normalizeDirPathFromAdapter(gamebase.adapters[i_adapterId]["module"].config_extrasBaseDirPath) + os.sep + imageRow["Path"]
                                memberPath = imageRow["FileToRun"]
                                if g_havePil:
                                    # Load the file from the zip into memory
                                    imageBytes = gamebase.getZipMemberBytes(zipFilePath, memberPath)

                                    # Parse image,
                                    # convert colours to RGB
                                    # and save as JPEG, to make it smaller and mostly come within QtWebEngine/Chromium data URI size limits
                                    image = PIL.Image.open(io.BytesIO(imageBytes))
                                    #image = image.resize((image.width // 8, image.height // 8))
                                    if image.mode != "RGB":
                                        image = image.convert("RGB")
                                    imageBytesIo = io.BytesIO()
                                    image.save(imageBytesIo, format="JPEG")
                                    imageBytes = imageBytesIo.getvalue()

                                    # Convert to data URI
                                    encoded = base64.b64encode(imageBytes)
                                    imgSrc = "data:image/jpeg;base64," + str(encoded.decode())
                                else:
                                    # (Re-)create temporary directory
                                    # and extract image file to it
                                    tempDirPath = tempfile.gettempdir() + "/gamebase/images/" + os.path.basename(zipFilePath) + "/"
                                    frontend_utils.createTree(tempDirPath)
                                    zipFile = zipfile.ZipFile(zipFilePath)
                                    zipFile.extract(memberPath, tempDirPath)

                                    #
                                    imgSrc = tempDirPath + os.sep + memberPath
                            else:
                                imgSrc = 'file://' + urllib.parse.quote(gamebase.normalizeDirPathFromAdapter(gamebase.adapters[i_adapterId]["module"].config_extrasBaseDirPath) + "/" + imageRow["Path"])

                            html += '<img src="' + imgSrc + '" style="height: 300px;">'
                        #html += '<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" style="height: 300px;">'
                        html += '<div>' + imageRow["Name"] + '</div>'

                        html += '</a>\n'

                        #cell.appendChild(link);

                    html += "  </div>"
                    html += '\n\n'


        #print(html)
        #with open("/tmp/detail_pane.html", "w") as f:
        #    f.write(html)

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
                        # Strip protocol scheme
                        path = url[9:]
                        # Get and unquote schema name, and rest expected to be extra paths
                        schemaName, extraPaths = path.split(":", 1)
                        schemaName = urllib.parse.unquote(schemaName)
                        # Get and unquote single extra path, or file to run also
                        if extraPaths.find(":") == -1:
                            extraPath = extraPaths
                            extraPath = urllib.parse.unquote(extraPath)
                            fileToRun = None
                        else:
                            extraPath, fileToRun = extraPaths.split(":", 1)
                            extraPath = urllib.parse.unquote(extraPath)
                            fileToRun = urllib.parse.unquote(fileToRun)
                        #
                        extraInfo = [row  for row in self.extrasRows  if row["Path"] == extraPath][0]
                        gameInfo = self.gameRow
                        gameInfo = db.DbRecordDict(gameInfo)

                        try:
                            gamebase.adapters[i_adapterId]["module"].runExtra(extraPath, fileToRun, extraInfo, gameInfo)
                        except Exception as e:
                            import traceback
                            print(traceback.format_exc())
                            messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
                            messageBox.setText("<big><b>In runExtra():</b></big><pre>" + traceback.format_exc() + "</pre>")
                            messageBox.resizeToContent()
                            messageBox.exec()

                        self.parent().parent().adapterRunFunctionFinished.emit()

                    # Else if it's a link to a screenshot,
                    # open it with the default application
                    elif url.startswith("screenshot:///"):
                        # Strip protocol scheme
                        path = url[14:]
                        # Get and unquote schema name, and rest expected to be screenshot path
                        schemaName, screenshotPath = path.split("/", 1)
                        schemaName = urllib.parse.unquote(schemaName)
                        #
                        screenshotPath = urllib.parse.unquote(screenshotPath)
                        frontend_utils.openInDefaultApplication(gamebase.screenshotPath_relativeToAbsolute(i_adapterId, screenshotPath))
                        self.parent().parent().externalApplicationOpened.emit()

                    # If it's a link to a game,
                    # select it in the table view
                    elif url.startswith("game:///"):
                        # Strip protocol scheme
                        path = url[8:]
                        # Get and unquote schema name, and rest expected to be game ID
                        schemaName, gameId = path.split("/", 1)
                        schemaName = urllib.parse.unquote(schemaName)
                        #
                        gameId = urllib.parse.unquote(gameId)
                        gameId = int(gameId)

                        # Emit requestGameNavigation signal,
                        # but do so only when program is idle, by using a one-shot timer,
                        # else if a listener responds to the signal by repopulating the detail pane,
                        # there is a seg fault
                        self.gameNavigationSelectTimer = QTimer()
                        self.gameNavigationSelectTimer.setInterval(0)
                        self.gameNavigationSelectTimer.setSingleShot(True)
                        self.gameNavigationSelectTimer.timeout.connect(lambda: self.parent().parent().requestGameNavigation.emit(schemaName, gameId))
                        self.gameNavigationSelectTimer.start()
                        #self.parent().parent().requestGameNavigation.emit(schemaName, gameId)

                    # Else if it's a normal link,
                    # open it with the default browser
                    else:
                        QDesktopServices.openUrl(i_qUrl)

                    # Refuse navigation
                    return False

                else:
                    return True
        self.webEnginePage = WebEnginePage(gameRow, extrasRows, self.webEngineView)
        self.webEnginePage.setHtml(html, QUrl("file:///"))
        # Let background of application show through to stop white flash on page loads
        self.webEnginePage.setBackgroundColor(Qt.transparent)

        def webEnginePage_onLinkHovered(i_url):
            self.linkHovered.emit(i_url)
        self.webEnginePage.linkHovered.connect(webEnginePage_onLinkHovered)

        # Load web engine page into the web engine view
        #self.webEnginePage.setView(self.webEngineView)
        self.webEngineView.setPage(self.webEnginePage)

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

                self.invalidateAllData()

                # Stop reordering
                self.reorder_rowNo = None

                #
                self.reorderIndicator_widget.hide()

                #
                if newPosition != -1:
                    self.selectionModel().setCurrentIndex(self.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                    self.parent().change.emit()

                #
                return True

        # Let event continue
        return False

    # + }}}

    def invalidateAllData(self):
        self.model().dataChanged.emit(self.model().index(0, 0), self.model().index(0, len(g_detailPaneItems) - 1))

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
        
        self.closeButton = QPushButton("&Close")
        self.layout.addWidget(self.closeButton, 5, 0, 1, 4, Qt.AlignHCenter)
        self.closeButton.clicked.connect(self.close)

        self.escShortcut = QShortcut(QKeySequence("Escape"), self)
        self.escShortcut.activated.connect(self.close)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)

        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 0)

    def close(self):
        self.hide()

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
            self.visibleItemsTableView.invalidateAllData()

            #
            self.visibleItemsTableView.selectionModel().setCurrentIndex(self.visibleItemsTableView.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.change.emit()

    def moveVisibleItemDownButton_onClicked(self):
        rowNoToMove = self.visibleItemsTableView.selectionModel().currentIndex().row()
        if rowNoToMove < len(g_detailPaneItems) - 1:
            newPosition = detailPaneItems_move(rowNoToMove, rowNoToMove + 2)
            self.visibleItemsTableView.invalidateAllData()

            #
            self.visibleItemsTableView.selectionModel().setCurrentIndex(self.visibleItemsTableView.selectionModel().model().index(newPosition, 0), QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.change.emit()

# + }}}
