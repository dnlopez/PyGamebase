
# Python std
import sys
import os.path


adapter = None
def importAdapter(i_adapterFilePath):
    """
    Params:
     i_adapterFilePath:
      (str)
    """
    # Add adapter's directory to sys.path
    i_adapterFilePath = os.path.abspath(i_adapterFilePath)
    sys.path.append(os.path.dirname(i_adapterFilePath))
    # Import the module
    import importlib
    global adapter
    adapter = importlib.import_module(os.path.splitext(os.path.basename(i_adapterFilePath))[0])


# + Screenshot file/URL resolving {{{

def normalizeDirPathFromAdapter(i_dirPath):
    """
    Strip trailing slash from a directory path, if present.

    Params:
     i_dirPath:
      (str)
      eg.
       "/mnt/gamebase/games/"

    Returns:
     (str)
     eg.
      "/mnt/gamebase/games"
    """
    if i_dirPath.endswith("/") or i_dirPath.endswith("\\"):
        i_dirPath = i_dirPath[:-1]
    return i_dirPath

def getScreenshotAbsolutePath(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    if not hasattr(adapter, "config_screenshotsBaseDirPath"):
        return None
    return normalizeDirPathFromAdapter(adapter.config_screenshotsBaseDirPath) + "/" + i_relativePath

def getScreenshotUrl(i_relativePath):
    """
    Params:
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    i_relativePath = i_relativePath.replace(" ", "%20")
    i_relativePath = i_relativePath.replace("#", "%23")
    screenshotAbsolutePath = getScreenshotAbsolutePath(i_relativePath)
    if screenshotAbsolutePath == None:
        return None
    return "file://" + getScreenshotAbsolutePath(i_relativePath)


def dbRow_getScreenshotRelativePath(i_row):
    """
    Get the path of a game's first screenshot picture.
    This comes from the 'ScrnshotFilename' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      The database didn't specify a screenshot file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.screenshotRelativePath)
        #i_row.
        screenshotRelativePath = i_row["Games.ScrnshotFilename"]
        if screenshotRelativePath != None:
            screenshotRelativePath = screenshotRelativePath.replace("\\", "/")

    # Return it from cache
    #return i_row.
    return screenshotRelativePath

def dbRow_getTitleshotRelativePath(i_row):
    """
    Get the path of a game's titleshot picture.
    This is alternative, equivalent terminology to the first screenshot.
    This comes from the 'ScrnshotFilename' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      The database didn't specify a titleshot file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.titleshotRelativePath)
        #i_row.
        titleshotRelativePath = dbRow_getScreenshotRelativePath(i_row);

    # Return it from cache
    #return i_row.
    return titleshotRelativePath;

def dbRow_getSupplementaryScreenshotPaths(i_row, i_simulateCount=None):
    """
    Params:
     i_row:
      (sqlite3.Row)
     i_simulateCount:
      Either (int)
      or (None)

    Returns:
     (list of str)
     Paths of images, relative to the 'Screenshots' folder.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#!i_row.supplementaryScreenshotPaths:
        supplementaryScreenshotPaths = []

        # Get titleshot relative path
        titleshotRelativePath = dbRow_getTitleshotRelativePath(i_row)
        if titleshotRelativePath != None:
            # Search disk for further image files similarly-named but with a numeric suffix
            screenshotStem, imageExtension = os.path.splitext(titleshotRelativePath)

            if i_simulateCount == None:
                screenshotNo = 1
                while True:
                    screenshotRelativePath = screenshotStem + "_" + str(screenshotNo) + imageExtension
                    screenshotAbsolutePath = getScreenshotAbsolutePath(screenshotRelativePath)
                    if screenshotAbsolutePath == None or not os.path.exists(screenshotAbsolutePath):
                        break

                    supplementaryScreenshotPaths.append(screenshotRelativePath)

                    screenshotNo += 1

                #i_row.supplementaryScreenshotPaths = supplementaryScreenshotPaths
            else:
                for screenshotNo in range(1, i_simulateCount + 1):
                    screenshotRelativePath = screenshotStem + "_" + str(screenshotNo) + imageExtension

                    supplementaryScreenshotPaths.append(screenshotRelativePath)

                return supplementaryScreenshotPaths;

    # Return it from cache
    #return i_row.
    return supplementaryScreenshotPaths

def dbRow_getPhotoRelativePath(i_row):
    """
    Get the path of a game's (musician) photo.
    This comes from the 'Photo' database field.

    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Path of image, relative to the 'Photos' folder.
     or (None)
      The database didn't specify a photo file path.
    """
    # If there's not already a cached value,
    # compute and cache it now
    if True:#(!i_row.photoRelativePath)
        #i_row.
        photoRelativePath = i_row["Musicians.Photo"]
        if photoRelativePath != None:
            photoRelativePath = photoRelativePath.replace("\\", "/")

    # Return it from cache
    #return i_row.
    return photoRelativePath

def dbRow_getNumberedScreenshotFullPath(i_row, i_picNo):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

     i_picNo:
      (int)
      0: first picture

    Returns:
     Either (str)
      Absolute (resolved via the adapter's 'config_screenshotsBaseDirPath') path of image.
     or (None)
      There is no screenshot at this numeric position.
    """
    screenshotPath = None
    if i_picNo == 0:
        screenshotPath = dbRow_getScreenshotRelativePath(i_row)
    else:
        screenshotPaths = dbRow_getSupplementaryScreenshotPaths(i_row)
        if i_picNo-1 < len(screenshotPaths):
            screenshotPath = screenshotPaths[i_picNo-1]
    if screenshotPath == None:
        return None

    if not hasattr(adapter, "config_screenshotsBaseDirPath"):
        return None

    return normalizeDirPathFromAdapter(adapter.config_screenshotsBaseDirPath) + "/" + screenshotPath

def dbRow_getPhotoFullPath(i_row):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     Either (str)
      Absolute (resolved via the adapter's 'config_photosBaseDirPath') path of image.
     or (None)
      There is no photo.
    """
    photoPath = dbRow_getPhotoRelativePath(i_row)
    if photoPath == None:
        return None

    if not hasattr(adapter, "config_photosBaseDirPath"):
        return None

    return normalizeDirPathFromAdapter(adapter.config_photosBaseDirPath + "/" + photoPath)

# + }}}
