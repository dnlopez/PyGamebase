# -*- coding: utf-8 -*-


# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *


class ResizableMessageBox(QDialog):
    def __init__(self, i_icon, i_title, i_text, i_buttons=QDialogButtonBox.Ok, i_parent=None, i_windowFlags=Qt.Dialog):
        """
        Params:
         i_icon:
          Either (QMessageBox.Icon)
           eg.
            self.style().standardIcon(QStyle.SP_MessageBoxCritical)
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
        self.layout.addWidget(self.iconLabel, 0, 0, 2, 1, Qt.AlignTop)
        if i_icon != None:
           self.iconLabel.setPixmap(i_icon.pixmap(128, 128))

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label, 0, 2, Qt.AlignTop)
        #2, 0: <PySide2.QtWidgets.QLabel(0x55f631f52a30, name="qt_msgbox_label") at 0x7fc7814ecf40>
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard|Qt.TextSelectableByKeyboard)

        self.informativeLabel = QLabel(self)
        self.informativeLabel.setWordWrap(True)
        self.layout.addWidget(self.informativeLabel, 1, 2, Qt.AlignTop)
        #2, 1: <PySide2.QtWidgets.QLabel(0x55f632830ea0, name="qt_msgbox_informativelabel") at 0x7fc7814ecfc0>
        self.informativeLabel.setTextInteractionFlags(Qt.TextSelectableByMouse|Qt.LinksAccessibleByMouse|Qt.LinksAccessibleByKeyboard|Qt.TextSelectableByKeyboard)

        self.buttons = QDialogButtonBox(i_buttons, self)
        self.layout.addWidget(self.buttons, 2, 0, 1, 3)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 0)

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
        informativeLabelFontMetrics = QFontMetrics(self.informativeLabel.property("font"))
        informativeLabelWidth = max([informativeLabelFontMetrics.horizontalAdvance(line)  for line in self.informativeLabel.text().split("\n")])

        #
        layoutContentsMargins = self.layout.contentsMargins()
        layoutSpacing = self.layout.spacing()

        #
        contentWidth = layoutContentsMargins.left() + self.layout.itemAtPosition(0, 0).geometry().width() + layoutSpacing + max(labelWidth, informativeLabelWidth) + layoutContentsMargins.right()
        if contentWidth > screenGeometry.width() - screenEdgeMargin:
            contentWidth = screenGeometry.width() - screenEdgeMargin

        #
        labelBoundingRect = labelFontMetrics.boundingRect(0, 0, contentWidth, screenGeometry.height() - screenEdgeMargin, Qt.TextWordWrap | Qt.TextExpandTabs, self.label.text(), 4);
        informativeLabelBoundingRect = informativeLabelFontMetrics.boundingRect(0, 0, contentWidth, screenGeometry.height() - screenEdgeMargin, Qt.TextWordWrap | Qt.TextExpandTabs, self.informativeLabel.text(), 4);
        contentHeight = layoutContentsMargins.top() + labelBoundingRect.height() + layoutSpacing + informativeLabelBoundingRect.height() + layoutSpacing + self.buttons.height() + layoutContentsMargins.bottom()
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

    def setInformativeText(self, i_text):
        self.informativeLabel.setText(i_text)

