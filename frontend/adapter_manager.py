
# Python std
#

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import gamebase
import db
import qt_extras
#import columns


def openAdapter(i_adapterFilePath):
    """
    Params:
     i_adapterFilePath:
      (str)

    Returns:
     Either (str)
      Unique ID string for loaded adapter.
     or (None)
      Adapter (or database) failed to open.
    """
    # If adapter is already loaded,
    # just reload the module
    adapterId = gamebase.adapterFilePathToAdapterId(i_adapterFilePath)
    if gamebase.adapterIsLoaded(adapterId):
        gamebase.reloadAdapter(adapterId)
        return adapterId

    # Import specified adapter module
    try:
        adapterId = gamebase.importAdapter(i_adapterFilePath)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
        messageBox.setText("<b>In adapter file:</b>\n<p><pre>" + i_adapterFilePath + "</pre>\n<p><b>While importing, an error occurred:</b>\n<p><pre>" + traceback.format_exc() + "</pre>\n")
        messageBox.resizeToContent()
        messageBox.exec()

        return None

    # If there isn't a database file path,
    # show error message, undo adapter import and stop
    if not hasattr(gamebase.adapters[adapterId]["module"], "config_databaseFilePath"):
        messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
        messageBox.setText("<b>In adapter file:</b>\n<p><pre>" + i_adapterFilePath + "</pre>\n<p><b>A required setting is missing:</b>\n<p><pre>config_databaseFilePath</pre>\n<p><b>This file will not be loaded.</b>")
        messageBox.resizeToContent()
        messageBox.exec()

        gamebase.forgetAdapter(adapterId)
        return None

    # Generate new schema name
    schemaName = db.sanitizeSchemaName(adapterId)
    gamebase.setAdapterSchemaName(adapterId, schemaName)

    # Open the database
    # and if it failed, show error message, undo adapter import and stop
    try:
        db.openDb(schemaName, gamebase.normalizeDirPathFromAdapter(gamebase.adapters[adapterId]["module"].config_databaseFilePath))
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical), "Error")
        messageBox.setText("<b>In adapter file:</b>\n<p><pre>" + i_adapterFilePath + "</pre>\n<p><b>When opening database file:</b>\n<p><pre>" + gamebase.adapters[adapterId]["module"].config_databaseFilePath + "</pre>\n<p><b>An error occurred:</b>\n<p><pre>" + "<br>\n".join(traceback.format_exception_only(e.__class__, e)) + "</pre>\n<p><b>This file will not be loaded.</b>")
        messageBox.resizeToContent()
        messageBox.exec()

        gamebase.forgetAdapter(adapterId)
        return None

    #
    return adapterId

def forgetAdapter(i_adapterId):
    """
    Params:
     i_adapterId:
      (str)
    """
    # Close the database
    db.closeDb(gamebase.adapters[i_adapterId]["schemaName"])

    # Forget the adapter
    gamebase.forgetAdapter(i_adapterId)


def selectAndOpenAdapter():
    """
    Returns:
     (bool)
     True:
      One or more new adapters were chosen and opened
    """
    # Show file selector for adapter modules
    # and if cancelled, return False
    fileDialog = QFileDialog(None, "Select Gamebase adapter file(s)")
    fileDialog.setFilter(QDir.Files)
    fileDialog.setFileMode(QFileDialog.ExistingFiles)
    #fileDialog.setOptions(QFileDialog.DontUseNativeDialog)
    fileDialog.setNameFilters(["Python adapter modules (*.py)", "All files (*)"])
    if not fileDialog.exec_():
        return False

    # Open each selected adapter file
    atLeastOneAdapterOpened = False
    filePaths = fileDialog.selectedFiles()
    for filePath in filePaths:
        if openAdapter(filePath) != None:
            atLeastOneAdapterOpened = True

    return atLeastOneAdapterOpened


# + Table view {{{

class AdapterTableViewModel(QAbstractTableModel):
    def __init__(self, i_parent, *args):
        QAbstractTableModel.__init__(self, i_parent, *args)

    def rowCount(self, i_parent):  # override from QAbstractTableModel
        return len(gamebase.adapters)

    def columnCount(self, i_parent):  # override from QAbstractTableModel
        return 1

    def data(self, i_index, i_role):  # override from QAbstractTableModel
        if not i_index.isValid():
            return None

        if i_index.column() == 0:
            if i_role == Qt.DisplayRole:
                rowNo = i_index.row()
                return list(gamebase.adapters.keys())[rowNo]
            elif i_role == Qt.TextAlignmentRole:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def headerData(self, i_columnNo, i_orientation, i_role):
        if i_orientation == Qt.Horizontal and i_role == Qt.DisplayRole:
            if i_columnNo == 0:
                return "Available items"

        return None

