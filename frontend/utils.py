
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

def findFileSequence(i_baseDirPath, i_filePath):
    """
    Find additional files that exist for as long as
    the last number is incremented or the last uppercase letter is advanced through the alphabet.

    Params:
     i_baseDirPath:
      (str)
      eg.
       "/home/daniel/gamebases/Gamebase Amiga 2.3/Games"
       "/home/daniel/gamebases/Amstrad CPC/Games"
     i_filePath:
      (str)
      eg.
       "A/Air Warrior_Disk1.zip"
       "C/Cabal (E) - Side A.cdt"
       "G/Game, Set & Match 2 (E) - Side 1A.cdt"

    Returns:
     (list of str)
     eg.
      ["A/Air Warrior_Disk1.zip", "A/Air Warrior_Disk2.zip", "A/Air Warrior_Disk3.zip"]
      ["C/Cabal (E) - Side A.cdt", "C/Cabal (E) - Side B.cdt"]
      ["G/Game, Set & Match 2 (E) - Side 1A.cdt", "G/Game, Set & Match 2 (E) - Side 1B.cdt", "G/Game, Set & Match 2 (E) - Side 2A.cdt", "G/Game, Set & Match 2 (E) - Side 2B.cdt", "G/Game, Set & Match 2 (E) - Side 3A.cdt", "G/Game, Set & Match 2 (E) - Side 3B.cdt", "G/Game, Set & Match 2 (E) - Side 4A.cdt", "G/Game, Set & Match 2 (E) - Side 4B.cdt"]
    """
    rv = [i_filePath]

    stem, extension = os.path.splitext(i_filePath)

    # If the name ends with a number and letter pair
    import re
    match = re.search("[0-9]+[A-Z]$", stem)
    if match:
        numberlessStem = stem[ : -len(match.group(0))]
        number = int(match.group(0)[:-1])
        startLetter = match.group(0)[-1]
        letter = chr(ord(startLetter) + 1)
        while True:
            while True:
                possibleFilePath = numberlessStem + str(number) + letter + extension
                if not os.path.isfile(i_baseDirPath + "/" + possibleFilePath):
                    break
                rv.append(possibleFilePath)

                letter = chr(ord(letter) + 1)

            if letter == startLetter:
                break
            number += 1
            letter = startLetter

        return rv

    # Else if the name ends with a number
    match = re.search("[0-9]+$", stem)
    if match:
        numberlessStem = stem[ : -len(match.group(0))]
        number = int(match.group(0))
        while True:
            number += 1
            possibleFilePath = numberlessStem + str(number) + extension
            if not os.path.isfile(i_baseDirPath + "/" + possibleFilePath):
                break
            rv.append(possibleFilePath)
        return rv

    # Else if the name ends with a letter
    match = re.search("[A-Z]$", stem)
    if match:
        letterlessStem = stem[ : -1]
        letter = stem[-1]
        while True:
            letter = chr(ord(letter) + 1)
            possibleFilePath = letterlessStem + letter + extension
            if not os.path.isfile(i_baseDirPath + "/" + possibleFilePath):
                break
            rv.append(possibleFilePath)
        return rv

    return rv

def findFileInPaths(i_baseDirPaths, i_fileRelativePath):
    """
    Find the first occurrence of a file that exists relative to a selection of base directories.

    Params:
     i_baseDirPaths:
      (list of str)
      eg.
       ["/home/daniel/gamebases/Memotech MTX/Rom", "/home/daniel/gamebases/Memotech MTX/mfloppy", "/home/daniel/gamebases/Memotech MTX/tapes"]
     i_fileRelativePath:
      (str)
      Path to look for within the base dir paths
      eg.
       "club004.mfloppy"
       "Acornsoft/Elite.ssd"

    Returns:
     Either (str)
      Full path of a file that exists
     or (None)
      The file was not found in any of the base dirs.
    """
    for baseDirPath in i_baseDirPaths:
        possiblePath = os.path.join(baseDirPath, i_fileRelativePath)
        if os.path.exists(possiblePath):
            return possiblePath
    return None

# + }}}

# + Filesystem {{{

