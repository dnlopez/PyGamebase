
# Python std
import sys
import sqlite3
import copy
import os.path
import re

# This program
import qt_extras
import columns


def sqliteRowToDict(i_row):
    """
    Convert a sqlite3.Row object to a plain dict for easier viewing.

    Params:
     i_row:
      (sqlite3.Row)

    Returns:
     (dict)
    """
    return { keyName: i_row[keyName]  for keyName in i_row.keys() }

# Open a temporary database
g_db = sqlite3.connect("")
# (sqlite3.Connection)

# Add REGEXP function
def functionRegex(i_pattern, i_value):
    #print("functionRegex(" + i_value + ", " + i_pattern + ")")
    #c_pattern = re.compile(r"\b" + i_pattern.lower() + r"\b")
    compiledPattern = re.compile(i_pattern)
    return compiledPattern.search(str(i_value)) is not None
g_db.create_function("REGEXP", 2, functionRegex)

g_openDatabases = {}
# (dict)
# Dictionary has:
#  Keys:
#   (str)
#   Schema name
#   ie. the alias specified in the ATTACH command
#  Values:
#   (dict)
#   Dictionary has specific key-value properties:
#    dbFilePath:
#     (str)
#    schema:
#     (dict)

def openDb(i_schemaName, i_dbFilePath):
    """
    Params:
     i_schemaName:
      (str)
     i_dbFilePath:
      (str)
    """
    if not os.path.isfile(i_dbFilePath):
        raise RuntimeError("file doesn't exist")

    dbInfo = {
        "dbFilePath": i_dbFilePath
    }

    # Attach database
    cursor = g_db.execute("ATTACH DATABASE '" + i_dbFilePath.replace("'", "''") + "' AS " + i_schemaName)

    # Get names of tables
    cursor = g_db.execute("SELECT name FROM " + i_schemaName + ".sqlite_master WHERE type = 'table'")
    rows = cursor.fetchall()
    dbTableNames = [row[0]  for row in rows]

    # Get info about tables
    dbInfo["schema"] = {}
    g_db.row_factory = sqlite3.Row
    for tableName in ["Games", "Years", "Genres", "PGenres", "Publishers", "Developers", "Programmers", "Languages", "Crackers", "Artists", "Licenses", "Rarities", "Musicians"]:
        if tableName in dbTableNames:
            cursor = g_db.execute("PRAGMA " + i_schemaName + ".table_info(" + tableName + ")")
            rows = cursor.fetchall()
            rows = [sqliteRowToDict(row)  for row in rows]
            dbInfo["schema"][tableName] = rows

    # Only use the columns that the database actually has
    columns.filterColumnsByDb(dbTableNames, dbInfo["schema"])

    #
    g_openDatabases[i_schemaName] = dbInfo

def closeDb(i_schemaName):
    """
    Params:
     i_schemaName:
      (str)
    """
    cursor = g_db.execute("DETACH DATABASE " + i_schemaName)
    del(g_openDatabases[i_schemaName])

def getJoinTermsToTable(i_tableName, io_tableConnections):
    """
    Params:
     i_tableName:
      (str)
     io_tableConnections:
      (dict)
      Mapping of table names to join clauses and dependencies
      eg.
       {
           "PGenres": {
               "dependencies": ["Genres"],
               "fromTerm": "LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id"
           },
           "Genres": {
               "dependencies": [],
               "fromTerm": "LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id"
           },
       }

    Returns:
     Function return value:
      (list of str)
     io_tableConnections:
      The used connections will be removed from the list.
    """
    rv = []

    if i_tableName in io_tableConnections:
        tableConnection = io_tableConnections[i_tableName]
        for dependency in tableConnection["dependencies"]:
            rv += getJoinTermsToTable(dependency, io_tableConnections)
        rv.append(tableConnection["fromTerm"])
        del(io_tableConnections[i_tableName])

    return rv

connectionsFromGamesTable = {
    "Years": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Years ON Games.YE_Id = Years.YE_Id"
    },
    "Genres": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Genres ON Games.GE_Id = Genres.GE_Id"
    },
    "PGenres": {
        "dependencies": ["Genres"],
        "fromTerm": "LEFT JOIN PGenres ON Genres.PG_Id = PGenres.PG_Id"
    },
    "Publishers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Publishers ON Games.PU_Id = Publishers.PU_Id"
    },
    "Developers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Developers ON Games.DE_Id = Developers.DE_Id"
    },
    "Programmers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Programmers ON Games.PR_Id = Programmers.PR_Id"
    },
    "Languages": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Languages ON Games.LA_Id = Languages.LA_Id"
    },
    "Crackers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Crackers ON Games.CR_Id = Crackers.CR_Id"
    },
    "Artists": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Artists ON Games.AR_Id = Artists.AR_Id"
    },
    "Licenses": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Licenses ON Games.LI_Id = Licenses.LI_Id"
    },
    "Rarities": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Rarities ON Games.RA_Id = Rarities.RA_Id"
    },
    "Musicians": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN Musicians ON Games.MU_Id = Musicians.MU_Id"
    },
}

