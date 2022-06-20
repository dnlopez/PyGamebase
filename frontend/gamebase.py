
# Python std
import sys
import os.path

# + Load {{{

adapters = {}
# (dict)
# Dict has arbitrary key-value properties:
#  Keys:
#   (str)
#   Unique ID string for loaded adapter.
#   (Currently happens to be the adapter module's absolute file path.)
#  Values:
#   (dict)
#   Dict has specific key-value properties:
#    module:
#     (module)
#     Imported adapter module
#    schemaName:
#     Either not yet set
#     or (str)

schemaAdapterIds = {}
# (dict)
# Shortcut reverse lookup table from schema name to adapter ID

def importAdapter(i_adapterFilePath):
    """
    Params:
     i_adapterFilePath:
      (str)

    Returns:
     (str)
     Unique ID string for loaded adapter.
    """
    # Add adapter's directory to sys.path
    i_adapterFilePath = os.path.abspath(i_adapterFilePath)
    sys.path.append(os.path.dirname(i_adapterFilePath))
    # Import the module
    import importlib
    adapterModule = importlib.import_module(os.path.splitext(os.path.basename(i_adapterFilePath))[0])
    adapters[i_adapterFilePath] = {
        "module": adapterModule
    }

    return i_adapterFilePath

def setAdapterSchemaName(i_adapterId, i_schemaName):
    """
    Params:
     i_adapterId:
      (str)
     i_schemaName:
      (str)
    """
    adapters[i_adapterId]["schemaName"] = i_schemaName
    schemaAdapterIds[i_schemaName] = i_adapterId

def forgetAdapter(i_adapterId):
    """
    Params:
     i_adapterId:
      (str)
    """
    # If we got as far as setting it there,
    # delete schema name from reverse lookup table
    if "schemaName" in adapters[i_adapterId]:
        schemaName = adapters[i_adapterId]
        if schemaName in schemaAdapterIds:
            del(schemaAdapterIds[schemaName])

    # Delete main adapter entry
    del(adapters[i_adapterId])

# + }}}

# + Screenshot/photo file/URL resolving {{{

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

# [was getScreenshotAbsolutePath()]
def screenshotPath_relativeToAbsolute(i_adapterId, i_relativePath):
    """
    Params:
     i_adapterId:
      (str)
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    if not hasattr(adapters[i_adapterId]["module"], "config_screenshotsBaseDirPath"):
        return None
    return normalizeDirPathFromAdapter(adapters[i_adapterId]["module"].config_screenshotsBaseDirPath) + "/" + i_relativePath

def photoPath_relativeToAbsolute(i_adapterId, i_relativePath):
    """
    Params:
     i_adapterId:
      (str)
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    if not hasattr(adapters[i_adapterId]["module"], "config_photosBaseDirPath"):
        return None
    return normalizeDirPathFromAdapter(adapters[i_adapterId]["module"].config_photosBaseDirPath) + "/" + i_relativePath

# [was getScreenshotUrl()]
def screenshotPath_relativeToUrl(i_adapterId, i_relativePath):
    """
    Params:
     i_adapterId:
      (str)
     i_relativePath:
      (str)

    Returns:
     Either (str)
     or (None)
    """
    i_relativePath = i_relativePath.replace(" ", "%20")
    i_relativePath = i_relativePath.replace("#", "%23")
    screenshotAbsolutePath = screenshotPath_relativeToAbsolute(i_adapterId, i_relativePath)
    if screenshotAbsolutePath == None:
        return None
    return "file://" + screenshotPath_relativeToAbsolute(i_adapterId, i_relativePath)

# + }}}

# + Get image paths {{{

# + + Screenshots {{{

# [was dbRow_getScreenshotRelativePath()
def dbRow_firstScreenshotRelativePath(i_row):
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

