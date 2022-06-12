
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

# + Preferences {{{

preferences = {}

def loadPreferences():
    """
    Load frontend configuration settings
    """
    global preferences

    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "preferences.json"
    if os.path.exists(settingsFilePath):
        try:
            with open(settingsFilePath, "rb") as f:
                preferences = json.loads(f.read().decode("utf-8"))
        except Exception as e:
            #import traceback
            #print("Failed to read preferences file: " + "\n".join(traceback.format_exception_only(e)))
            pass

def savePreferences():
    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "preferences.json"
    with open(settingsFilePath, "wb") as f:
        f.write(json.dumps(preferences, indent=4).encode("utf-8"))

    #messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation), "Save preferences")
    #messageBox.setText("Saved preferences to " + settingsFilePath + ".")
    #messageBox.resizeToContent()
    #messageBox.exec()

# + }}}

# + View settings {{{

viewSettings = {}

def loadViewSettings():
    """
    Load frontend configuration settings
    """
    global viewSettings

    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "view.json"
    if os.path.exists(settingsFilePath):
        try:
            with open(settingsFilePath, "rb") as f:
                viewSettings = json.loads(f.read().decode("utf-8"))
        except Exception as e:
            #import traceback
            #print("Failed to read layout settings file: " + "\n".join(traceback.format_exception_only(e)))
            pass

def saveViewSettings():
    createSettingsDir()
    settingsFilePath = settingsDirPath + os.sep + "view.json"
    with open(settingsFilePath, "wb") as f:
        f.write(json.dumps(viewSettings, indent=4).encode("utf-8"))

    messageBox = qt_extras.ResizableMessageBox(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation), "Save layout")
    messageBox.setText("Saved layout settings to " + settingsFilePath + ".")
    messageBox.resizeToContent()
    messageBox.exec()

# + }}}