class AdapterTableView(QTableView):
    def __init__(self, i_parent=None):
        QTableView.__init__(self, i_parent)

        # Create model and set it in the table view
        self.tableModel = AdapterTableViewModel(self)
        self.setModel(self.tableModel)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        #self.doubleClicked.connect(self.onDoubleClicked)
        #self.activated.connect(functools.partial(self.onActivatedOrClicked, True))

    def onDoubleClicked(self, i_modelIndex):
        """
        Params:
         i_modelIndex:
          (QModelIndex)
        """
    #    self.requestMove.emit(i_modelIndex.row())

# + }}}

class AdapterManager(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle("Add/remove Gamebases")
        self.setProperty("class", "adapterManager")

        # Window layout
        self.layout = QGridLayout()
        #self.layout.setSpacing(0)
        #self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.visibleItemsLabel = QLabel("Loaded adapters")
        self.layout.addWidget(self.visibleItemsLabel, 0, 0, 1, 1, Qt.AlignHCenter)

        self.adapterTableView = AdapterTableView()
        self.layout.addWidget(self.adapterTableView, 1, 0, 1, 1)

        self.buttonContainer = QWidget(self)
        self.buttonLayout = QVBoxLayout(self.buttonContainer)
        #self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonContainer.setLayout(self.buttonLayout)

        self.addItemsButton = QPushButton("&Add...")
        self.buttonLayout.addWidget(self.addItemsButton)
        self.addItemsButton.clicked.connect(self.addItemsButton_onClicked)

        self.reloadItemButton = QPushButton("R&eload")
        self.buttonLayout.addWidget(self.reloadItemButton)
        self.reloadItemButton.clicked.connect(self.reloadItemButton_onClicked)

        self.reloadAllItemButton = QPushButton("Reload a&ll")
        self.buttonLayout.addWidget(self.reloadAllItemButton)
        self.reloadAllItemButton.clicked.connect(self.reloadAllItemButton_onClicked)

        self.removeItemButton = QPushButton("&Remove")
        self.buttonLayout.addWidget(self.removeItemButton)
        self.removeItemButton.clicked.connect(self.removeItemButton_onClicked)

        self.layout.addWidget(self.buttonContainer, 1, 1, 1, 1, Qt.AlignTop)

        #self.dialogButtons = QDialogButtonBox(QDialogButtonBox.Cancel, self)
        #self.layout.addWidget(self.dialogButtons, 3, 0, 1, 2, Qt.AlignHCenter)
        #self.dialogButtons.accepted.connect(self.dialogButtons_onAccept)

        self.closeButton = QPushButton("&Close")
        self.layout.addWidget(self.closeButton, 2, 0, 1, 2, Qt.AlignHCenter)
        self.closeButton.clicked.connect(self.closeButton_onClicked)

        #self.layout.setColumnStretch(0, 2)
        #self.layout.setColumnStretch(1, 0)
        #self.layout.setColumnStretch(2, 1)
        #self.layout.setColumnStretch(3, 1)

        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 0)

    def showEvent(self, i_event):
        self.adapterTableView.model().modelReset.emit()
        self.adapterTableView.setFocus()

    def closeButton_onClicked(self):
        self.hide()

    adaptersChanged = Signal()
    # Emitted when
    #  One or more adapters are added, reloaded or removed

    def addItemsButton_onClicked(self):
        if selectAndOpenAdapter():
            self.adapterTableView.model().modelReset.emit()
            self.adaptersChanged.emit()

    def reloadItemButton_onClicked(self):
        currentIndex = self.adapterTableView.selectionModel().currentIndex()
        adapterId = self.adapterTableView.model().data(currentIndex, Qt.DisplayRole)

        gamebase.reloadAdapter(adapterId)
        self.adaptersChanged.emit()

    def reloadAllItemButton_onClicked(self):
        for adapterId in gamebase.adapters.keys():
            print(adapterId)
            gamebase.reloadAdapter(adapterId)
        self.adaptersChanged.emit()

    def removeItemButton_onClicked(self):
        currentIndex = self.adapterTableView.selectionModel().currentIndex()
        adapterId = self.adapterTableView.model().data(currentIndex, Qt.DisplayRole)

        forgetAdapter(adapterId)

        self.adapterTableView.model().modelReset.emit()
        self.adaptersChanged.emit()
