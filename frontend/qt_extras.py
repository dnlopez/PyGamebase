# -*- coding: utf-8 -*-


# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *


class LineEditWithClearButton(QFrame):

    editingFinished = Signal(bool)
    # Emitted when any of the following happen:
    #  The line edit has focus and the Return or Enter key is pressed
    #  The line edit loses focus after its text has been modified
    #  The clear button is clicked
    #
    # Params:
    #  i_modified:
    #   (bool)
    #   True: the text was modified

    def __init__(self, i_height, i_parent=None):
        """
        Params:
         i_height:
          (int)
        """
        QFrame.__init__(self, i_parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("class", "LineEditWithClearButton")
        self.setAutoFillBackground(True)

        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setFixedHeight(i_height)
        self.layout.addWidget(self.lineEdit)
        self.layout.setStretch(0, 1)

        self.clearButton = QPushButton("", self)
        self.clearButton.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.clearButton.setStyleSheet("QPushButton { margin: 4px; border-width: 1px; border-radius: 10px; }");
        #self.clearButton.setFlat(True)
        self.clearButton.setFixedHeight(i_height)
        self.clearButton.setFixedWidth(i_height)
        self.clearButton.setFocusPolicy(Qt.NoFocus)
        self.clearButton.setVisible(False)
        self.layout.addWidget(self.clearButton)
        self.layout.setStretch(1, 0)
        self.clearButton.clicked.connect(self.clearButton_onClicked)

        self.lineEdit.textEdited.connect(self.lineEdit_onTextEdited)

        self.lineEdit.editingFinished.connect(self.onEditingFinished)

    # + Internal event handling {{{

    def lineEdit_onTextEdited(self, i_text):
        # Hide or show clear button depending on whether there's text
        self.clearButton.setVisible(i_text != "")

    def clearButton_onClicked(self):
        textWasModified = self.lineEdit.text != ""

        self.lineEdit.setText("")
        self.clearButton.setVisible(False)

        self.lineEdit.setModified(False)
        self.editingFinished.emit(textWasModified)

    def onEditingFinished(self):
        textWasModified = self.lineEdit.isModified()
        self.lineEdit.setModified(False)
        self.editingFinished.emit(textWasModified)

    # + }}}

    # + Text {{{

    def text(self):
        """
        Returns:
         (str)
        """
        return self.lineEdit.text()

    def setText(self, i_text):
        """
        Params:
         i_text:
          (str)
        """
        textChanged = i_text != self.lineEdit.text()
        self.lineEdit.setText(i_text)
        if textChanged:
            self.lineEdit_onTextEdited(i_text)

    # + }}}

    # + Focus {{{

    def setFocus(self, i_reason):
        self.lineEdit.setFocus(i_reason)

    # + }}}


class ResizableMessageBox(QDialog):
    def __init__(self, i_icon, i_title, i_text="", i_buttons=QDialogButtonBox.Ok, i_parent=None, i_windowFlags=Qt.Dialog):
        """
        Params:
         i_icon:
          Either (QMessageBox.Icon)
           eg.
            QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
          or (None)
         i_title:
          (str)
         i_text:
          (str)
         i_buttons:
          (QMessageBox.StandardButtons)
         i_parent:
          (QWidget)
         i_windowFlags:
          (Qt.WindowFlags)
        """
        QDialog.__init__(self, i_parent, i_windowFlags)

        self.layout = QGridLayout(self)

        self.iconLabel = QLabel(self)
        self.layout.addWidget(self.iconLabel, 0, 0, 1, 1, Qt.AlignTop)
        if i_icon != None:
           self.iconLabel.setPixmap(i_icon.pixmap(128, 128))

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label, 0, 2, 1, 1, Qt.AlignTop)
        #2, 0: <PySide2.QtWidgets.QLabel(0x55f631f52a30, name="qt_msgbox_label") at 0x7fc7814ecf40>
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard|Qt.TextSelectableByKeyboard)

        self.buttons = QDialogButtonBox(i_buttons, self)
        self.layout.addWidget(self.buttons, 1, 0, 1, 3)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.setFocus()

        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)

        self.setWindowTitle(i_title)
        self.setText(i_text)

    def resizeToContent(self):
        # Get dimensions of screen
        # and choose the margin we want to keep from the edge
        screen = QGuiApplication.primaryScreen()
        screenGeometry = screen.geometry()
        screenEdgeMargin = 100

        # Get dimensions of text when unwrapped
        labelFontMetrics = QFontMetrics(self.label.property("font"))
        labelWidth = max([labelFontMetrics.horizontalAdvance(line)  for line in self.label.text().split("\n")])

        #
        layoutContentsMargins = self.layout.contentsMargins()
        layoutSpacing = self.layout.spacing()

        #
        contentWidth = layoutContentsMargins.left() + self.layout.itemAtPosition(0, 0).geometry().width() + layoutSpacing + labelWidth + layoutContentsMargins.right()
        if contentWidth > screenGeometry.width() - screenEdgeMargin:
            contentWidth = screenGeometry.width() - screenEdgeMargin

        #
        labelBoundingRect = labelFontMetrics.boundingRect(0, 0, contentWidth, screenGeometry.height() - screenEdgeMargin, Qt.TextWordWrap | Qt.TextExpandTabs, self.label.text(), 4);
        contentHeight = layoutContentsMargins.top() + labelBoundingRect.height() + layoutSpacing + self.buttons.height() + layoutContentsMargins.bottom()
        if contentHeight > screenGeometry.height() - screenEdgeMargin:
            contentHeight = screenGeometry.height() - screenEdgeMargin

        #
        self.resize(contentWidth, contentHeight)

    """
    def resizeEvent(self, event):
        _result = super().resizeEvent(event)
        print("---")
        print(str(self.label.width()) + ", " + str(self.label.height()))
        print(str(self.iconLabel.width()) + ", " + str(self.label.height()))
        print(str(self.buttons.width()) + ", " + str(self.label.height()))

        self.setFixedWidth(self._width)

        _text_box = self.findChild(QTextEdit)
        if _text_box is not None:
            # get width
            _width = int(self._width - 50)  # - 50 for border area
            # get box height depending on content
            _font = _text_box.document().defaultFont()
            _fontMetrics = QFontMetrics(_font)
            _textSize = _fontMetrics.size(0, details_box.toPlainText(), 0)
            _height = int(_textSize.height()) + 30  # Need to tweak
            # set size
            _text_box.setFixedSize(_width, _height)
    """

    def setText(self, i_text):
        self.label.setText(i_text)