# [was dbRow_getSupplementaryScreenshotPaths()]
def dbRow_supplementaryScreenshotRelativePaths(i_row, i_simulateCount=None):
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
    schemaName = i_row["SchemaName"]
    adapterId = schemaAdapterIds[schemaName]

    # If there's not already a cached value,
    # compute and cache it now
    if True:#!i_row.supplementaryScreenshotPaths:
        supplementaryScreenshotPaths = []

        # Get titleshot relative path
        titleshotRelativePath = dbRow_firstScreenshotRelativePath(i_row)
        if titleshotRelativePath != None:
            # Search disk for further image files similarly-named but with a numeric suffix
            screenshotStem, imageExtension = os.path.splitext(titleshotRelativePath)

            if i_simulateCount == None:
                screenshotNo = 1
                while True:
                    screenshotRelativePath = screenshotStem + "_" + str(screenshotNo) + imageExtension
                    screenshotAbsolutePath = screenshotPath_relativeToAbsolute(adapterId, screenshotRelativePath)
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

def dbRow_allScreenshotRelativePaths(i_row):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     (list of str)
     Paths of images, relative to the 'Screenshots' folder.
    """
    rv = []

    firstScreenshotRelativePath = dbRow_firstScreenshotRelativePath(i_row)
    if firstScreenshotRelativePath != None:
        rv.append(firstScreenshotRelativePath)
        rv.extend(dbRow_supplementaryScreenshotRelativePaths(i_row))

    return rv

def dbRow_screenshotCount(i_row):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     (int)
    """
    return len(dbRow_supplementaryScreenshotRelativePaths(i_row)) + 1

def dbRow_nthScreenshotRelativePath(i_row, i_picNo):
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
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      There is no screenshot at this numeric position.
    """
    screenshotPath = None
    if i_picNo == 0:
        screenshotPath = dbRow_firstScreenshotRelativePath(i_row)
    else:
        screenshotPaths = dbRow_supplementaryScreenshotRelativePaths(i_row)
        if i_picNo-1 < len(screenshotPaths):
            screenshotPath = screenshotPaths[i_picNo-1]
    return screenshotPath

# [was dbRow_getNumberedScreenshotFullPath()]
def dbRow_nthScreenshotFullPath(i_row, i_picNo):
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
    path = dbRow_nthScreenshotRelativePath(i_row, i_picNo)
    if path != None:
        schemaName = i_row["SchemaName"]
        adapterId = schemaAdapterIds[schemaName]
        path = screenshotPath_relativeToAbsolute(adapterId, path)
    return path


import random
g_sessionRandomSeed = random.randint(0, 100)

def dbRow_allRandomScreenshotRelativePaths(i_row):
    """
    Params:
     i_row:
      (sqlite3.Row)
      A row from the 'Games' table

    Returns:
     (list of str)
     Paths of images, relative to the 'Screenshots' folder.
    """
    allRelativePaths = dbRow_allScreenshotRelativePaths(i_row)
    random.Random(i_row["Games.GA_Id"] + g_sessionRandomSeed).shuffle(allRelativePaths)
    return allRelativePaths

def dbRow_nthRandomScreenshotRelativePath(i_row, i_picNo):
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
      Path of image, relative to the 'Screenshots' folder.
     or (None)
      There is no screenshot at this numeric position.
    """
    allRelativePaths = dbRow_allRandomScreenshotRelativePaths(i_row)
    if i_picNo >= len(allRelativePaths):
        return None
    return allRelativePaths[i_picNo]

def dbRow_nthRandomScreenshotFullPath(i_row, i_picNo):
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
    path = dbRow_nthRandomScreenshotRelativePath(i_row, i_picNo)
    if path != None:
        schemaName = i_row["SchemaName"]
        adapterId = schemaAdapterIds[schemaName]
        path = screenshotPath_relativeToAbsolute(adapterId, path)
    return path

# + + }}}

# + + Photo {{{

# [was dbRow_getPhotoRelativePath()]
def dbRow_photoRelativePath(i_row):
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

# [was dbRow_getPhotoFullPath()]
def dbRow_photoFullPath(i_row):
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
    path = dbRow_photoRelativePath(i_row)
    if path != None:
        schemaName = i_row["SchemaName"]
        adapterId = schemaAdapterIds[schemaName]
        path = photoPath_relativeToAbsolute(adapterId, path)
    return path

# + + }}}

# + }}}
