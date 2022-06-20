
# Python std
import sys
import sqlite3
import copy
import os.path
import re

# This program
import qt_extras
import columns
import sql


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

    try:
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

        # Note which table column specs can be realized from this database
        fulfillableColumnIds = set()
        def validateTableColumnSpec(i_dbSchema, i_dbTableNames, i_tableColumnSpec):
            rv = True
            if "dbTableNames" in i_tableColumnSpec:
                for dbTableName in i_tableColumnSpec["dbTableNames"]:
                    if not (dbTableName in i_dbTableNames):
                        rv = False
            if "dbColumnNames" in i_tableColumnSpec:
                for dbColumnName in i_tableColumnSpec["dbColumnNames"]:
                    tableName, columnName = dbColumnName.split(".")
                    if not (tableName in i_dbSchema.keys()):
                        rv = False
                    else:
                        columnNames = [row["name"]  for row in i_dbSchema[tableName]]
                        if not (columnName in columnNames):
                            rv = False
            if rv == False:
                print("Missing column: " + i_tableColumnSpec["id"])
            return rv
        for tableColumnSpec in columns.g_tableColumnSpecs:
            if validateTableColumnSpec(dbInfo["schema"], dbTableNames, tableColumnSpec):
                fulfillableColumnIds.add(tableColumnSpec["id"])
        dbInfo["fulfillableColumnIds"] = fulfillableColumnIds

        ## Only use the columns that the database actually has
        #columns.filterColumnsByDb(dbTableNames, dbInfo["schema"])

        #
        g_openDatabases[i_schemaName] = dbInfo

    except:
        g_db.execute("DETACH DATABASE " + i_schemaName)

def closeDb(i_schemaName):
    """
    Params:
     i_schemaName:
      (str)
    """
    cursor = g_db.execute("DETACH DATABASE " + i_schemaName)
    del(g_openDatabases[i_schemaName])


def tableColumnSpecToTableNamesAndSelectTerms(i_tableColumnSpec, i_schemaName):
    """
    Given a table column spec,
    get the (real or placeholder) SELECT and FROM (table name) terms to use in an SQL statement to get information for that column from a given database.

    Params:
     i_tableColumnSpec:
      (columns.TableColumnSpec)
     i_schemaName:
      (str)

    Returns:
     (tuple)
     Tuple has elements:
      0:
       (set)
       Table names
      1:
       (set)
       SQL SELECT terms
    """
    dbTableNames = set()
    dbSelectTerms = set()

    if i_tableColumnSpec["id"] in g_openDatabases[i_schemaName]["fulfillableColumnIds"]:
        if "dbTableNames" in i_tableColumnSpec:
            for dbTableName in i_tableColumnSpec["dbTableNames"]:
                dbTableNames.add(dbTableName)
        if "dbSelect" in i_tableColumnSpec:
            dbSelectTerms.add(i_tableColumnSpec["dbSelect"])
    else:
        if "dbSelectPlaceholder" in i_tableColumnSpec:
            dbSelectTerms.add(i_tableColumnSpec["dbSelectPlaceholder"])

    return (dbTableNames, dbSelectTerms)


# + Gamebase-specified schema {{{

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
        "fromTerm": "LEFT JOIN <schema name>.Years ON Games.YE_Id = Years.YE_Id"
    },
    "Genres": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Genres ON Games.GE_Id = Genres.GE_Id"
    },
    "PGenres": {
        "dependencies": ["Genres"],
        "fromTerm": "LEFT JOIN <schema name>.PGenres ON Genres.PG_Id = PGenres.PG_Id"
    },
    "Publishers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Publishers ON Games.PU_Id = Publishers.PU_Id"
    },
    "Developers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Developers ON Games.DE_Id = Developers.DE_Id"
    },
    "Programmers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Programmers ON Games.PR_Id = Programmers.PR_Id"
    },
    "Languages": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Languages ON Games.LA_Id = Languages.LA_Id"
    },
    "Crackers": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Crackers ON Games.CR_Id = Crackers.CR_Id"
    },
    "Artists": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Artists ON Games.AR_Id = Artists.AR_Id"
    },
    "Licenses": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Licenses ON Games.LI_Id = Licenses.LI_Id"
    },
    "Rarities": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Rarities ON Games.RA_Id = Rarities.RA_Id"
    },
    "Musicians": {
        "dependencies": [],
        "fromTerm": "LEFT JOIN <schema name>.Musicians ON Games.MU_Id = Musicians.MU_Id"
    },
}

# + }}}

# + Run queries {{{

