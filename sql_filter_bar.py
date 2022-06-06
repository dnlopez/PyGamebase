
# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *

# This program
import qt_extras


# + SQL filter bar {{{

class SqlFilterBar(qt_extras.LineEditWithClearButton):
    editingFinished = Signal(bool)
    # Params:
    #  i_modified:
    #   (bool)
    #   True: the text in the filter text box was changed

    filterRowHeight = 30

    def __init__(self, i_parent=None):
        qt_extras.LineEditWithClearButton.__init__(self, SqlFilterBar.filterRowHeight, i_parent)

        self.lineEdit.editingFinished.connect(self.lineEdit_onEditingFinished)

    # + Internal event handling {{{

    def lineEdit_onEditingFinished(self):
        # If text was modified, requery,
        # else focus the tableview
        textWasModified = self.lineEdit.isModified()
        self.lineEdit.setModified(False)
        self.editingFinished.emit(textWasModified)

    # + }}}

    def userSetText(self, i_text):
        """
        Params:
         i_text:
          (str)
        """
        textChanged = i_text != self.lineEdit.text()
        self.lineEdit.setText(i_text)
        if textChanged:
            self.editingFinished.emit(True)

    # + Focus {{{

    def setFocus(self, i_reason):
        self.lineEdit.setFocus(i_reason)

    # + }}}

# + }}}
