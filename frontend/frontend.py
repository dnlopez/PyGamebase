
# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

# This program
import qt_extras


def popupMenu(i_itemTexts):
    """
    Params:
     i_itemTexts:
      (list of str)

    Returns:
     Either (int)
     or (None)
    """
    # Create a menu
    # and add item texts as menu actions
    menu = QMenu(mainWindow)
    actions = []
    for itemText in i_itemTexts:
        #menu.addAction(QAction(itemText)) #, None))
        actions.append(menu.addAction(itemText))

    # Popup the menu at the current mouse position
    selectedAction = menu.exec_(QApplication.desktop().cursor().pos())

    # Return what was selected
    if selectedAction == None:
        return None
    else:
        return actions.index(selectedAction)

def messageBox(i_text, i_title, i_icon="information"):
    """
    Params:
     i_message:
      (str)
      May be a plain string, or rich text using a subset of HTML, see: https://doc.qt.io/qt-5/richtext-html-subset.html
       eg.
        "<p><big><b>Heading</b></big><p>Detailed information"
     i_title:
      (str)
     i_icon:
      Either (str)
       One of
        "information"
        "warning"
        "critical"
      or (None)
       No icon.
    """
    if i_icon == "information":
        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)
    elif i_icon == "warning":
        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
    elif i_icon == "critical":
        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical)
    else:
        icon = None

    messageBox = qt_extras.ResizableMessageBox(icon, i_title, i_text)
    messageBox.resizeToContent()
    messageBox.exec()