class StayOpenMenu(QMenu):
    """
    A menu which stays open after something is selected
    so you can make multiple selections in one go.
    """
    def __init__(self, i_title, i_parent=None):
        QMenu.__init__(self, i_title, i_parent)

    #    # Install event filter to watch for clicks
    #    self.installEventFilter(self)
    #
    #def eventFilter(self, i_watched, i_event):
    #    if i_event.type() == QEvent.MouseButtonRelease:
    #        if i_watched.activeAction():
    #            # If the selected action does not have a submenu,
    #            # trigger the function and eat the event
    #            if not i_watched.activeAction().menu():
    #                i_watched.activeAction().trigger()
    #                return True
    #    return QMenu.eventFilter(self, i_watched, i_event)

    def mouseReleaseEvent(self, i_event):
        # If there is an active action and it's not a submenu,
        # trigger that action and don't pass the event to the subclass to keep the menu open
        if self.activeAction() and not self.activeAction().menu():
            self.activeAction().trigger()
            return

        #
        QMenu.mouseReleaseEvent(self, i_event)

    def keyPressEvent(self, i_event):
        # If pressing a key that would normally select
        # and there is an active action and it's not a submenu,
        # trigger that action and don't pass the event to the subclass to keep the menu open
        if (i_event.key() == Qt.Key_Return or i_event.key() == Qt.Key_Enter) and \
           self.activeAction() and not self.activeAction().menu():
            self.activeAction().trigger()
            return

        #
        QMenu.keyPressEvent(self, i_event)


class PlainTextViewer(QWidget):
    def __init__(self, i_parent=None):
        QWidget.__init__(self, i_parent)

        #self.setWindowTitle("Subprocess Output")
        #self.setGeometry(50, 75, 600, 400)

        self.layout = QVBoxLayout(self)

        # + Toolbar {{{

        self.toolbar = QWidget()
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar_layout.addWidget(QLabel("Wrap text:"))
        wrapTextCheckBox = QCheckBox(self.toolbar)
        wrapTextCheckBox.stateChanged.connect(self.wrapTextCheckBox_onStateChanged)
        self.toolbar_layout.addWidget(wrapTextCheckBox)
        self.toolbar_layout.addStretch()
        self.layout.addWidget(self.toolbar)

        # + }}}

        self.plainTextEdit = QPlainTextEdit(self)
        self.layout.addWidget(self.plainTextEdit)

        self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)
        #self.plainTextEdit.setUndoRedoEnabled(False)

        font = QFont("monospace")
        font.setStyleHint(QFont.Monospace)
        self.plainTextEdit.setFont(font)
        #self.plainTextEdit.document().setDefaultFont(QFont("monospace", 10, QFont.Normal))

    def wrapTextCheckBox_onStateChanged(self, i_state):
        if i_state == Qt.Checked:
            self.plainTextEdit.setWordWrapMode(QTextOption.WrapAnywhere)
        else:
            self.plainTextEdit.setWordWrapMode(QTextOption.NoWrap)

    def setText(self, i_text):
        """
        Params:
         i_text:
          (str)
        """
        self.plainTextEdit.setPlainText(i_text)