# + Run queries {{{

def getGameList(i_sqlText):
    """
    Params:
     i_sqlText:
      (str)

    Returns:
     (sqlite3.Cursor)
    """
    return g_db.execute(i_sqlText)

def getGameRecord(i_gameId, i_includeRelatedGameNames=False):
    """
    Params:
     i_gameId:
      (int)
     i_includeRelatedGameNames:
      (bool)

    Returns:
     (dict)
    """
    dbInfo = g_openDatabases[list(g_openDatabases.keys())[0]]

    # From Games table, select all fields
    fromTerms = [
        "Games"
    ]

    selectTerms = [
    ]
    fullyQualifiedFieldNames = True
    if fullyQualifiedFieldNames:
        for field in dbInfo["schema"]["Games"]:
            selectTerms.append("Games." + field["name"] + " AS [Games." + field["name"] + "]")
    else:
        selectTerms.append("Games.*")

    #
    if i_includeRelatedGameNames:
        gamesColumnNames = [row["name"]  for row in dbInfo["schema"]["Games"]]
        if "CloneOf" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS CloneOf_Games ON Games.CloneOf = CloneOf_Games.GA_Id")
            selectTerms.append("CloneOf_Games.Name AS [Games.CloneOf_Name]")
        if "Prequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Prequel_Games ON Games.Prequel = Prequel_Games.GA_Id")
            selectTerms.append("Prequel_Games.Name AS [Games.Prequel_Name]")
        if "Sequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Sequel_Games ON Games.Sequel = Sequel_Games.GA_Id")
            selectTerms.append("Sequel_Games.Name AS [Games.Sequel_Name]")
        if "Related" in gamesColumnNames:
            fromTerms.append("LEFT JOIN Games AS Related_Games ON Games.Related = Related_Games.GA_Id")
            selectTerms.append("Related_Games.Name AS [Games.Related_Name]")

    # For all other tables connected to Games
    # that are present in this database
    tableConnections = copy.deepcopy(connectionsFromGamesTable)
    tableNames = [tableName  for tableName in tableConnections.keys()  if tableName in dbInfo["schema"].keys()]
    for tableName in tableNames:
        # Join to it
        fromTerms += getJoinTermsToTable(tableName, tableConnections)
        # Select all fields from it
        if fullyQualifiedFieldNames:
            for field in dbInfo["schema"][tableName]:
                selectTerms.append(tableName + "." + field["name"] + " AS [" + tableName + "." + field["name"] + "]")
        else:
            selectTerms.append(tableName + ".*")

    # Build SQL string
    #  SELECT
    sql = "SELECT " + ", ".join(selectTerms)
    #  FROM
    sql += "\nFROM " + " ".join(fromTerms)
    #  WHERE
    sql += "\nWHERE Games.GA_Id = " + str(i_gameId)

    # Execute
    g_db.row_factory = sqlite3.Row
    cursor = g_db.execute(sql)

    row = cursor.fetchone()
    row = sqliteRowToDict(row)
    return row

def getExtrasRecords(i_gameId):
    # Build SQL string
    sql = "SELECT * FROM Extras"
    sql += "\nWHERE GA_Id = " + str(i_gameId)
    sql += "\nORDER BY DisplayOrder"

    # Execute
    g_db.row_factory = sqlite3.Row
    cursor = g_db.execute(sql)

    rows = cursor.fetchall()
    rows = [sqliteRowToDict(row)  for row in rows]
    return rows

# + }}}

import collections
class DbRecordDict(collections.UserDict):
    """
    A dictionary intended to hold keys which are fully qualified '<table name>.<column name>' names,
    and overrides __getitem__ so that you can get items by either that full name or just '<column name>'.
    """
    def __getitem__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return self.data[i_key]

        # Try matching just the last name component
        for realKey, value in self.data.items():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return value

        # Raise KeyError
        return self.data[i_key]

    def __contains__(self, i_key):
        # Try matching the key name as given
        if i_key in self.data:
            return True

        # Try matching just the last name component
        for realKey in self.data.keys():
            if realKey.rsplit(".", 1)[-1] == i_key:
                return True

        #
        return False
