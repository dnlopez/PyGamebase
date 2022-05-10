
# Python std
import os
import sys
import platform
import subprocess



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
      or (list of string)
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
    shellExecList(executableAndArgs)



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
      or (list of string)
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

# + Running {{{

# Python std
import shlex
if hasattr(shlex, "quote"):
    python_quote = shlex.quote  # since Python 3.3
else:
    import pipes
    python_quote = pipes.quote  # before Python 3.3

def shellExecList(i_executableAndArguments):
    """
    [like dan.process.shellStartList()]

    Start a program in a shell,
    specifying the executable name and arguments as a string.

    Params:
     i_executableAndArguments:
      (list of str)
      The first element is the executable name, and the remaining elements are the executable arguments.
      Any sublists are flattened to their elements before the above interpretation takes place.
      If a name or argument contains any special shell characters like spaces, quotes, backslashes or parentheses, those will be quoted before reaching the shell.

    Returns:
     (subprocess.Popen)
     The Popen object for the started process.
    """
    # Flatten sublists
    i_executableAndArguments = flattenList(i_executableAndArguments)

    # Quote arguments if necessary
    i_executableAndArguments = [python_quote(arg)  for arg in i_executableAndArguments]

    # Convert to string
    i_executableAndArguments = " ".join(i_executableAndArguments)

    # [Use "...String()" function]
    # Start program
    import subprocess
    popen = subprocess.Popen(i_executableAndArguments,
                             shell=True,
                             stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())

    # Return Popen object
    return popen

def directExecList(i_executableAndArguments):
    """
    [like dan.process.directStartList()]

    Start a program directly,
    specifying the executable name and arguments as a list.

    Params:
     i_executableAndArguments:
      (list of str)
      The first element is the executable name, and the remaining elements are the executable arguments.
      Any sublists are flattened to their elements before the above interpretation takes place.

    Returns:
     (subprocess.Popen)
     The Popen object for the started process.

    Platform specifics:
     On Unix, os.execvp()-like behavior is used to start the program, so the system PATH will be used.
     On Windows, CreateProcess() is used to start the program.
    """
    # Flatten sublists
    i_executableAndArguments = flattenList(i_executableAndArguments)

    # Start program
    import subprocess
    popen = subprocess.Popen(i_executableAndArguments,
                             shell=False,
                             stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())

    # Return Popen object
    return popen

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
          (list of string)

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
