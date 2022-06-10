
# Python std
import os.path
import json
import qt_extras

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


settingsDirPath = QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation) + os.sep + "pyGamebase"
def createSettingsDir():
    if not os.path.exists(settingsDirPath):
        os.makedirs(settingsDirPath)

values = {}

def loadViewSettings():
    """
    Load frontend configuration settings
    """
    global values

    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "view.json"
    if os.path.exists(settingsFilePath):
        try:
            with open(settingsFilePath, "rb") as f:
                values = json.loads(f.read().decode("utf-8"))
        except Exception as e:
            #import traceback
            #print("Failed to read frontend settings file: " + "\n".join(traceback.format_exception_only(e)))
            pass

def saveViewSettings():
    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "view.json"
    with open(settingsFilePath, "wb") as f:
        f.write(json.dumps(values, indent=4).encode("utf-8"))

    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation), "Save layout", "")
    #messageBox.setText("<big><b>Missing adapter setting:</b></big>")
    messageBox.setInformativeText("Saved settings to " + settingsFilePath + ".")
    messageBox.resizeToContent()
    messageBox.exec()
