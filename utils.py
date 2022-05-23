
# Python std
import os
import sys
import platform
import subprocess
import shutil



#def openFileInDefaultApplication(i_filePath):
#    """
#    Params:
#     i_filePath:
#      (str)
#    """
#    # If on macOS
#    if platform.system() == "Darwin":
#        subprocess.call(("open", i_filePath))
#    # Else if on Windows
#    elif platform.system() == "Windows":
#        os.startfile(i_filePath)
#    # Else assume a Linux variant
#    else:
#        subprocess.call(("xdg-open", i_filePath))
def openInDefaultApplication(i_filePaths):
    """
    Params:
     i_filePaths:
      Either (str)
      or (list of str)
    """
    # Choose launcher command
    #  If on macOS
    if platform.system() == "Darwin":
        executableAndArgs = ["open"]
    #  Else if on Windows
    elif platform.system() == "Windows":
        executableAndArgs = ["start"]
    #  Else assume a Linux variant
    else:
        executableAndArgs = ["xdg-open"]

    # Append file paths
    if type(i_filePaths) == str:
        executableAndArgs.append(i_filePaths)
    else:  # if an array
        executableAndArgs.extend(i_filePaths)

    # Execute
    shellStartProcess(executableAndArgs)



# + Strings {{{

def stringEndsWith(i_str, i_endsWith, i_caseSensitive = False):
    """
    Params:
     i_str:
      (str)
     i_endsWith:
      (str)
     i_caseSensitive:
      (bool)

    Returns:
     (bool)
    """
    if not i_caseSensitive:
        i_str = i_str.upper()
        i_endsWith = i_endsWith.upper()

    return i_str.endswith(i_endsWith)

# + }}}

# + Path and file names {{{

def pathHasExtension(i_path, i_extensions, i_caseSensitive = False):
    """
    Test whether a path has a particular extension

    Params:
     i_path:
      (str)
      eg. "aaa/bbb/ccc.txt"
     i_extensions:
      Either (str)
       eg.
        ".txt"
      or (list of str)
       Return True if path has any one of these extensions.
       eg.
        [".txt", ".doc"]
     i_caseSensitive:
      (bool)

    Returns:
     (bool)
    """
    if type(i_extensions) == str:
        return stringEndsWith(i_path, i_extensions, i_caseSensitive)
    else:
        for extension in i_extensions:
            if stringEndsWith(i_path, extension, i_caseSensitive):
                return True
        return False

def joinPath(i_basePath, i_relativePath):
    """
    Params:
     i_basePath:
      (str)
      Trailing slashes are ignored.
     i_relativePath:
      (str)
      Leading slashes are ignored.

    Returns:
     (str)
    """
    import os.path
    return os.path.join(i_basePath, i_relativePath.lstrip("/"))

def joinPaths(i_basePath, i_relativePaths):
    """
    Params:
     i_basePath:
      (str)
      Trailing slashes are ignored.
     i_relativePaths:
      (list of str)
      Leading slashes are ignored.

    Returns:
     (list of str)
    """
    return [joinPath(i_basePath, relativePath)  for relativePath in i_relativePaths]

# + }}}

# + Zip files {{{

def extractZip(i_zipFilePath, i_destDirPath):
    """
    Params:
     i_zipFilePath:
      (str)
     i_destDirPath:
      (str)

    Returns:
     (list of str)
     Relative paths of files that have been extracted from zip.
    """
    #console.log('extractZip("' + i_zipFilePath + '")')

    #
    import zipfile
    archive = zipfile.ZipFile(i_zipFilePath)
    # [error here if file not found]

    # Extract to dest dir with overwriting allowed
    archive.extractall(i_destDirPath)

    # Get absolute paths of files (exclude directories)
    filePaths = [path  for path in archive.namelist()  if not path.endswith("/")]

    #
    return filePaths

# + }}}

# + Quoting arguments for different shells {{{

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

# + }}}

# + Running {{{

# For processes that you don't need to see logged in the GUI's "Subprocess output" window
# (eg. simply unarchiving or copying some files - though Python does also have internal libraries for those things):
#
#  startProcess() (with wrappers: directStartProcess(), shellStartProcess())
#   Start a subprocess, not waiting for it to finish.
#  runProcess() (with wrappers: directRunProcess(), shellRunProcess())
#   Start a subprocess, wait for it to finish, and receive back its output and exit code.
#
# For processes whose output you would like to see logged in the GUI's "Subprocess output" window
# (eg. running an emulator):
#
#  startTask() (with wrappers: directStartTask(), shellStartTask())
#   Start a subprocess, not waiting for it to finish.