def createTree(i_pathOnDiskOfLeafDir):
    """
    Create a folder if it doesn't already exist,
    including all its parent directories.

    Params:
     i_pathOnDiskOfLeafDir:
      (str)
    """
    # Allow either forward or back-slashes
    i_pathOnDiskOfLeafDir = i_pathOnDiskOfLeafDir.replace("/", os.sep)

    partialPath = ""
    for part in i_pathOnDiskOfLeafDir.split(os.sep):
        partialPath += part + os.sep
        if not os.path.isdir(partialPath):
            os.mkdir(partialPath)

# + }}}

# + Zip files {{{

def extractZip(i_zipFilePath, i_destDirPath, i_membersToExtract=None):
    """
    Params:
     i_zipFilePath:
      (str)
      Path of ZIP file.
     i_destDirPath:
      (str)
      Folder to unzip to.
     i_membersToExtract:
      Either (list of str)
       Specific zip members to extract
      or (None)
       Extract all zip members.

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
    archive.extractall(i_destDirPath, members=i_membersToExtract)

    # Get absolute paths of files (exclude directories)
    if i_membersToExtract == None:
        filePaths = [path  for path in archive.namelist()  if not path.endswith("/")]
    else:
        filePaths = []
        for path in archive.namelist():
            if not path.endswith("/"):
                for memberToExtract in i_membersToExtract:
                    if path.startswith(memberToExtract):
                        filePaths.append(path)
                        break

    #
    return filePaths

# + }}}

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

# + + A whole command {{{

def commandListToStringForBash(i_executableAndArguments):
    """
    Convert an executable name and arguments in list form
    to a single string for execution by Bash
    (the individual list elements quoted as necessary).

    Params:
     i_executableAndArguments:
      (list of str)

    Returns:
     (str)
    """
    return " ".join([quoteArgumentForBash(arg)  for arg in flattenList(i_executableAndArguments)])

def commandListToStringForWindowsCmd(i_executableAndArguments):
    """
    Convert an executable name and arguments in list form
    to a single string for execution by Windows cmd.exe
    (the individual list elements quoted as necessary).

    Params:
     i_executableAndArguments:
      (list of str)

    Returns:
     (str)
    """
    return " ".join([quoteArgumentForWindowsCmd(arg)  for arg in flattenList(i_executableAndArguments)])

import platform
if platform.system() == "Windows":
    commandListToStringForNativeShell = commandListToStringForWindowsCmd
else:
    commandListToStringForNativeShell = commandListToStringForBash

# + + }}}

# + }}}

# + Running subprocesses {{{

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
            i_executableAndArguments = commandListToStringForNativeShell(i_executableAndArguments)

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

    # + Get value {{{

    def get(self, i_keyName, i_caseSensitive = False):
        """
        Get the value of a Gemus field ("key=value" pair).

        Params:
         i_keyName:
          (str)
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key.
          or unspecified
           Use default of False.

        Returns:
         Either (str)
          The value of the field.
         or (None)
          A Gemus field does not exist with the given key name.
        """
        # If don't care about case, normalize i_keyName
        normalizedInputPropertyName = i_keyName
        if not i_caseSensitive:
            normalizedInputPropertyName = normalizedInputPropertyName.upper()

        # For each Gemus property
        for propertyName in self.properties.keys():
            # If don't care about case, normalize the Gemus property name
            normalizedPropertyName = propertyName
            if not i_caseSensitive:
                normalizedPropertyName = normalizedPropertyName.upper()

            # If they match, return the value
            if normalizedPropertyName == normalizedInputPropertyName:
                return self.properties[propertyName]

        return None

    # + }}}

    # + Comparisons {{{

    def fieldIs(self, i_keyName, i_value, i_caseSensitive = False):
        """
        Test whether a Gemus field exists and its value entirely matches some string.

        Similar to, in GEMUS
         <name> = <value>
         <name> CONTAINS(<value>)
         <name> CONTAINS(<value>||<value>||<value>)

        Params:
         i_keyName:
          (str)
         i_value:
          Either (str)
           String to match with.
          or (list)
           Multiple strings to match with.
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key
            and the case of i_value must match with the case of the Gemus value.
          or unspecified
           Use default of False.

        Returns:
         (bool)
         True:
          The Gemus field exists
          and its value entirely matches at least one of the given strings.
        """
        # If passed a list (not a str),
        # recurse for all strings
        if not isinstance(i_value, str):
            return any(self.fieldIs(i_keyName, value, i_caseSensitive)  for value in i_value)
        # Else if passed a str
        else:
            # Get Gemus field value
            # and if it doesn't exist, return False
            gemusValue = self.get(i_keyName, i_caseSensitive)
            if gemusValue == None:
                return False

            # If don't care about case, normalize the values
            if not i_caseSensitive:
                i_value = i_value.upper()
                gemusValue = gemusValue.upper()

            # Test for complete match
            return gemusValue == i_value

    def fieldContains(self, i_keyName, i_value, i_caseSensitive = False):
        """
        Test whether a Gemus field exists and its value contains a substring.

        Similar to, in GEMUS
         Key_<name> CONTAINS(*<value>*)
         Key_<name> CONTAINS(*<value>*||*<value>*||*<value>*)

        Params:
         i_keyName:
          (str)
         i_value:
          Either (str)
           Subtring to look for.
          or (list)
           Multiple subtrings to look for.
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key
            and the case of i_value must match with the case of the Gemus value.
          or unspecified
           Use default of False.

        Returns:
         (bool)
         True:
          The Gemus field exists
          and its value contains at least one of the given substrings.
        """
        # If passed a list (not a str),
        # recurse for all strings
        if not isinstance(i_value, str):
            return any(self.fieldContains(i_keyName, value, i_caseSensitive)  for value in i_value)
        # Else if passed a str
        else:
            # Get Gemus field value
            # and if it doesn't exist, return False
            gemusValue = self.get(i_keyName, i_caseSensitive)
            if gemusValue == None:
                return False

            # If don't care about case, normalize the values
            if not i_caseSensitive:
                i_value = i_value.upper()
                gemusValue = gemusValue.upper()

            # Test for substring match
            return gemusValue.find(i_value) != -1

    def fieldStartsWith(self, i_keyName, i_value, i_caseSensitive = False):
        """
        Test whether a Gemus field exists and its value starts with one or more strings.

        Similar to, in GEMUS
         Key_<name> CONTAINS(<value>*)
         Key_<name> CONTAINS(<value>*||<value>*||<value>*)

        Params:
         i_keyName:
          (str)
         i_value:
          Either (str)
           Prefix to look for.
          or (list)
           Multiple prefixes to look for.
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key
            and the case of i_value must match with the case of the Gemus value.
          or unspecified
           Use default of False.

        Returns:
         (bool)
         True:
          The Gemus field exists
          and its value starts with at least one of the given prefixes.
        """
        # If passed a list (not a str),
        # recurse for all strings
        if not isinstance(i_value, str):
            return all(self.fieldStartsWith(i_keyName, value, i_caseSensitive)  for value in i_value)
        # Else if passed a str
        else:
            # Get Gemus field value
            # and if it doesn't exist, return False
            gemusValue = self.get(i_keyName, i_caseSensitive)
            if gemusValue == None:
                return False

            # If don't care about case, normalize the values
            if not i_caseSensitive:
                i_value = i_value.upper()
                gemusValue = gemusValue.upper()

            # Test for starting with
            return gemusValue.startswith(i_value)

    def fieldEndsWith(self, i_keyName, i_value, i_caseSensitive = False):
        """
        Test whether a Gemus field exists and its value ends with one or more strings.

        Similar to, in GEMUS
         Key_<name> CONTAINS(*<value>)
         Key_<name> CONTAINS(*<value>||*<value>||*<value>)

        Params:
         i_keyName:
          (str)
         i_value:
          Either (str)
           Suffix to look for.
          or (list)
           Multiple suffixes to look for.
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key
            and the case of i_value must match with the case of the Gemus value.
          or unspecified
           Use default of False.

        Returns:
         (bool)
         True:
          The Gemus field exists
          and its value ends with at least one of the given suffixes.
        """
        # If passed a list (not a str),
        # recurse for all strings
        if not isinstance(i_value, str):
            return all(self.fieldEndsWith(i_keyName, value, i_caseSensitive)  for value in i_value)
        # Else if passed a str
        else:
            # Get Gemus field value
            # and if it doesn't exist, return False
            gemusValue = self.get(i_keyName, i_caseSensitive)
            if gemusValue == None:
                return False

            # If don't care about case, normalize the values
            if not i_caseSensitive:
                i_value = i_value.upper()
                gemusValue = gemusValue.upper()

            # Test for ending with
            return gemusValue.endswith(i_value)

    def fieldNotEmpty(self, i_keyName, i_caseSensitive = False):
        """
        Test whether a Gemus field exists and its value is not empty.

        Similar to, in GEMUS
         Key_<name> CONTAINS(*)

        Params:
         i_keyName:
          (str)
         i_caseSensitive:
          Either (bool)
           True:
            The case of i_keyName must match with the case of the Gemus key.
          or unspecified
           Use default of False.

        Returns:
         (bool)
         True:
          The Gemus field exists and
          its value contains some characters other than whitespace.
        """
        # Get Gemus field value
        # and if it doesn't exist, return False
        gemusValue = self.get(i_keyName, i_caseSensitive)
        if gemusValue == None:
            return False

        # Strip whitespace, then test whether empty
        return gemusValue.strip() != ""


    # Deprecated, use fieldIs()
    def fieldIsOneOf(self, i_keyName, i_values):
        """
        Params:
         i_keyName:
          (str)
         i_values:
          (list of str)

        Returns:
         (bool)
        """
        for value in i_values:
            if self.fieldIs(i_keyName, value):
                return True
        return False

    # + }}}

# + }}}

# + Config files {{{

def setIniValue(i_filePath, i_sectionName, i_keyName, i_value,
                i_keyValueDelimiter = "=", i_sectionNameCaseSensitive = True, i_keyNameCaseSensitive = False):
    """
    Set a key=value pair in a Windows .INI-style file.

    Similar to, in GEMUS
     Set_INI_Value()

    Params:
     i_filePath:
      (str)
      Path of file to work in.
     i_sectionName:
      (str)
      Name of INI file section to work in.
      If the section doesn't exist in the file, it will be created.
     i_keyName:
      (str)
      Name of key in key=value pair.
      If a line with this key already exists in the file, that line will be changed,
      else a new line will be added.
     i_value:
      (str)
      Value of key=value pair.
     i_keyValueDelimiter:
      (str)
      String that seperates a key and a value.
     i_sectionNameCaseSensitive:
      (bool)
     i_keyNameCaseSensitive:
      (bool)
    """
    # Read lines of file
    with open(i_filePath, "r") as handle:
        lines = handle.readlines()


    def getKeyAndValue(i_line):
        keyAndValue = i_line.split(i_keyValueDelimiter, 1)
        if len(keyAndValue) < 2:
            return None, None
        return keyAndValue[0].strip(), keyAndValue[1].strip()

    # Find target section
    lineNo = 0
    while lineNo < len(lines):
        line = lines[lineNo]

        strippedLine = line.strip()
        if strippedLine.startswith("[") and strippedLine.endswith("]"):
            sectionName = strippedLine[1:-1]
            if (i_sectionNameCaseSensitive and sectionName == i_sectionName) or (not i_sectionNameCaseSensitive and sectionName.upper() == i_sectionName.upper()):
                break

        lineNo += 1
    # If didn't 'break', ie. didn't find the target section
    # add a new section
    else:
        lines.append("\n")
        lineNo += 1
        lines.append("[" + i_sectionName + "]\n")

    # For each line in target section
    lineNo += 1
    updated = False
    while lineNo < len(lines):
        line = lines[lineNo]

        # If found another section,
        # break
        strippedLine = line.strip()
        if strippedLine.startswith("[") and strippedLine.endswith("]"):
            break

        # If found the right key,
        # replace the value and break
        keyName, value = getKeyAndValue(strippedLine)
        if keyName != None and ((i_keyNameCaseSensitive and keyName == i_keyName) or \
                                (not i_keyNameCaseSensitive and keyName.upper() == i_keyName.upper())):
            lines[lineNo] = i_keyName + i_keyValueDelimiter + i_value + "\n"
            updated = True
            break

        lineNo += 1

    # If section or file ended without finding existing value to change,
    # rewind back over any blank lines, and insert a new key=value
    if not updated:
        lineNo -= 1
        while lines[lineNo].strip() == "":
            lineNo -= 1
        lines.insert(lineNo + 1, i_keyName + i_keyValueDelimiter + i_value + "\n")


    # Write file back
    with open(i_filePath, "w") as handle:
        handle.writelines(lines)

def setCfgValue(i_filePath, i_keyName, i_value,
                i_keyValueDelimiter = "=", i_keyNameCaseSensitive = False):
    """
    Set a key=value pair in a file which simply has one of them per line (almost a Windows .INI-style file, but without sections).

    Similar to, in GEMUS
     Set_CFG_Item()
     Set_CFG_Value()

    Params:
     i_filePath:
      (str)
      Path of file to work in.
     i_keyName:
      (str)
      Name of key in key=value pair.
      If a line with this key already exists in the file, that line will be changed,
      else a new line will be added.
     i_value:
      (str)
      Value of key=value pair.
     i_keyValueDelimiter:
      (str)
      String that seperates a key and a value.
     i_keyNameCaseSensitive:
      (bool)
    """
    # Read lines of file
    with open(i_filePath, "r") as handle:
        lines = handle.readlines()


    def getKeyAndValue(i_line):
        keyAndValue = i_line.split(i_keyValueDelimiter, 1)
        if len(keyAndValue) < 2:
            return None, None
        return keyAndValue[0].strip(), keyAndValue[1].strip()

    # For each line
    lineNo = 0
    while lineNo < len(lines):
        line = lines[lineNo]

        # If found the right key,
        # replace the value and break
        keyName, value = getKeyAndValue(line)
        if keyName != None and ((i_keyNameCaseSensitive and keyName == i_keyName) or \
                                (not i_keyNameCaseSensitive and keyName.upper() == i_keyName.upper())):
            lines[lineNo] = i_keyName + i_keyValueDelimiter + i_value + "\n"
            break

        lineNo += 1
    # If didn't 'break', ie. didn't find the target key
    # rewind back over any blank lines, and insert a new key=value
    else:
        lineNo -= 1
        while lines[lineNo].strip() == "":
            lineNo -= 1
        lines.insert(lineNo + 1, i_keyName + i_keyValueDelimiter + i_value + "\n")


    # Write file back
    with open(i_filePath, "w") as handle:
        handle.writelines(lines)

# + }}}

# + MAME {{{

def getMameMediaSlots(i_mameExecutable, i_machineName):
    """
    Params:
     i_mameExecutable:
      (str)
     i_machineName:
      (str)

    Returns:
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
    """
    # Get list of MAME media slots for the given machine
    exitCode, output = shellRunProcess([i_mameExecutable, i_machineName, "-listmedia"])

    # Example output:
    #SYSTEM           MEDIA NAME       (brief)    IMAGE FILE EXTENSIONS SUPPORTED
    #---------------- --------------------------- -------------------------------
    #a600             floppydisk       (flop)     .mfi  .dfi  .hfe  .mfm  .td0  .imd  .d77  .d88  .1dd  .cqm  .cqi  .dsk  .adf  .ipf  
    #a600             printout         (prin)     .prn
    #a600             harddisk         (hard)     .chd  .hd   .hdv  .2mg  .hdi
    #

    # Split to lines and drop 2 lines of header and 1 blank line footer
    outputLine = output.decode("utf-8").split("\n")[2:-1]
    availableDevices = []
    for line in outputLine:
        #print(line)
        system, mediaName, brief, extensions = line.split(None, 3)
        availableDevices.append([mediaName, extensions.split()])
    return availableDevices

def allocateGameFilesToMameMediaSlots(i_gameFilePaths, io_availableDevices):
    """
    Params:
     i_gameFilePaths:
      (list of str)
     io_availableDevices:
      (list)
      Same as returned from getMameMediaSlots().

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
    Popup a menu at the mouse pointer with a selection of text items.

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

