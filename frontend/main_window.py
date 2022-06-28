
# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras
import column_filter_bar
import sql_filter_bar


class MainWindow(QWidget):
    def __init__(self, i_application): #, i_gamebase):
        # Create a top-level window by creating a widget with no parent
        QWidget.__init__(self, None)

        self.application = i_application
        #self.gamebase = i_gamebase

        self.setProperty("class", "mainWindow")

        #mainWindow.setStyleSheet("* {background-color: white; }")

        # Window layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.initDropFiles()

    # + Drop files {{{

    urlsDropped = Signal(list)
    # Emitted when
    #  Some URLs (files) are dropped on the window
    #
    # Params:
    #  i_urls:
    #   (list of QUrl)

    def initDropFiles(self):
        self.setAcceptDrops(True)

    def dragEnterEvent(self, i_event):  # override from QWidget
        i_event.acceptProposedAction()

    def dropEvent(self, i_event):  # override from QWidget
        mimeData = i_event.mimeData()
        if mimeData.hasUrls():
            self.urlsDropped.emit(mimeData.urls())

    # + }}}
