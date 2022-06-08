
# Python std
import os.path
import urllib.parse

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

        self.webEngineView = QWebEngineView()
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

        global detailPane_currentGameId
        detailPane_currentGameId = gameRow["Games.GA_Id"]

        html = ""

        html += '<link rel="stylesheet" type="text/css" href="file://' + os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + '/detail_pane.css">'

        # Insert screenshots after the first one
        supplementaryScreenshotRelativePaths = gamebase.dbRow_getSupplementaryScreenshotPaths(gameRow)
        for relativePath in supplementaryScreenshotRelativePaths:
            screenshotUrl = gamebase.getScreenshotUrl(relativePath)
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
        extrasRows = db.getExtrasRecords(str(gameRow["Games.GA_Id"]))

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
