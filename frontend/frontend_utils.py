
# Python std
import sys
import os


def openInDefaultApplication(i_filePaths):
    """
    Params:
     i_filePaths:
      Either (str)
      or (list of str)
    """
    # Choose launcher command
    import platform
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

    # [shellExecList()]

    # Quote arguments if necessary
    import shlex
    executableAndArgs = [shlex.quote(arg)  for arg in executableAndArgs]

    # Convert to string
    executableAndArgs = " ".join(executableAndArgs)

    # [Use "...String()" function]
    # Start program
    import subprocess
    popen = subprocess.Popen(executableAndArgs,
                             shell=True,
                             stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())

def createTree(i_pathOnDiskOfLeafDir):
    """
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
