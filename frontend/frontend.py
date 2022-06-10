
# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


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