# + Message box {{{

def messageBox(i_text, i_title="Message from adapter", i_icon="information"):
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
    import frontend
    frontend.messageBox(i_text, i_title, i_icon)

# + }}}

# + Simulating key presses {{{

import time

def typeOnKeyboard(i_thingsToType):
    """
    Dependencies:
     The 'pyautogui' module must be installed to use this function.

    Params:
     i_thingsToType:
      Either (str)
       Things to type.
       The string may contain any of the following substrings, concatenated together:
        Single-character strings
         the space character
         \t \n \r
         ! " # $ % & ' ( ) * + , - . /
         0 1 2 3 4 5 6 7 8 9
         : ; < = > ? @ [ \\ ] ^ _ `
         a b c d e f g h i j k l m n o p q r s t u v w x y z
         A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
         { | } ~
        Multiple-character strings (which each must be enclosed in curly braces, eg. "{tab}{space}")
         Common keys
          space tab backspace return
         Modifier keys
          shift shiftleft shiftright
          ctrl ctrlleft ctrlright
          alt altleft altright
          option optionleft optionright
          win winleft winright
         Lock keys
          capslock numlock scrolllock
         Escape and function keys
          esc escape
          f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 f13 f14 f15 f16 f17 f18 f19 f20 f21 f22 f23 f24
         Navigation block keys
          insert delete del home end pagedown pgdn pageup pgup
         Cursor keys
          up down left right
         Numeric keypad
          num0 num1 num2 num3 num4 num5 num6 num7 num8 num9
          add subtract divide multiply decimal
          enter
         Multimedia and system keys
          apps browserback browserfavorites browserforward browserhome browserrefresh browsersearch browserstop
          launchapp1 launchapp2 launchmail launchmediaselect
          playpause stop nexttrack prevtrack
          volumedown volumemute volumeup
          sleep
          print printscreen prntscrn prtsc prtscr pause
         Language entry keys
          kana kanji hanguel hangul hanja junja
         Other keys
          accept clear convert execute final fn help modechange nonconvert select separator yen command
       Any key specified as above will be pressed and released before moving onto the next key. This including the modifiers, like {shift}.
       But any key may also be written (in braces, since it will become multiple characters if not already) with a suffix for additional behaviour:
        down
         Press and hold the key down.
         eg.
          {shift down}abc
           Will type 'ABC' (if caps lock is off).
         You will normally want to follow this at some point with an 'up' as described next.
        up
         Release the key.
         eg.
          {shift down}abc{shift up}def
           Will type 'ABCdef' (if caps lock is off).
        +
         Press and hold the key down only for the next non-suffixed key, then release it.
         eg,
          {shift+}abc
           Will type 'Abc' (if caps lock is off).
        Some more examples:
         {alt+}{f4}
          The shortcut for closing a window on Windows.
         {ctrl+}{alt+}{f2}
          The shortcut for switching to the second virtual console on Linux.
         {alt down}{tab}{tab}{tab}{alt up}
          Switch to the third-last application used using the 'Alt-Tab' switcher.
      or (list)
       Each element is:
        Either (str)
         Things to type, in the same format asa above.
        or (float)
         Set the between-key delay for subsequent characters to this many seconds.
         The initial setting is 0.02.
        or (dict)

    """
    try:
        import pyautogui
    except ImportError as e:
        import traceback
        import frontend
        frontend.messageBox("<b>You must install the Python library 'pyautogui' to use typeOnKeyboard().</b><br>\n<br>\n(" + "<br>\n".join(traceback.format_exception_only(e.__class__, e)).strip() + ")", "Error", "critical")
        return

    pyautogui.PAUSE = 0

    if isinstance(i_thingsToType, str):
        i_thingsToType = [i_thingsToType]

    keyDownDelay = 0.02
    betweenKeyDelay = 0.02

    singleKeyHolds = set()

    for thing in i_thingsToType:
        if isinstance(thing, float):
            betweenKeyDelay = thing;

        elif isinstance(thing, dict):
            pass

        elif isinstance(thing, str):
            # Split tokens
            #  Each is either a single character or something in braces
            tokens = []
            charNo = 0
            while charNo < len(thing):
                if thing[charNo] == "{":
                    charNo += 1
                    startCharNo = charNo
                    while charNo < len(thing):
                        if thing[charNo] == "}":
                            break
                        charNo += 1
                    tokens.append(thing[startCharNo:charNo])
                    charNo += 1
                else:
                    tokens.append(thing[charNo])
                    charNo += 1

            #
            for token in tokens:
                if len(token) > 1 and token.endswith(" down"):
                    keyName = token[:-5]
                    pyautogui.keyDown(keyName)
                elif len(token) > 1 and token.endswith(" up"):
                    keyName = token[:-3]
                    pyautogui.keyUp(keyName)
                elif len(token) > 1 and token.endswith("+"):
                    keyName = token[:-1]
                    singleKeyHolds.add(keyName)
                    pyautogui.keyDown(keyName)
                else:
                    keyName = token
                    pyautogui.keyDown(keyName)
                    time.sleep(keyDownDelay)
                    pyautogui.keyUp(keyName)
                    #
                    for singleKeyHold in singleKeyHolds:
                        pyautogui.keyUp(singleKeyHold)
                    singleKeyHolds.clear()

                time.sleep(betweenKeyDelay)

# + }}}