def startProcess(i_viaShell, i_executableAndArguments):
    """
    Start a subprocess.

    Params:
     i_viaShell:
      (bool)
      False:
       Run directly, ie. not via a shell.
       [According to Python subprocess.Popen(), the executable might still be searched for in the $PATH]
      True:
       Run via the native shell, eg. bash on POSIX, or cmd on Windows.
     i_executableAndArguments:
      Either (list of str)
       The first element is the executable name, and the remaining elements are the executable arguments.
       Any sublists will be flattened to their elements before the above interpretation takes place.
       If individual elements contain any spaces, quotes or any such shell-sensitive characters,
       those characters will be (if i_viaShell is False) passed unmodified to the process, or (if i_viaShell is True) escaped, as appropriate.
       If you want to use shell features (with i_viaShell being True) like environment variables ($VARNAME) or redirection (>FILENAME) you must pass a string instead.
      or (str)
       Executable name and arguments, seperated by whitespace.
       Any spaces (or quotes or backslashes) that belong to a name or argument must be either escaped (by preceding with a backslash) or enclosed in quotes.
       (If i_viaShell == True, this argument type is the most direct and the splitting is done by the shell itself;
       else if i_viaShell == False, the Python function shlex.split() will be called to split the arguments to a list for subprocess.Popen().)

    Returns:
     (subprocess.Popen)
    """
    #print("startProcess(" + str(i_viaShell) + ", " + str(i_executableAndArguments))

    # If running directly (not via a shell),
    # Python's subprocess.Popen() works best with a list,
    # so do our own conversions to that
    if not i_viaShell:
        # If we have a string then split it with shlex.split()
        # else if we have a list then flatten it
        if isinstance(i_executableAndArguments, str):
            i_executableAndArguments = shlex.split(i_executableAndArguments)
        else:
            i_executableAndArguments = flattenList(i_executableAndArguments)
    # Else if running via a shell,
    # Python's subprocess.Popen() works best with a string,
    # so do our own conversions to that
    else:
        # If we have a string then nothing to do,
        # else if we have a list then flatten it, then quote and join the arguments
        if not isinstance(i_executableAndArguments, str):
            i_executableAndArguments = " ".join([quoteArgumentForNativeShell(arg)  for arg in flattenList(i_executableAndArguments)])

    # Start program with stderr merged into stdout and stdout readable through a pipe
    import subprocess
    popen = subprocess.Popen(i_executableAndArguments,
                             shell=i_viaShell,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Return Popen object
    return popen

def directStartProcess(i_executableAndArguments):
    return startProcess(False, i_executableAndArguments)

def shellStartProcess(i_executableAndArguments):
    return startProcess(True, i_executableAndArguments)

def runProcess(i_viaShell, i_executableAndArguments):
    """
    Start a subprocess and wait for it to finish,
    returning its exit code and output.

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (int)
       The program's exit code.
      1:
       (Python 2: str, Python 3: bytes)
       What the program wrote to stdout and stderr.
    """
    # Start process
    popen = startProcess(i_viaShell, i_executableAndArguments)

    # Wait for finish
    stdOutput, errOutput = popen.communicate()

    # Return exit code and output
    return (popen.returncode, stdOutput)

def directRunProcess(i_executableAndArguments):
    return runProcess(False, i_executableAndArguments)

def shellRunProcess(i_executableAndArguments):
    return runProcess(True, i_executableAndArguments)


# Python std
import threading

class Task():
    """
    Class to run a subprocess and asynchronously collect its output,
    to show in the frontend's "Subprocess output" window.

    After construction, see the following properties:
     executableAndArgs:
      (str)
      The command that was run (essentially a copy of the constructor argument i_executableAndArguments).
     popen:
      Either (None)
       The process failed to start
      or (subprocess.Popen)
       The process' Popen object.
       This could be used to get the running process ID (popen.pid).
     output:
      (str)
      The output (stdout and stderr combined) of the process so far.
     returncode:
      Either (None)
       The subprocess has not exited yet
      or (int)
       The subprocess exited with this exit code.
    """
    stdbufPath = shutil.which("stdbuf")

    def __init__(self, i_viaShell, i_executableAndArguments):
        # Initialize output variables
        self.executableAndArgs = None
        self.popen = None
        self.output = ""
        self.returncode = None

        # Start a subthread to start program and collect output
        self.thread = threading.Thread(target=self.thread_main, args=(i_viaShell, i_executableAndArguments))
        self.thread.start()

    def thread_main(self, i_viaShell, i_executableAndArguments):
        # If possible, turn off buffering in the program's standard streams
        # so stdout and stderr are returned in the correct order
        if Task.stdbufPath != None:
            if isinstance(i_executableAndArguments, str):
                i_executableAndArguments = Task.stdbufPath + " -i0 -o0 -e0 " + i_executableAndArguments
            else:
                i_executableAndArguments = [Task.stdbufPath, "-i0", "-o0", "-e0"] + i_executableAndArguments

        # Save actual command line that is about to be run
        self.executableAndArgs = i_executableAndArguments

        # Start program
        try:
            self.popen = startProcess(i_viaShell, i_executableAndArguments)
        except Exception as e:
            import traceback
            exceptionInfo = traceback.format_exc()
            print(exceptionInfo)
            self.output = exceptionInfo
            #self.output = "\n".join(exceptionInfo)
            return

        # Read output until streams close
        for line in iter(self.popen.stdout.readline, b''):
            line = line.decode("utf-8")
            # Save the output
            self.output += line
            # Also send output to stdout as normal
            sys.stdout.write(line)

        # Wait for program to exit (usually immediately after streams closed above) and save exit code
        self.returncode = self.popen.wait()

        print("Process exited with code " + str(self.returncode))

tasks = []

def startTask(i_viaShell, i_executableAndArguments):
    tasks.append(Task(i_viaShell, i_executableAndArguments))

def directStartTask(i_executableAndArguments):
    startTask(False, i_executableAndArguments)

def shellStartTask(i_executableAndArguments):
    startTask(True, i_executableAndArguments)

# + }}}

# + Lists {{{

def moveElementToFront(i_list, i_element):
    """
    Params:
     i_list:
      (list)
      List to maybe reorder
     i_element:
      Element to move to the front, if present in i_list

    Returns:
     (list)
    """
    if i_element not in i_list:
        return i_list

    elementPos = i_list.index(i_element)
    return [i_list[elementPos]] + i_list[0:elementPos] + i_list[elementPos + 1: ]

def flattenList(i_list):
    """
    [like dan.list.flattenList()]

    Flatten a list which may contain nested lists.

    Params:
     i_list:
      (list)
      A list which may contain nested lists.
      eg. [[1, 2, 3], [4, [5, 6]], 7, [8, 9]]

    Returns:
     (list)
     The list with elements of all sublists brought up to the top level.
      eg. [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    flattened = []
    for item in i_list:
        if isinstance(item, list):
            flattened.extend(flattenList(item))
        else:
            flattened.append(item)
    return flattened

# + }}}

# + Gemus utilities {{{

# http://www.gb64.com/oldsite/gemus.htm

class Gemus():
    def __init__(self, i_gemusText):
        """
        Params:
         i_gemusText:
          (str)
        """
        # Split lines, fields and values and store all in self.properties
        self.properties = {}
        lines = i_gemusText.split("\n")
        for line in lines:
            nameAndValue = line.split("=")
            if len(nameAndValue) >= 2:
                self.properties[nameAndValue[0]] = nameAndValue[1]

    def fieldIs(self, i_fieldName, i_value):
        """
        Params:
         i_fieldName:
          (str)
         i_value:
          (str)

        Returns:
         (bool)
        """
        return i_fieldName in self.properties and self.properties[i_fieldName] == i_value

    def fieldContains(self, i_fieldName, i_value):
        """
        Params:
         i_fieldName:
          (str)
         i_value:
          (str)

        Returns:
          (bool)
        """
        return i_fieldName in self.properties and self.properties[i_fieldName].find(i_value) != -1

    def fieldIsOneOf(self, i_fieldName, i_values):
        """
        Params:
         i_fieldName:
          (str)
         i_values:
          (list of str)

        Returns:
         (bool)
        """
        for value in i_values:
            if self.fieldIs(i_fieldName, value):
                return True
        return False

    def get(self, i_fieldName, i_caseSensitive=None):
        """
        Params:
         i_fieldName:
          (str)
         i_caseSensitive:
          Either (bool)
          or (None)
           Use default of false.

        Returns:
         Either (str)
         or (None)
        """
        # If don't care about case, normalize the name
        normalizedInputPropertyName = i_fieldName
        if not i_caseSensitive:
            normalizedInputPropertyName = normalizedInputPropertyName.upper()

        for propertyName in self.properties.keys():
            # If don't care about case, normalize the name
            normalizedPropertyName = propertyName
            if not i_caseSensitive:
                normalizedPropertyName = normalizedPropertyName.upper()

            # Compare them
            if normalizedPropertyName == normalizedInputPropertyName:
                return self.properties[propertyName]

        return None

# + }}}

# + MAME {{{

def allocateGameFilesToMameMediaSlots(i_gameFilePaths, io_availableDevices):
    """
    Params:
     i_gameFilePaths:
      (list of str)
     io_availableDevices:
      (list)
      Each element is:
       (list)
       List has elements:
        0:
         (str)
         Media/MAME command-line option name
         eg.
          "cassette"
          "cartridge"
          "floppydisk1"
        1:
         (list of str)
         Extensions of files which may go in the above slot
         eg.
          (for cassette) [".wav", ".cas"]

    Returns:
     Function return value:
      (list of str)
      MAME command-line options
     io_availableDevices:
      Used up devices will have been removed from this list.
    """
    args = []

    for gameFilePath in i_gameFilePaths:
        for availableDeviceNo, availableDevice in enumerate(io_availableDevices):
            deviceName, allowedFileExtensions = availableDevice

            if pathHasExtension(gameFilePath, allowedFileExtensions):
                args.extend(["-" + deviceName, gameFilePath])
                del(io_availableDevices[availableDeviceNo])
                break

    return args

# + }}}

# + Popup menu {{{

def popupMenu(i_itemTexts):
    """
    Params:
     i_itemTexts:
      (list of str)

    Returns:
     Either (str)
     or (None)
    """
    import frontend
    selectedItemNo = frontend.popupMenu(i_itemTexts)
    if selectedItemNo == None:
        return None
    else:
        return i_itemTexts[selectedItemNo]

# + }}}