def getGameList_getSql(i_tableColumnSpecIds, i_whereExpression, i_sortOperations, i_whereExpressionMightUseNonVisibleColumns=True):
    """
    Params:
     i_tableColumnSpecIds:
      (list of str)
     i_whereExpression:
      (str)
     i_sortOperations:
      (list)
      See ColumnNameBar.sort_operations
     i_whereExpressionMightUseNonVisibleColumns:
      (bool)

    Returns:
     Either (str)
     or raise exception (SqlParseError)
      args[0]:
       (str)
       Description of error.
    """
    sqlTexts = []

    for schemaName in list(g_openDatabases.keys()):
        # Start with fields that are always selected
        selectTerms = [
            "'" + schemaName + "' AS \"SchemaName\"",
            "Games.GA_Id AS [Games.GA_Id]"
        ]

        fromTerms = [
            schemaName + ".Games"
        ]

        # Determine what extra fields to select
        neededTableNames = set()
        neededSelectTerms = set()

        #  For all visible table columns,
        #  collect FROM and SELECT terms
        for tableColumnSpecId in i_tableColumnSpecIds:
            tableColumnSpec = columns.tableColumnSpec_getById(tableColumnSpecId)
            newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
            neededTableNames |= newNeededTableNames
            neededSelectTerms |= newNeededSelectTerms

        #  If needed, parse WHERE expression for column names and add those too
        if i_whereExpressionMightUseNonVisibleColumns:
            #columnIdentifiers = sql.sqlWhereExpressionToColumnIdentifiers(i_whereExpression)
            #for columnIdentifier in columnIdentifiers:
            #    tableColumnSpec = columns.tableColumnSpec_getByDbIdentifier(columnIdentifier)
            #    newNeededTableNames, newNeededSelectTerms = tableColumnSpecToTableNamesAndSelectTerms(tableColumnSpec, schemaName)
            #    neededTableNames |= newNeededTableNames
            #    neededSelectTerms |= newNeededSelectTerms
            try:
                normalizedWhereExpression, newNeededTableNames, newNeededSelectTerms = sql.normalizeSqlWhereExpressionToTableNamesAndSelectTerms(i_whereExpression, schemaName)
                if normalizedWhereExpression != None:
                    i_whereExpression = normalizedWhereExpression
                    neededTableNames |= newNeededTableNames
                    neededSelectTerms |= newNeededSelectTerms
            except sql.SqlParseError as e:
                raise

        # Add the extra fromTerms
        tableConnections = copy.deepcopy(connectionsFromGamesTable)
        for neededTableName in neededTableNames:
            fromTerms += [fromTerm.replace("<schema name>", schemaName)  for fromTerm in getJoinTermsToTable(neededTableName, tableConnections)]

        # Add the extra selectTerms
        for neededSelectTerm in neededSelectTerms:
            if neededSelectTerm == "Games.GA_Id" or neededSelectTerm == "GA_Id":  # TODO use a set for this too
                continue
            selectTerms.append(neededSelectTerm)

        #
        # SELECT and FROM
        sqlTexts.append("SELECT " + ", ".join(selectTerms) + "\nFROM " + " ".join(fromTerms))

    #print(sqlTexts)

    # WHERE
    i_whereExpression = i_whereExpression.strip()
    if i_whereExpression != "":
        sqlTexts = [sqlText + "\nWHERE " + i_whereExpression  for sqlText in sqlTexts]
        #sqlText += "\nWHERE " + i_whereExpression

    sqlText = "\nUNION ALL\n".join(sqlTexts)

    # ORDER BY
    if len(i_sortOperations) > 0:
        sqlText += "\nORDER BY "

        orderByTerms = []
        for columnId, direction in i_sortOperations:
            tableColumnSpec = columns.tableColumnSpec_getById(columnId)
            term = '"' + tableColumnSpec["dbIdentifiers"][0] + '"'
            if direction == -1:
                term += " DESC"
            orderByTerms.append(term)
        sqlText += ", ".join(orderByTerms)

    #
    return sqlText

def getGameList_executeSql(i_sqlText):
    """
    Params:
     i_sqlText:
      (str)

    Returns:
     (sqlite3.Cursor)
    """
    return g_db.execute(i_sqlText)

def getGameRecord(i_schemaName, i_gameId, i_includeRelatedGameNames=False):
    """
    Params:
     i_schemaName:
      (str)
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
        i_schemaName + ".Games"
    ]

    selectTerms = [
        "'" + i_schemaName + "' AS \"SchemaName\""
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
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS CloneOf_Games ON Games.CloneOf = CloneOf_Games.GA_Id")
            selectTerms.append("CloneOf_Games.Name AS [Games.CloneOf_Name]")
        if "Prequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Prequel_Games ON Games.Prequel = Prequel_Games.GA_Id")
            selectTerms.append("Prequel_Games.Name AS [Games.Prequel_Name]")
        if "Sequel" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Sequel_Games ON Games.Sequel = Sequel_Games.GA_Id")
            selectTerms.append("Sequel_Games.Name AS [Games.Sequel_Name]")
        if "Related" in gamesColumnNames:
            fromTerms.append("LEFT JOIN " + i_schemaName + ".Games AS Related_Games ON Games.Related = Related_Games.GA_Id")
            selectTerms.append("Related_Games.Name AS [Games.Related_Name]")

    # For all other tables connected to Games
    # that are present in this database
    tableConnections = copy.deepcopy(connectionsFromGamesTable)
    tableNames = [tableName  for tableName in tableConnections.keys()  if tableName in dbInfo["schema"].keys()]
    for tableName in tableNames:
        # Join to it
        fromTerms += [fromTerm.replace("<schema name>", i_schemaName)  for fromTerm in getJoinTermsToTable(tableName, tableConnections)]
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
    #print(sql)
    cursor = g_db.execute(sql)

    row = cursor.fetchone()
    row = sqliteRowToDict(row)
    return row

def getExtrasRecords(i_schemaName, i_gameId):
    """
    Params:
     i_schemaName:
      (str)
     i_gameId:
      (int)

    Returns:
     (dict)
    """
    # Build SQL string
    sql = "SELECT '" + i_schemaName + "' AS \"SchemaName\", * FROM " + i_schemaName + ".Extras"
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
