
# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import settings


def makeLabelledEditField(i_label, i_tooltip=None, i_comment=None, i_browseFor=None, i_browseCaption="", i_enabled=True, i_shareWidget=None, i_onEditingFinished=None):
    """
    Params:
     i_label:
      (str)
     i_tooltip:
      Either (str)
      or (None)
     i_comment:
      Either (str)
      or (None)
     i_browseFor:
      Either (str)
       One of
        "directory"
        "file"
      or (None)
       Don't include a browse button.
     i_browseCaption:
      (str)
     i_shareWidget:
      Either (QWidget)
      or (None)
     i_onEditingFinished:
      Either (function)
      or (None)

    Returns:
     (QLineEdit)
    """
    if i_shareWidget:
        widget = i_shareWidget
    else:
        widget = QWidget()

    gridLayout = widget.layout()
    if gridLayout == None:
        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)
        gridLayout.setContentsMargins(0, 8, 0, 8)
        widget.setLayout(gridLayout)
        
    baseRowNo = gridLayout.rowCount()

    label = QLabel(i_label)
    gridLayout.addWidget(label, baseRowNo, 0)
    if i_tooltip != None:
        label.setToolTip(i_tooltip)

    lineEdit = QLineEdit()
    if i_onEditingFinished != None:
        lineEdit.editingFinished.connect(i_onEditingFinished)
    gridLayout.addWidget(lineEdit, baseRowNo, 1)
    lineEdit.setEnabled(i_enabled)
    if i_tooltip != None:
        lineEdit.setToolTip(i_tooltip)

    if i_comment != None:
        gridLayout.addWidget(QLabel(i_comment), baseRowNo + 1, 1)

    if i_browseFor != None:
        pushButton_browse = QPushButton("Browse...")
        gridLayout.addWidget(pushButton_browse, baseRowNo, 2)
        if i_browseFor == "directory":
            def pushButton_browse_onClicked():
                #file1Name = QFileDialog.getOpenFileName()
                path = QFileDialog.getExistingDirectory(None, i_browseCaption)
                if path != "":
                    lineEdit.setText(path)
                if i_onEditingFinished != None:
                    i_onEditingFinished()
            pushButton_browse.clicked.connect(pushButton_browse_onClicked)
        elif i_browseFor == "file":
            def pushButton_browse_onClicked():
                path, filter = QFileDialog.getOpenFileName(None, i_browseCaption)
                if path != "":
                    lineEdit.setText(path)
                if i_onEditingFinished != None:
                    i_onEditingFinished()
            pushButton_browse.clicked.connect(pushButton_browse_onClicked)

    return lineEdit


class PreferencesWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setWindowTitle("Preferences")
        self.setProperty("class", "preferences")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        tabWidget = QTabWidget()
        self.layout.addWidget(tabWidget)

        # + Style {{{

        style_tabPage_widget = QWidget()
        tabWidget.addTab(style_tabPage_widget, "Style")

        style_vBoxLayout = QVBoxLayout()
        style_tabPage_widget.setLayout(style_vBoxLayout)

        widget_group = QWidget()
        # Application stylesheet
        self.style_applicationStylesheet_lineEdit = makeLabelledEditField("Application stylesheet: ", i_browseFor="file", i_browseCaption="Choose application stylesheet", i_comment="(Requires application restart)\n", i_shareWidget=widget_group, i_onEditingFinished=self.setting_onEditingFinished)
        # Detail pane stylesheet
        self.style_detailPaneStylesheet_lineEdit = makeLabelledEditField("Detail pane stylesheet: ", i_browseFor="file", i_browseCaption="Choose detail pane stylesheet", i_shareWidget=widget_group, i_onEditingFinished=self.setting_onEditingFinished)
        #
        style_vBoxLayout.addWidget(widget_group)

        style_vBoxLayout.addStretch()

        self.closeButton = QPushButton("&Close")
        self.layout.addWidget(self.closeButton, 0, Qt.AlignCenter)
        self.closeButton.clicked.connect(self.close)

        #
        self.escShortcut = QShortcut(QKeySequence("Escape"), self)
        self.escShortcut.activated.connect(self.close)

    def close(self):
        self.hide()

    def setting_onEditingFinished(self):
        settings.preferences["applicationStylesheet"] = self.style_applicationStylesheet_lineEdit.text()
        settings.preferences["detailPaneStylesheet"] = self.style_detailPaneStylesheet_lineEdit.text()
        settings.savePreferences()

    def show(self):
        self.style_applicationStylesheet_lineEdit.setText(settings.preferences.get("applicationStylesheet", ""))
        self.style_detailPaneStylesheet_lineEdit.setText(settings.preferences.get("detailPaneStylesheet", ""))
        super().show()
        self.resize(800, self.height())
