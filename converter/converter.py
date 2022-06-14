#!/usr/bin/python
# -*- coding: utf-8 -*-


# Python std
import sys
import os
import os.path
#import sqlite3
#import functools
import glob

# Qt
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


scriptDirPath = os.path.dirname(os.path.realpath(__file__))


# + Quoting for different shells {{{

# + + Single argument {{{

import shlex
if hasattr(shlex, "quote"):
    quoteArgumentForBash = shlex.quote  # since Python 3.3
else:
    import pipes
    quoteArgumentForBash = pipes.quote  # before Python 3.3

def quoteArgumentForWindowsCmd(i_arg):
    return i_arg.replace("^", "^^") \
                .replace("(", "^(") \
                .replace(")", "^)") \
                .replace("%", "^%") \
                .replace("!", "^!") \
                .replace('"', '^"') \
                .replace('<', "^<") \
                .replace('>', "^>") \
                .replace('&', "^&") \
                .replace(" ", '" "')

import platform
if platform.system() == "Windows":
    quoteArgumentForNativeShell = quoteArgumentForWindowsCmd
else:
    quoteArgumentForNativeShell = quoteArgumentForBash

# + + }}}

# + }}}

import dan.streams
class AsyncQTimerSubprocess:
    def __init__(self, i_commandAndArguments, i_onOutput, i_onDone=None):
        """
        Params:
         i_commandAndArguments:
          Either (str)
           Command line to run in a shell
          or (list of str)
           Components of command line to run in a shell.
           This function will take care of quoting/escaping individual elements if necessary.
         i_onOutput:
          (function)
          Called when child program emits a line of output (on stdout or stderr).
          Function has:
           Params:
            i_line:
             (str)
         i_onDone:
          Either (function)
           Called when child program exits
           Function has:
            Params:
             i_exitCode:
              (int)
          or (None)
           Don't use this callback.
        """
        # If i_commandAndArguments is not a string (and presumably is a list),
        # convert it to one
        if type(i_commandAndArguments) != str:
            # Quote arguments if necessary before joining
            i_commandAndArguments = [quoteArgumentForNativeShell(arg)  for arg in i_commandAndArguments]
            i_commandAndArguments = " ".join(i_commandAndArguments)
        #print("AsyncQTimerSubprocess running:")
        #print(i_commandAndArguments)

        # Start program
        import subprocess
        self.popen = subprocess.Popen(i_commandAndArguments,
                                      shell=True,
                                      #bufsize=1, text=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Collect both its stdout and stderr streams in another thread
        self.streamReader = dan.streams.NonblockingMultipleStreamReader({
            "child_stdout": self.popen.stdout,
            "child_stderr": self.popen.stderr
        })

        # Start a Qt timer with a small interval to run its callback during idle processing time
        self.outputCheck_timer = QTimer()
        self.outputCheck_timer.setInterval(30)
        self.outputCheck_timer.timeout.connect(self.outputCheck_timer_onTimeout)
        self.outputCheck_timer.start()

        # Save callbacks
        self.onOutput = i_onOutput
        self.onDone = i_onDone

    def outputCheck_timer_onTimeout(self):
        """
        Callback that runs during idle processing time
        to handle process output
        """
        # Send any output to onOutput() callback
        while True:
            nextLine = self.streamReader.readLine(i_timeout = 0.0)
            if nextLine == None:
                break
            self.onOutput(nextLine[1].decode("utf-8").rstrip("\n"))

        # If process exited,
        # stop timer and call onDone() callback
        exitCode = self.popen.poll()
        if exitCode != None:
            self.outputCheck_timer.stop()
            if self.onDone != None:
                self.onDone(exitCode)


# Create a Qt application
# (or reuse old one if it already exists; ie. when re-running in REPL during development)
if not QApplication.instance():
    application = QApplication(sys.argv)
else:
    application = QApplication.instance()

# Create a top-level window by creating a widget with no parent
myWindow = QWidget()
#myWindow.adjustSize()
myWindow.resize(800, 400)
myWindow.move(QApplication.desktop().rect().center() - myWindow.rect().center())
myWindow.move(QApplication.desktop().rect().center() - myWindow.rect().center())
myWindow.setWindowTitle("PyGamebase converter")

main_vBoxLayout = QVBoxLayout()
main_vBoxLayout.setSpacing(0)
myWindow.setLayout(main_vBoxLayout)

# Auto-detect
autoDetectByGamebaseFolderButton = QPushButton("Try and auto-fill everything by choosing a GameBase folder...")
main_vBoxLayout.addWidget(autoDetectByGamebaseFolderButton, 0, Qt.AlignLeft)
def autoDetectByGamebaseFolderButton_onClicked():
    #file1Name = QFileDialog.getOpenFileName()
    dirPath = QFileDialog.getExistingDirectory(None, "Choose GameBase directory")
    if dirPath != "":
        dirPath = QDir.toNativeSeparators(dirPath)
        step1_accessDatabasePath_lineEdit.setText("")
        step1_sqliteDatabasePath_lineEdit.setText("")
        step2_gamesFolderPath_lineEdit.setText("")
        step2_screenshotsFolderPath_lineEdit.setText("")
        step2_musicFolderPath_lineEdit.setText("")
        step2_photosFolderPath_lineEdit.setText("")
        step2_extrasFolderPath_lineEdit.setText("")
        step3_gamebaseTitle_lineEdit.setText("")
        step3_emulatorExecutable_lineEdit.setText("")
        step3_adapterFile_lineEdit.setText("")

        #
        dirEntries = os.listdir(dirPath)
        #print(dirEntries)

        candidates = [e  for e in dirEntries  if e.upper().endswith(".MDB")]
        if len(candidates) > 0:
            step1_accessDatabasePath_lineEdit.setText(os.path.join(dirPath, candidates[0]))
            step1_sqliteDatabasePath_lineEdit.setText(os.path.join(dirPath, candidates[0])[:-4] + ".sqlite")
            step3_gamebaseTitle_lineEdit.setText(candidates[0][:-4].replace("_", " "))
            step3_adapterFile_lineEdit.setText(os.path.join(dirPath, candidates[0])[:-4] + ".py")

        candidates = [e  for e in dirEntries  if e.upper() == "GAMES"]
        if len(candidates) > 0:
            step2_gamesFolderPath_lineEdit.setText(os.path.join(dirPath, candidates[0]))

        candidates = [e  for e in dirEntries  if e.upper() == "SCREENSHOTS"]
        if len(candidates) > 0:
            step2_screenshotsFolderPath_lineEdit.setText(os.path.join(dirPath, candidates[0]))

        candidates = [e  for e in dirEntries  if e.upper() == "MUSIC" or e.upper() == "C64MUSIC"]
        if len(candidates) > 0:
            step2_musicFolderPath_lineEdit.setText(os.path.join(dirPath, candidates[0]))

        candidates = [e  for e in dirEntries  if e.upper() == "PHOTOS" or e.upper() == "MUSICIAN PHOTOS"]
        if len(candidates) > 0:
            step2_photosFolderPath_lineEdit.setText(os.path.join(dirPath, candidates[0]))

        candidates = [e  for e in dirEntries  if e.upper() == "EXTRAS"]
        if len(candidates) > 0:
            step2_extrasFolderPath_lineEdit.setText(os.path.join(dirPath, candidates[0]))

autoDetectByGamebaseFolderButton.clicked.connect(autoDetectByGamebaseFolderButton_onClicked)

def makeLabelledEditField(i_label, i_tooltip=None, i_comment=None, i_browseFor=None, i_browseCaption="", i_enabled=True, i_shareWidget=None):
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
                    path = QDir.toNativeSeparators(path)
                    lineEdit.setText(path)
            pushButton_browse.clicked.connect(pushButton_browse_onClicked)
        elif i_browseFor == "file":
            def pushButton_browse_onClicked():
                path, filter = QFileDialog.getOpenFileName(None, i_browseCaption)
                if path != "":
                    path = QDir.toNativeSeparators(path)
                    lineEdit.setText(path)
            pushButton_browse.clicked.connect(pushButton_browse_onClicked)

    return lineEdit

main_vBoxLayout.addSpacing(18)

tabWidget = QTabWidget()
main_vBoxLayout.addWidget(tabWidget)

# + Step 1: Convert database {{{

step1_tabPage_widget = QWidget()
tabWidget.addTab(step1_tabPage_widget, "Step 1")

step1_vBoxLayout = QVBoxLayout()
step1_tabPage_widget.setLayout(step1_vBoxLayout)

step1_label = QLabel("Convert database")
step1_label.setStyleSheet("QLabel { background-color: black; color: white; padding: 4px; font-weight: bold; font-size: 16px; }");
step1_vBoxLayout.addWidget(step1_label)
step1_labelDetail = QLabel("Convert Microsoft Access database (.mdb file) to a SQLite database (typically .db or .sqlite file)")
step1_labelDetail.setStyleSheet("QLabel { background-color: #666; color: white; padding: 4px; }");
step1_labelDetail.setWordWrap(True)
step1_vBoxLayout.addWidget(step1_labelDetail)

widget_group = QWidget()
# MDB tools location
step1_mdbToolsExeDirPath_lineEdit = makeLabelledEditField("MDB Tools location: ", i_comment="(Folder containing mdb-schema, mdb-tables and mdb-export;\nLeave blank if already in system PATH)", i_browseFor="directory", i_browseCaption="Choose directory with MDB Tools executables", i_shareWidget=widget_group)
# Access MDB database path
step1_accessDatabasePath_lineEdit = makeLabelledEditField("Access database file: ", i_browseFor="file", i_browseCaption="Choose Access database file", i_shareWidget=widget_group)
# SQLite database path
step1_sqliteDatabasePath_lineEdit = makeLabelledEditField("SQLite database file: ", i_comment="(if the above file exists, it will be overwritten)", i_browseFor="file", i_browseCaption="Choose SQLite database file", i_shareWidget=widget_group)
#
step1_vBoxLayout.addWidget(widget_group)

# Go
step1_go_button = QPushButton("Go")
step1_vBoxLayout.addWidget(step1_go_button, 0, Qt.AlignHCenter)
#

##
#sys.path.append("/home/daniel/docs/code/python")
#import mdb_to_sqlite
#import io
#import contextlib
#
#f = io.StringIO()
#with contextlib.redirect_stdout(f):
#    #do_something(my_object)
#    mdb_to_sqlite.convertMdbToSqlite(step1_accessDatabasePath_lineEdit.text(), step1_sqliteDatabasePath_lineEdit.text())
#out = f.getvalue()
#log_plainTextEdit.setPlainText(out)
#


currentSubprocess = None
def step1_go_button_onClicked():
    # Assemble command
    executableAndArgs = [scriptDirPath + os.sep + "utility_scripts" + os.sep + "mdb_to_sqlite.py", step1_accessDatabasePath_lineEdit.text(), step1_sqliteDatabasePath_lineEdit.text()]
    if step1_mdbToolsExeDirPath_lineEdit.text() != "":
        executableAndArgs += ["--mdbtools-exe-dir", step1_mdbToolsExeDirPath_lineEdit.text()]

    # Start log
    log_plainTextEdit.clear()
    log_plainTextEdit.appendPlainText("*** Running " + " ".join([quoteArgumentForNativeShell(arg)  for arg in executableAndArgs]) + "...")
    log_plainTextEdit.appendPlainText("")

    # Run command
    def onOutput(i_line):
        log_plainTextEdit.appendPlainText(i_line.rstrip("\r"))
    def onDone(i_exitCode):
        log_plainTextEdit.appendPlainText("")
        log_plainTextEdit.appendPlainText("*** Process exited with code " + str(i_exitCode))
        global currentSubprocess
        currentSubprocess = None
    global currentSubprocess
    currentSubprocess = AsyncQTimerSubprocess(executableAndArgs, onOutput, onDone)
step1_go_button.clicked.connect(step1_go_button_onClicked)

step1_vBoxLayout.addStretch()

# + }}}

# + Step 2: Fix file paths in database {{{

step2_tabPage_widget = QWidget()
tabWidget.addTab(step2_tabPage_widget, "Step 2")

step2_vBoxLayout = QVBoxLayout()
step2_tabPage_widget.setLayout(step2_vBoxLayout)

step2_label = QLabel("Fix file paths in database")
step2_label.setStyleSheet("QLabel { background-color: black; color: white; padding: 4px; font-weight: bold; font-size: 16px; }");
step2_vBoxLayout.addWidget(step2_label)
step2_labelDetail = QLabel("Change case (ie. upper/lower) of file paths in the database to match the paths that actually exist on the disk")
step2_labelDetail.setStyleSheet("QLabel { background-color: #666; color: white; padding: 4px; }");
step2_labelDetail.setWordWrap(True)
step2_vBoxLayout.addWidget(step2_labelDetail)

#widget_group = QWidget()
## SQLite database path
#step2_sqliteDatabasePath_lineEdit = makeLabelledEditField("SQLite database file: ", i_comment="(contents will be modified)", i_enabled=False, i_shareWidget=widget_group)
#step2_sqliteDatabasePath_lineEdit.setText("zxc")
#step2_vBoxLayout.addWidget(widget_group)

widget_group = QWidget()
# Games path
step2_gamesFolderPath_lineEdit = makeLabelledEditField("Games folder: ", i_browseFor="directory", i_browseCaption="Choose Games folder location", i_shareWidget=widget_group)
# Screenshots path
step2_screenshotsFolderPath_lineEdit = makeLabelledEditField("Screenshots folder: ", i_browseFor="directory", i_browseCaption="Choose Screenshots folder location", i_shareWidget=widget_group)
# Music path
step2_musicFolderPath_lineEdit = makeLabelledEditField("Music folder: ", i_browseFor="directory", i_browseCaption="Choose Music folder location", i_shareWidget=widget_group)
# Photos path
step2_photosFolderPath_lineEdit = makeLabelledEditField("Photos folder: ", i_browseFor="directory", i_browseCaption="Choose Photos folder location", i_shareWidget=widget_group)
# Extras path
step2_extrasFolderPath_lineEdit = makeLabelledEditField("Extras folder: ", i_browseFor="directory", i_browseCaption="Choose Extras folder location", i_shareWidget=widget_group)
#
step2_vBoxLayout.addWidget(widget_group)

step2_fromPreviousTabs_label = QLabel('("SQLite database file" from previous tab will be modified)')
step2_labelDetail.setWordWrap(True)
step2_vBoxLayout.addWidget(step2_fromPreviousTabs_label)

# Go
step2_go_button = QPushButton("Go")
step2_vBoxLayout.addWidget(step2_go_button, 0, Qt.AlignHCenter)
def step2_go_button_onClicked():
    # Assemble command
    executableAndArgs = [scriptDirPath + os.sep + "utility_scripts" + os.sep + "fix_path_case.py", step1_sqliteDatabasePath_lineEdit.text()]
    if step2_gamesFolderPath_lineEdit.text() != "":
        executableAndArgs += ["--games", step2_gamesFolderPath_lineEdit.text()]
    if step2_screenshotsFolderPath_lineEdit.text() != "":
        executableAndArgs += ["--screenshots", step2_screenshotsFolderPath_lineEdit.text()]
    if step2_musicFolderPath_lineEdit.text() != "":
        executableAndArgs += ["--music", step2_musicFolderPath_lineEdit.text()]
    if step2_photosFolderPath_lineEdit.text() != "":
        executableAndArgs += ["--photos", step2_photosFolderPath_lineEdit.text()]
    if step2_extrasFolderPath_lineEdit.text() != "":
        executableAndArgs += ["--extras", step2_extrasFolderPath_lineEdit.text()]
    executableAndArgs += ["--verbose"]

    # Start log
    log_plainTextEdit.clear()
    log_plainTextEdit.appendPlainText("*** Running " + " ".join([quoteArgumentForNativeShell(arg)  for arg in executableAndArgs]) + "...")
    log_plainTextEdit.appendPlainText("")

    # Run command
    def onOutput(i_line):
        log_plainTextEdit.appendPlainText(i_line.rstrip("\r"))
    def onDone(i_exitCode):
        log_plainTextEdit.appendPlainText("")
        log_plainTextEdit.appendPlainText("*** Process exited with code " + str(i_exitCode))
        global currentSubprocess
        currentSubprocess = None
    global currentSubprocess
    currentSubprocess = AsyncQTimerSubprocess(executableAndArgs, onOutput, onDone)
step2_go_button.clicked.connect(step2_go_button_onClicked)

step2_vBoxLayout.addStretch()

# + }}}

# + Step 3: Create frontend adapter file {{{

step3_tabPage_widget = QWidget()
tabWidget.addTab(step3_tabPage_widget, "Step 3")

step3_vBoxLayout = QVBoxLayout()
step3_tabPage_widget.setLayout(step3_vBoxLayout)

step3_label = QLabel("Create frontend adapter file")
step3_label.setStyleSheet("QLabel { background-color: black; color: white; padding: 4px; font-weight: bold; font-size: 16px;}");
step3_vBoxLayout.addWidget(step3_label)
step3_labelDetail = QLabel("Create a Python file to launch the frontend with in order to use it with this database and set of file folders. Note: this will only be a very minimal template - see the 'examples' directory for more developed examples!")
step3_labelDetail.setStyleSheet("QLabel { background-color: #666; color: white; padding: 4px; }");
step3_labelDetail.setWordWrap(True)
step3_vBoxLayout.addWidget(step3_labelDetail)

step3_fromPreviousTabs_label = QLabel('(Settings also used from previous tabs: "SQLite database file", "Games/Screenshots/Music/Photos/Extras folder")')
step3_labelDetail.setWordWrap(True)
step3_vBoxLayout.addWidget(step3_fromPreviousTabs_label)

widget_group = QWidget()
# GameBase title
step3_gamebaseTitle_lineEdit = makeLabelledEditField("GameBase title: ", i_tooltip='Human-friendly Gamebase title.\neg. "Gamebase64 v17" or "Commodore 64"', i_shareWidget=widget_group)
# Emulator executable
step3_emulatorExecutable_lineEdit = makeLabelledEditField("Emulator executable: ", i_browseFor="file", i_browseCaption="Choose emulator executable", i_shareWidget=widget_group)
# Adapter file path
step3_adapterFile_lineEdit = makeLabelledEditField("Adapter file: ", i_comment="(if the above file exists, it will be overwritten)", i_browseFor="file", i_browseCaption="Choose adapter file path", i_shareWidget=widget_group)
#
step3_vBoxLayout.addWidget(widget_group)

# Go
step3_go_button = QPushButton("Go")
step3_vBoxLayout.addWidget(step3_go_button, 0, Qt.AlignHCenter)
def step3_go_button_onClicked():
    log_plainTextEdit.clear()
    log_plainTextEdit.appendPlainText("*** Filling template...")

    script = '''\
# Python std
import os.path
import shutil
import tempfile
import pprint

# This program
import utils


# Frontend configuration
'''
    if step3_gamebaseTitle_lineEdit.text() != "":
        script += 'config_title = "' + step3_gamebaseTitle_lineEdit.text().replace('"', r'\"') + '"\n'
    if step1_sqliteDatabasePath_lineEdit.text() != "":
        script += 'config_databaseFilePath = "' + step1_sqliteDatabasePath_lineEdit.text().replace('"', r'\"') + '"\n'
    if step2_screenshotsFolderPath_lineEdit.text() != "":
        script += 'config_screenshotsBaseDirPath = "' + step2_screenshotsFolderPath_lineEdit.text().replace('"', r'\"') + '"\n'
    if step2_photosFolderPath_lineEdit.text() != "":
        script += 'config_photosBaseDirPath = "' + step2_photosFolderPath_lineEdit.text().replace('"', r'\"') + '"\n'
    if step2_musicFolderPath_lineEdit.text() != "":
        script += 'config_musicBaseDirPath = "' + step2_musicFolderPath_lineEdit.text().replace('"', r'\"') + '"\n'
    if step2_extrasFolderPath_lineEdit.text() != "":
        script += 'config_extrasBaseDirPath = "' + step2_extrasFolderPath_lineEdit.text().replace('"', r'\"') + '"\n'
    script += '''\


def runGame(i_gamePath, i_fileToRun = None, i_gameInfo = None):
    #print('runGame(' + pprint.pformat(i_gamePath) + ', ' + pprint.pformat(i_fileToRun) + ', ' + pprint.pformat(i_gameInfo) + ')')

    gamesBaseDirPath = "''' + step2_gamesFolderPath_lineEdit.text().replace('"', r'\"') + '''"
    tempDirPath = tempfile.gettempdir() + "/gamebase"

    # If file is a zip
    if utils.pathHasExtension(i_gamePath, ".ZIP"):
        # Extract it
        zipMembers = utils.extractZip(gamesBaseDirPath + "/" + i_gamePath, tempDirPath)
        gameFiles = zipMembers
    # Else if file is not a zip
    else:
        # Copy it
        shutil.copyfile(gamesBaseDirPath + i_gamePath, tempDirPath + "/" + os.path.basename(i_gamePath))
        gameFiles = [os.path.basename(i_gamePath)]

    #
    if i_fileToRun == None:
        gameFiles = utils.moveElementToFront(gameFiles, i_fileToRun)

    #
    command = ["''' + step3_emulatorExecutable_lineEdit.text().replace('"', r'\"') + '''"]
    command.extend(utils.joinPaths(tempDirPath, gameFiles))
    utils.shellStartTask(command)


def runExtra(i_extraPath, i_extraInfo, i_gameInfo):
    #print('runExtra(' + pprint.pformat(i_extraPath) + ', ' + pprint.pformat(i_extraInfo) + ', ' + pprint.pformat(i_gameInfo) + ')')

    # If file is a zip
    if utils.pathHasExtension(i_extraPath, ".ZIP"):
        # Extract it
        tempDirPath = tempfile.gettempdir() + "/gamebase"
        zipMembers = utils.extractZip(config_extrasBaseDirPath + "/" + i_extraPath, tempDirPath)

        #
        utils.openInDefaultApplication(zipMembers)
    else:
        utils.openInDefaultApplication(config_extrasBaseDirPath + "/" + i_extraPath)
'''

    log_plainTextEdit.appendPlainText("*** Writing to " + step3_adapterFile_lineEdit.text())
    with open(step3_adapterFile_lineEdit.text(), "w") as f:
        f.write(script)

    log_plainTextEdit.appendPlainText("*** Done.")

step3_go_button.clicked.connect(step3_go_button_onClicked)

step3_vBoxLayout.addStretch()

# + }}}

log_plainTextEdit = QPlainTextEdit()
main_vBoxLayout.addWidget(log_plainTextEdit)
#log_plainTextEdit.setPlainText("output...")
#
font = QFont("monospace")
font.setStyleHint(QFont.Monospace)
log_plainTextEdit.setFont(font)
#QFontInfo(font)


#main_vBoxLayout.addStretch()


myWindow.show()

# Enter Qt application main loop
exitCode = application.exec_()
#sys.exit(exitCode)
